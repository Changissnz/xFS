from graph_models.community import * 
from .usg_controller import * 
from types import FunctionType,MethodType
from morebs2.matrix_methods import is_valid_range,point_on_bounds_by_ratio_vector
from morebs2.numerical_generator import modulo_in_range,prg_decimal,prg_choose_n,prg__single_to_int
from morebs2.measures import zero_div 
from math import floor 

# used by <StrangleSubject> for guessing force to break strangleholds. 
DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION = 5 
DEFAULT_STRANGLESUBJECT_COMMUNITY_SIZE_RANGE = [20,100] 
DEFAULT_STRANGLER_HOLD_FREQUENCY_CONSUMPTION_MIN_THRESHOLD = 5 
DEFAULT_MAX_NUMBER_OF_STRANGLEFORM_ENTITIES = 50 

"""
Function used by strangle subject to break out of stranglehold. 

Breaking process goes as follows: 
- partition the nodes of `node_map` into two sets: 
    - positive : being strangled 
    - negative: not being strangled 
- for the total force F, set q = F / |node_map| * neg_weight / pos_weight; 
    neg_weight the cumulative node weights in the `node_weight_map` for 
    the negative nodeset, pos_weight likewise. 
* If pos_weight is 0, then set q equal to 0. 
- Apply -q to every positive node, and 0 to every negative node. This comprises 
  the map, 
      node -> breaking force applied to node. 
"""
def default_strangle_breaking_function(node_map,F,node_weight_map=None): 
    if len(node_map) == 0: return dict() 
    assert F <= 0. 
    if type(node_weight_map) == type(None): 
        node_weight_map = {k:1 for k in node_map.keys()} 
    else: 
        assert type(node_weight_map) == dict 

    q = F / len(node_map) 
    smap = {k:q for k in node_map.keys()} 
    
    # get nodes that are not being strangled.
    neg_set = {k for k,v in node_map.items() if v <= 0.}
    pos_set = {k for k in node_map.keys() if k not in neg_set} 

    neg_weight = sum([node_weight_map[n] for n in neg_set]) 
    pos_weight = sum([node_weight_map[n] for n in pos_set]) 

    q2 = q * neg_weight
    q2 = zero_div(q2,pos_weight,0)  

    for s in smap.keys(): 
        if s in pos_set: 
            smap[s] -= q2 
        else: 
            smap[s] = 0 
    return {k:round(v,5) for k,v in smap.items()}

def min_strangle_breaking_force(node_map,node_weight_map=None): 

    if type(node_weight_map) == type(None): 
        node_weight_map = {k:1 for k in node_map.keys()} 
    else: 
        assert type(node_weight_map) == dict 

    q = -max(node_map.values())
    assert q <= 0.0 

    neg_set = {k for k,v in node_map.items() if v <= 0.}
    pos_set = {k for k in node_map.keys() if k not in neg_set} 
    if len(pos_set) == 0: 
        return 0 

    neg_weight = sum([node_weight_map[n] for n in neg_set]) 
    pos_weight = sum([node_weight_map[n] for n in pos_set]) 
    assert pos_weight > 0 
    if pos_weight <= neg_weight: return None 

    coeff = neg_weight / pos_weight - 1 
    if coeff == 0: 
        return None 
    return -abs(len(node_map) * q / coeff)

def guess_min_max_strangle_breaking_force(num_nodes,node_weight_map,hypothesized_max_node_force): 
    # get min 
    node_map = {i:hypothesized_max_node_force for i in range(num_nodes)}
    q = min_strangle_breaking_force(node_map,node_weight_map) 

    max_node_map = {i:hypothesized_max_node_force for i in range(num_nodes)} 
    # case: odd 
    if num_nodes % 2: 
        h = floor(num_nodes/2) 
    else: 
        h = int(num_nodes / 2 - 1)

    for i in range(h): 
        max_node_map[i] = 0 
    
    # get max 
    q2 = min_strangle_breaking_force(max_node_map,node_weight_map) 
    if type(q2) == type(None): 
        q2 = q 

    return sorted([q,q2]) 

class StrangleForm: 

    def __init__(self,G,prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        force_assignment_type="random",force_per_node_range=[10,1000],energy=10**6,\
        enable_consumption:bool=False): 
        assert type(G) == defaultdict
        assert type(prg) in {FunctionType,MethodType}
        assert type(edge_cost_function) in {FunctionType,MethodType}
        assert force_assignment_type in {"random","degree-proportional"}
        assert is_valid_range(force_per_node_range,True,False) or is_valid_range(force_per_node_range,False,False)
        assert force_per_node_range[0] > 0
        assert type(enable_consumption) == bool 

        self.G = G 
        self.prg = prg 
        self.edge_cost_function = edge_cost_function
        self.force_assignment_type = force_assignment_type
        self.force_per_node_range = force_per_node_range
        self.usgcs = [] 
        self.max_degree = max([len(v) for v in self.G.values()]) 
        assert self.max_degree > 0 
        self.held_nodes = dict() 
        self.broken_hold = set() 
        self.hold_frequency = defaultdict(float) 
        self.strangled_stat = False 

        self.energy = energy 
        self.consumed = set() 
        self.enable_consumption = enable_consumption

        self.highest_score = 0. 

    def strangle_status(self): 
        return (len(self.held_nodes),len(self.broken_hold),len(self.usgcs)) 

    def node_status(self,open_info):  
        d = {k:0 for k in self.G.keys()}
        if not open_info: 
            return d 
        
        for k,v in self.held_nodes.items(): 
            d[k] = v 
        return d 

    def score(self,W=None,consumed_ratio=0.5): 
        s = 0 
        if type(W) == dict: 
            for c in self.consumed: 
                s += (W[c] * consumed_ratio)
            for k in self.held_nodes.keys(): 
                s += W[k] 
        else: 
            s += (len(self.consumed) * consumed_ratio) 
            s += len(self.held_nodes)
        self.highest_score = max([self.highest_score,s]) 
        return s 

    def register_reaction(self,counter_force): 
        broken_hold = set() 
        for k,v in counter_force.items(): 

            # case: StrangleSubject transfers energy over to 
            #       Strangler 
            if v > 0: 
                self.energy += v 
                continue 

            if k not in self.held_nodes: continue 
            self.held_nodes[k] += v 
            if self.held_nodes[k] <= 0.: 
                broken_hold |= {k} 
        
        self.update_broken_hold(broken_hold)
        return broken_hold 

    def move(self,entry_points,traversal_type_seq=None): 
        # sanity check 
        q = self.consumed.intersection(set(self.G.keys()))
        assert q == set(), "got {}".format(q) 

        if self.strangled_stat: 
            return 

        if len(self.held_nodes) == 0: 
            self.initiate_stranglehold(entry_points,traversal_type_seq) 
        elif len(self.broken_hold) > 0: 
            self.initiate_stranglehold(entry_points,traversal_type_seq) 
        else: 
            pass 

        self.move__advance() 
        return 

    def check_strangled_stat(self): 
        if set(self.held_nodes.keys()) == set(self.G.keys()): 
            self.strangled_stat = True 

    def move__advance(self): 
        for i in range(len(self.usgcs)): 
            self.advance_one_controller(i)

        self.clean_controllers() 
    
    def clean_controllers(self): 
        i = 0
        while i < len(self.usgcs): 
            stat = self.clean_one_controller(i) 
            if stat: 
                ##print("\t** finished controller") 
                continue 
            i += 1 

    def clean_one_controller(self,index): 
        usgc = self.usgcs[index]
        
        keys= set(usgc.searches.keys())
        for k in keys: 
            q = usgc.searches[k] 
            if q.fin_stat: 
                del usgc.searches[k] 

        if len(usgc.searches) == 0: 
            self.usgcs.pop(index) 
            return True 
        return False 

    def advance_one_controller(self,controller_index): 
        usgc = self.usgcs[controller_index]
        search_indices = sorted(usgc.searches.keys()) 

        for si in search_indices: 
            new_nodes,stat = self.move_one_search(usgc,si)
            if stat: continue 
            self.assign_force(new_nodes) 
        return 
        
    def move_one_search(self,usgc,index): 

        while True: 
            cost,not_finished,_ = usgc.move_search(index)

            if not not_finished: 
                return None,not not_finished 
            
            self.energy -= cost 
            x = usgc.recent_edges(index)
            if len(x) > 0:
                new_nodes = set([x_[1] for x_ in x])
                return new_nodes, False  

    def initiate_stranglehold(self,entry_points,traversal_type_seq=None): 
        self.initiate_stranglehold_(sorted(entry_points),traversal_type_seq) 
        self.assign_force(entry_points)

    def initiate_stranglehold_(self,entry_points,traversal_type_seq=None):  
        if type(traversal_type_seq) == type(None): 
            traversal_type_seq = ["dfs"] * len(entry_points) 
        else: 
            assert type(traversal_type_seq) == list 
            assert len(traversal_type_seq) == len(entry_points) 
            assert set(traversal_type_seq).issubset({"bfs","dfs"}) 
        assert type(entry_points) == list 
        assert len(entry_points) == len(set(entry_points)) 

        tdict = {"bfs":False,"dfs":True}
        traversal_type_seq = [tdict[t] for t in traversal_type_seq] 

        usgc = USGController()

        px = DEFAULT_PRNG_TO_NEXTNODE_PRIORITY_FUNCTION__DFS(self.prg)

        for p,t in zip(entry_points,traversal_type_seq): 
            usgc.set_new_search(is_dfs=t,start_node=p,d=self.G,\
            edge_cost_function=self.edge_cost_function,\
            nextnode_priority_function=px,search_target_nodeset=set(),\
            no_duplicate_touch_nodes=True)
        usgc.set_no_duplicate_touch__combined(True) 
        self.usgcs.append(usgc)

        while len(self.usgcs) > DEFAULT_MAX_NUMBER_OF_STRANGLEFORM_ENTITIES:  
            self.usgcs.pop(0)

        return

    def switch_force_assignment(self): 
        if self.force_assignment_type == "random": 
            self.force_assignment_type = "degree-proportional" 
        else: 
            self.force_assignment_type = "random" 
        return 

    def assign_force(self,nodeset): 
        assert type(nodeset) == set 
        nodeseq = sorted(nodeset.intersection(set(self.G.keys())))  
        cumulative_force = 0 
        max_degree = max([len(self.G[n]) for n in nodeseq]) 
        for n in nodeseq: 
            assert n in self.G 
            if n in self.held_nodes: 
                continue 
            if self.force_assignment_type == "degree-proportional":
                degree = len(self.G[n])
                f = degree / max_degree
                f = f * (self.force_per_node_range[1] - self.force_per_node_range[0])
                q = self.force_per_node_range[0] + f 
            else: 
                q = modulo_in_range(self.prg(),self.force_per_node_range) 
            self.held_nodes[n] = q
            self.broken_hold -= {n}   
            cumulative_force += q 
            self.hold_frequency[n] += 1 
        self.energy -= cumulative_force
        return cumulative_force 

    def update_broken_hold(self,broken_hold): 
        for b in broken_hold: 
            del self.held_nodes[b] 
        self.broken_hold |= broken_hold
        return

    def consume(self): 
        if not self.enable_consumption: 
            return None,None 

        consumed_set = self.choose_consumption()
        if len(consumed_set) == 0: 
            return None,None 
        assert consumed_set.intersection(self.consumed) == set()
        self.consumed |= consumed_set

        q = MicroGraph(deepcopy(self.G))
        q.subgraph_nodeset_exclusion(self.consumed)  
        assert set(q.dg.keys()).intersection(self.consumed) == set() 
        self.G = deepcopy(q.dg)

        for c in consumed_set: 
            del self.held_nodes[c] 
            del self.hold_frequency[c] 

        assert self.consumed.intersection(set(self.G.keys())) == set() 
        return consumed_set,deepcopy(self.G)

    def choose_consumption(self): 
        # get the held nodes that exceed hold frequency 
        consumption_candidates = set() 

        keys = set(self.held_nodes.keys())
        for h in keys: 
            if h not in self.G: 
                del self.held_nodes[h] 
                del self.hold_frequency[h] 
                continue 

            if self.hold_frequency[h] >= \
                DEFAULT_STRANGLER_HOLD_FREQUENCY_CONSUMPTION_MIN_THRESHOLD: 
                consumption_candidates |= {h} 

        if len(consumption_candidates) == 0: return set() 

        consumption_candidates = sorted(consumption_candidates) 

        q = prg_decimal(self.prg,[0.,1.]) 
        n = ceil(q * len(consumption_candidates))
        if n == 0: 
            return set() 
        selection = prg_choose_n(consumption_candidates,n,prg__single_to_int(self.prg),True)
        return set(selection)

"""
Data structure used by <StrangleEnv> to relay information to <StrangleSubject>. 
The information is used by <StrangleSubject> to calculate its decision on applying 
the appropriate breaking force to the appropriate community (nodeset) where strangling 
is taking place.  

info type 0 -> 
    map, node -> 0 force (equivalent to no node status given)
info type 1 ->
    list, of communities calculated by <StrangleSubject> s.t. every 
        community has at least 1 node being strangled. 
info type 2 -> 
    set, of nodes being strangled by <StrangleForm> 
info type 3 -> 
    [0] map, node -> strangling force (0 if no strangle) 
    [1] map, node -> node weight
"""
class StrangleFormInfo: 

    def __init__(self,info_type): 
        assert info_type in {0,1,2,3} 
        self.info_type = info_type  
        #print("IT: ",self.info_type)
        self.info = None 

    def load_info(self,sform,node_weights,communities):  
        assert type(sform) == StrangleForm 

        # node -> 0. 
        if self.info_type == 0: 
            self.info = sform.node_status(bool(self.info_type)) 
        # list of communities with at least 1 strangled node. 
        elif self.info_type == 1: 
            q = set(sform.held_nodes.keys())
            active_comm = [] 
            for c in communities: 
                if c.intersection(q) != set(): 
                    active_comm.append(c) 
            self.info = active_comm 
        # set(strangled nodes) 
        elif self.info_type == 2: 
            q = set(sform.held_nodes.keys())
            self.info = q
        # [0] node -> strangling force 
        # [1] node -> weight 
        else: 
            self.info = (sform.node_status(bool(self.info_type)),\
                node_weights)
        return 

class StrangleSubject: 

    def __init__(self,G,num_comm_range,break_prg,comm_prg,force_per_node_range,energy=10**6):  
        assert type(G) == defaultdict
        assert is_valid_range(num_comm_range,True,False)
        assert type(break_prg) in {FunctionType,MethodType}
        assert type(comm_prg) in {FunctionType,MethodType}

        self.G = G 
        self.num_comm_range = num_comm_range
        self.break_prg = break_prg
        self.comm_prg = comm_prg 
        self.force_per_node_range = force_per_node_range
        self.energy = energy 
        self.communities = None 

        self.surface_info = None 

        # (nodeset,float: cumulative force)
        self.break_decision = None 
        return

    def calculate_communities(self):
        num_comm = modulo_in_range(int(self.comm_prg()),self.num_comm_range) 
        if num_comm > len(self.G): 
            num_comm = modulo_in_range(int(self.comm_prg()),[1,len(self.G)]) 

        self.communities = ReinforcementCommunityFinder.partition_into_n_communities(\
            self.G,num_comm,self.comm_prg,max_reassignment=False,fast_part=True,\
            verbose=False) 

        return

    def receive_surface_info(self,sfi:StrangleFormInfo):
        assert type(sfi) == StrangleFormInfo
        self.surface_info = sfi 
        return

    """
    Chooses one of the calculated graph communities, from method<calculate_communities>, 
    to break out strangled nodes. Then hypothesizes a breaking force to apply over the 
    community nodeset. In modes 0-2, where there is limited information on the status 
    of the community nodes, the hypothesis is based on method<guess_min_max_strangle_breaking_force>. 
    In mode 3, all relevant information is known, so the method used calculates the most 
    cost-efficient breaking force, method<min_strangle_breaking_force>. 

    return:
    - community::nodeset, (breaking force)::float
    """
    def break_decision_(self):
        if self.surface_info.info_type == 0: 
            self.break_decision = self.estimate_force_info_type_0()
        elif self.surface_info.info_type == 1: 
            self.break_decision = self.estimate_force_info_type_1()
        elif self.surface_info.info_type == 2: 
            self.break_decision = self.estimate_force_info_type_2()
        else: 
            self.break_decision = self.estimate_force_info_type_3()
        self.energy += self.break_decision[1] 
        return self.break_decision 

    def estimate_force_info_type_0(self): 
        assert self.surface_info.info_type == 0  

        # choose a component 
        q = int(self.break_prg()) % len(self.communities) 
        comm = self.communities[q] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_1(self): 
        assert self.surface_info.info_type == 1 
        comms = self.surface_info.info 

        if len(comms) == 0: 
            return 0 

        q = int(self.break_prg()) % len(comms) 
        comm = self.communities[q] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_2(self): 
        assert self.surface_info.info_type == 2 

        cx = self.communities_strangled_node_count(self.surface_info.info)
        cx = prg_seqsort_ties(cx,prg__single_to_int(self.break_prg),vf=lambda x:x[1])
        comm = cx[-1][0] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_3(self): 
        
        # get strangled nodes 
        q = {k for k,v in self.surface_info.info[0].items() if v != 0.} 
        cx = self.communities_strangled_node_count(q,True) 

        # choose a community 
        cx = prg_seqsort_ties(cx,prg__single_to_int(self.break_prg),vf=lambda x:x[1])
        comm = cx[-1][0] 

        # get the minumum breaking force for strangled nodes of community 
        d0 = {k:v for k,v in self.surface_info.info[0].items() if k in comm} 
        d1 = {k:v for k,v in self.surface_info.info[1].items() if k in comm} 

        F = min_strangle_breaking_force(d0,node_weight_map=d1) 
        if type(F) == type(None): F = 0 
        return comm,F 

    def communities_strangled_node_count(self,active_nodes,output_ratio:bool=False): 

        def number_of_strangled_in_community(comm): 
            q = 0 
            for c in comm: 
                if c in active_nodes: 
                    q += 1
            if output_ratio: return q / len(comm)
            return q 

        cx = [] 
        for c in self.communities: 
            q = number_of_strangled_in_community(c)
            cx.append((c,q))
        return cx 

    def guess_force_for_component(self,component): 

        # guess the max node force based on interval 
        q = modulo_in_range(int(self.break_prg()),[0,DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION+1])
        q = q / DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION 

        b = np.array([self.force_per_node_range])
        rv = np.array([q]) 
        p0 = point_on_bounds_by_ratio_vector(b,rv)[0] 

        # guess the (min,max) breaking force
        M = guess_min_max_strangle_breaking_force(len(component),None,p0) 
        
        # choose a value in the (min,max) 
        q = modulo_in_range(int(self.break_prg()),[0,DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION+1])
        q = q / DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION 
        
        b = np.array([M])
        rv1 = np.array([q]) 
        p1 = point_on_bounds_by_ratio_vector(b,rv1)[0] 
        return p1