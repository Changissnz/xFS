from morebs2.matrix_methods import *
from morebs2.search_space_iterator import * 
from morebs2.numerical_generator import modulo_in_range,safe_modulo_in_range,prg_seqsort,prg_seqsort_ties
from morebs2.point_sorter import rank_sequence
from .tree_gen import SimpleCounter
from types import MethodType,FunctionType
from copy import deepcopy 


"""
S := str, comma-separated integers, even non-zero number of integers;
    (agent idn i_j,idn i_j move)*

return:
- dict, agent idn -> move idn.  
"""
def string_to_agent_move_map(S): 
    q = string_to_vector(S) 
    assert len(q) > 0 and len(q) % 2 == 0
    d = dict()
    for i in range(0,len(q),2): 
        a,m = q[i],q[i+1]
        d[a] = m 
    return d 

def agent_move_map_to_string(amap):
    assert type(amap) in {dict,defaultdict} 
    if len(amap) == 0: return "" 

    keys = sorted(amap.keys()) 
    s = ""
    for k in keys: 
        s += "{},{},".format(int(k),int(amap[k])) 
    return s[:-1] 

def is_partial_agent_move_map_match(partial,whole): 
    for k,v in partial.items(): 
        if whole[k] == v: 
            continue 
        return False 
    return True 

def agent_move_map__partial_key_match(S,amap):
    key_matches = [] 

    for k in S.keys(): 
        whole = string_to_agent_move_map(k) 
        if is_partial_agent_move_map_match(amap,whole):
            key_matches.append(k) 
    return sorted(key_matches)

def multi_agent_action_map__zeros(agents,agent2movesize_map,move_idn_counter): 
    # assign move identifiers to each agent's moves 
    agents = sorted(agents) 
    agent2move_map = {} 
    for a in agents: 
        l = agent2movesize_map[a] 
        agent2move_map[a] = [move_idn_counter() for _ in range(l)] 

    q = [agent2movesize_map[a] for a in agents] 
    bounds = np.array([np.zeros(len(agents),),q]).T 
    start_point = bounds[:,0]
    column_order = [i for i in range(len(q))] 
    ssi_hop = np.array(q)
    ssi = SearchSpaceIterator(bounds,start_point,column_order,\
        ssi_hop,cycleOn = False,cycleIs = 0)

    T = {} 
    v = {a:0 for a in agents}
    while not ssi.finished(): 
        # get the index 
        n = next(ssi) 
        # get the dict 
        d = {agents[i]:agent2move_map[i][int(n_)] for (i,n_) in enumerate(n)} 

        # convert dict to string 
        s = agent_move_map_to_string(d) 

        # load element 
        T[s] = deepcopy(v) 
    
    return T,agent2move_map

def bracket_assignment_agent_action_payoff(T,agent_idn,agent_moveset,agent_action_value_range,\
    bracket_size_range,prg): 

    actions = sorted(agent_moveset) 
    num_brackets = modulo_in_range(int(prg()),bracket_size_range)
    ##print(agent_idn," num brackets: ",num_brackets)
    v = n_partition_for_range(agent_action_value_range,num_brackets)

    actions = prg_seqsort(actions,prg)
    action_brackets = [] 
    for i,a2 in enumerate(actions): 
        i2 = i % num_brackets 
        r2 = v[i2:i2+2]
        action_brackets.append(r2) 

    for (i,a) in enumerate(actions):
        amap = {agent_idn:a}
        keys = agent_move_map__partial_key_match(T,amap)
        r2 = action_brackets[i]
        for k in keys: 
            value = round(modulo_in_range(prg(),r2),5) 
            T[k][agent_idn] = value 
    return

"""
table for immediate effects of actions by agents
"""
class MultiAgentActionTable: 

    """
    agents := set, agent idns 
    agent_action_map := dict, 
        stringized repr. of (agent idn,move idn) -> agent idn -> value from move. 
    """
    def __init__(self,agents,agent_action_map): 
        self.agents = agents 
        self.agent_action_map = agent_action_map
        self.agent2move_map = None 
        self.check_arguments()
        return

    def __str__(self): 
        keys = sorted(self.agent_action_map.keys()) 
        S = "" 
        for k in keys: 
            S += self.stringize_action_profile(k) + "\n" + "-" * 50 + "\n" 
        return S 

    def __getitem__(self, key):
        if key in self.agent_action_map: 
            return self.agent_action_map[key]
        assert False 
    
    def stringize_action_profile(self,k): 
        m2 = string_to_agent_move_map(k)
        x = self.agent_action_map[k] 
        keys = sorted(m2.keys())

        s = ""
        for k2 in keys: 
            s += "agent {} move {} value {}\n".format(k2,m2[k2],x[k2])  
        return s 

    ################### preprocessing moves for info on `agent_action_map`
    def check_arguments(self):
        assert type(self.agents) == set 
        self.agent2move_map = self.agent_to_move_map() 
        assert len(self.agent_action_map) == self.total_number_of_move_combinations() 
        return

    def agent_to_move_map(self):
        d = defaultdict(set) 
        for k,v in self.agent_action_map.items(): 
            q = string_to_agent_move_map(k)
            for k2,v2 in q.items(): 
                d[k2] |= {v2}
            assert type(v) in {dict,defaultdict} 
            assert set(v.keys()) == self.agents 
        return d 

    def total_number_of_move_combinations(self):
        l = 1 
        for v in self.agent2move_map.values(): 
            l = l * len(v) 
        return l 

    ############################## used to determine lattice points of n-dimensional 
    ############################## game table prism. 

    """
    sort_index := 0 -> min,
                  1 -> max,
                  2 -> mean. 
    """
    def sort_agent_moves(self,a_idn,sort_index,other_agent_moves={}): 
        assert sort_index in {0,1,2}

        move_info = []
        for m in self.agent2move_map[a_idn]: 
            info = self.base_info_on_agent_move(a_idn,m,other_agent_moves)
            move_info.append((int(m),info))
        return sorted(move_info,key=lambda x:x[1][sort_index])

    """
    Determines the rank of agent `a_idn` conducting move `move_idn` 
    w.r.t. the others. For every element E in `agent_action_map` that 
    has agent `a_idn` conduct `move_idn`, ranks value of agent with the 
    costs of the other, producing rank r. 

    NOTE: ordering of rank is least=0, greatest=max. 

    return:
    - list, ranks of value for agent conducting move w.r.t. other agents.
    """
    def possible_ranks_of_agent_by_move(self,a_idn,move_idn,other_agent_moves={}): 
        self.query_parameter_assertion(a_idn,move_idn,other_agent_moves)

        amap = {a_idn:move_idn}
        amap.update(other_agent_moves)

        keys = agent_move_map__partial_key_match(self.agent_action_map,amap)
        ranks = []
        for k in keys: 
            v = self.agent_action_map[k] 
            v_ = [(k2,v2) for k2,v2 in v.items()]
            q = rank_sequence(v_,vf=lambda x:x[1],\
                element_output_function=lambda x:x[0],output_type=dict)
            r = q[a_idn]
            ranks.append(r) 
        return ranks 

    """
    return:
    - (min,max,mean) of agent move value 
    """
    def base_info_on_agent_move(self,a_idn,move_idn,other_agent_moves={}):
        self.query_parameter_assertion(a_idn,move_idn,other_agent_moves)

        amap = {a_idn:move_idn}
        amap.update(other_agent_moves)
        keys = agent_move_map__partial_key_match(self.agent_action_map,amap)
        assert len(keys) > 0 

        vs = []
        for k in keys:
            v = self.agent_action_map[k][a_idn]
            vs.append(v) 
        
        return np.min(vs),np.max(vs),np.round(np.mean(vs),5) 

    """
    calculates the move by agent `a_idn` that would yield the minumum mean value by agents in 
    set `other_idns`. If `other_agent_moves` is not empty, only those moves by the other agents 
    are considered in the ranking calculation.
    """
    def agent_move_for_minmean_value_by_other_agents(self,a_idn,other_idns,other_agent_moves={},\
        prg = None):
        
        other_info = self.agent_move_for_info_on_other_agents(a_idn,other_idns,other_agent_moves,2,2)
        other_info = [(k,v) for k,v in other_info.items()]

        if type(prg) != type(None):
            return int(prg_seqsort_ties(other_info,prg,vf=lambda x:x[1])[0][0])
        return int(sorted(other_info,key=lambda x:x[1])[0][0])

    def agent_move_for_info_on_other_agents(self,a_idn,other_idns,other_agent_moves={},index0=2,\
        index1=2):
        assert index0 in {0,1,2}
        assert index1 in {0,1,2}

        def fx(S):
            if index1 == 0:
                return np.min(S)
            elif index1 == 1:
                return np.max(S)
            else:
                return np.round(np.mean(S),5) 

        move_info = {}
        for m in self.agent2move_map[a_idn]:
            dx = self.base_info_on_other_agents(a_idn,m,other_idns,other_agent_moves)

            s = [v[index0] for v in dx.values()] 
            s = fx(s)
            move_info[m] = s 
        return move_info 

    def base_info_on_other_agents(self,a_idn,move_idn,other_idns,other_agent_moves={}): 
        self.query_parameter_assertion(a_idn,move_idn,other_agent_moves)
        assert other_idns.issubset(self.agents) and a_idn not in other_idns

        amap = {a_idn:move_idn}
        amap.update(other_agent_moves)
        keys = agent_move_map__partial_key_match(self.agent_action_map,amap)
        assert len(keys) > 0 

        vs = []
        other_agent_mean = defaultdict(float)
        other_agent_min = {o:float('inf') for o in other_idns}
        other_agent_max = {o:-float('inf') for o in other_idns}

        for k in keys:
            v = self.agent_action_map[k]
            for o in other_idns:
                v2 = v[o]
                other_agent_mean[o] += v2 
                other_agent_min[o] = min([v2,other_agent_min[o]])
                other_agent_max[o] = max([v2,other_agent_max[o]])
        for o in other_idns: 
            other_agent_mean[o] = round(other_agent_mean[o] / len(keys),5) 

        other_agent_info = {o:\
            (other_agent_min[o],other_agent_max[o],other_agent_mean[o]) \
            for o in other_idns}
        return other_agent_info

    def query_parameter_assertion(self,a_idn,move_idn,other_agent_moves):
        assert a_idn in self.agents
        assert move_idn in self.agent2move_map[a_idn]
        assert type(other_agent_moves) == dict 
        assert set(other_agent_moves.keys()).issubset(self.agents) 

    @staticmethod 
    def generate_instance__type_prng(agents,agent2movesize_map,agent_action_value_range,\
        prg,move_idn_counter=SimpleCounter(0).__next__): 
        agent_action_value_range = MultiAgentActionTable.generate_instance__parameter_assertion(\
            agents,agent2movesize_map,agent_action_value_range,prg)

        T,_ = multi_agent_action_map__zeros(agents,agent2movesize_map,move_idn_counter)
        agents_ = sorted(agents) 

        keys = sorted(T.keys())
        for k in keys:
            v = T[k] 
            for k2 in agents_: 
                v[k2] = round(safe_modulo_in_range(prg(),\
                    agent_action_value_range[k2]),5) 
        return MultiAgentActionTable(agents,T) 

    @staticmethod 
    def generate_instance__type_strict_percentile(agents,agent2movesize_map,agent_action_value_range,\
        prg,bracket_size_range,move_idn_counter=SimpleCounter(0).__next__):

        agent_action_value_range = MultiAgentActionTable.generate_instance__parameter_assertion(\
            agents,agent2movesize_map,agent_action_value_range,prg)

        T,M = multi_agent_action_map__zeros(agents,agent2movesize_map,move_idn_counter)
        agents = sorted(agents)
        for agent_idn in agents: 
            agent_moveset = M[agent_idn]
            aarange = agent_action_value_range[agent_idn]
            bracket_assignment_agent_action_payoff(T,agent_idn,agent_moveset,\
                aarange,bracket_size_range,prg)
        return MultiAgentActionTable(set(agents),T)

    @staticmethod 
    def generate_instance__parameter_assertion(agents,agent2movesize_map,agent_action_value_range,\
        prg):
        assert type(prg) in {FunctionType,MethodType}

        agent_action_value_range = MultiAgentActionTable.format_agent_action_value_range(\
            agents,agent_action_value_range)

        assert set(agent2movesize_map.keys()) == agents
        for v in agent2movesize_map.values(): assert v > 0 
        return agent_action_value_range

    @staticmethod 
    def format_agent_action_value_range(agents,agent_action_value_range): 

        if type(agent_action_value_range) == dict: 
            assert set(agent_action_value_range.keys()) == agents 
            for v in agent_action_value_range.values(): 
                assert v[0] <= v[1]     
        else: 
            assert agent_action_value_range[0] <= agent_action_value_range[1] 
            agents = sorted(agents) 
            d = {} 
            for k in agents: 
                d[k] = deepcopy(agent_action_value_range) 
            agent_action_value_range = d 
        return agent_action_value_range