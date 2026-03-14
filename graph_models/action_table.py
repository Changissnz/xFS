from morebs2.matrix_methods import *

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
        return -1 

    ################### preprocessing moves for info on `agent_action_map`
    def check_arguments(self):
        assert type(self.agents) == set 
        self.agent2move_map = self.agent_to_move_map() 
        assert len(self.agent_action_map) == self.total_number_of_move_combinations() 
        return

    def agent_to_move_map(self):
        d = defaultdict(set) 
        for k,v in self.agent_action_map.values(): 
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
            move_info.append((m,info))
        return sorted(move_info,key=lambda x:x[1][sort_index])

    """
    Determines the rank of agent `a_idn` conducting move `move_idn` 
    w.r.t. the others. For every element E in `agent_action_map` that 
    has agent `a_idn` conduct `move_idn`, ranks value of agent with the 
    costs of the other, producing rank r. 

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
        
        return np.min(vs),np.max(vs),np.mean(vs)

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
            return prg_seqsort_ties(other_info,prg,vf=lambda x:x[1])[0][0]
        return sorted(other_info,key=lambda x:x[1])[0][0]

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
                return np.mean(S)

        move_info = {}
        for m in self.agent2move_map[a_idn]:
            dx = self.base_info_on_other_agents(a_idn,m,other_idns,other_agent_moves)
            s = [v[index0] for v in dx.items()]
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
            other_agent_mean[o] /= len(keys)

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
    def generate_instance(): 
        return -1 

    @staticmethod 
    def generate_zero_instance():
        return -1 