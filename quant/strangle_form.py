from graph_models.community import * 
from .usg_controller import * 
from types import FunctionType,MethodType
from morebs2.matrix_methods import is_valid_range,point_on_bounds_by_ratio_vector
from morebs2.numerical_generator import modulo_in_range
from morebs2.measures import zero_div 

# used by <StrangleSubject> for guessing force to break strangleholds. 
DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION = 5 


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

    coeff = neg_weight / pos_weight - 1 
    if coeff == 0: 
        return None 
    return len(node_map) * q / coeff

def guess_min_max_strangle_breaking_force(num_nodes,hypothesized_max_node_force): 

    # get min 
    node_map = {k:hypothesized_max_node_force for i in range(num_nodes)}
    q = min_strangle_breaking_force(node_map) 

    max_node_map = {k:hypothesized_max_node_force for i in range(num_nodes)} 
    # case: odd 
    if num_nodes % 2: 
        h = ceil(num_nodes/2) 
    else: 
        h = int(num_nodes / 2 + 1)

    for i in range(h): 
        max_node_map[i] = 0 

    # get max 
    q2 = min_strangle_breaking_force(max_node_map) 
    return sorted([q,q2]) 

class StrangleForm: 

    def __init__(self,G,prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        force_assignment_type="random",force_per_node_range=[10,1000]): 
        assert type(G) == defaultdict
        assert type(prg) in {FunctionType,MethodType}
        assert type(edge_cost_function) in {FunctionType,MethodType}
        assert force_assignment_type in {"random","degree-proportional"}
        assert is_valid_range(force_per_node_range,True,False) or is_valid_range(force_per_node_range,False,False)
        assert force_per_node_range[0] > 0

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
        self.strangled_stat = False 

    def node_status(self,open_info):  
        d = {k:0 for k in self.G.keys()}
        if not open_info: 
            return d 
        
        for k,v in self.held_nodes.items(): 
            d[k] = v 
        return d 

    def register_reaction(self,counter_force): 

        broken_hold = set() 
        for k,v in counter_force.items(): 
            assert v <= 0.  
            if k not in self.held_nodes: continue 
            self.held_nodes[k] += v 
            if self.held_nodes[k] <= 0.: 
                broken_hold |= {k} 
        
        self.update_broken_hold(broken_hold)
        return broken_hold 

    def move(self,entry_points,traversal_type_seq=None): 

        if self.strangled_stat: 
            return 

        if len(self.held_nodes) == 0: 
            self.initiate_stranglehold(entry_points,traversal_type_seq) 
        elif len(self.broken_hold) > 0: 
            self.initiate_stranglehold(entry_points,traversal_type_seq) 
        else: 
            pass 

        self.move__advance() 
        if set(self.held_nodes.keys()) == set(self.G.keys()): 
            self.strangled_stat = True 
        return 

    def move__advance(self): 
        for i in range(len(self.usgcs)): 
            self.advance_one_controller(i)

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
            _,not_finished,_ = usgc.move_search(index)

            if not not_finished: 
                return None,not not_finished 

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
        return

    def switch_force_assignment(self): 
        if self.force_assignment_type == "random": 
            self.force_assignment_type = "degree-proportional" 
        else: 
            self.force_assignment_type = "random" 
        return 

    def assign_force(self,nodeset): 
        assert type(nodeset) == set 
        nodeseq = sorted(nodeset) 

        cumulative_force = 0 
        for n in nodeseq: 
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
        return cumulative_force 

    def update_broken_hold(self,broken_hold): 
        for b in broken_hold: 
            del self.held_nodes[b] 
        self.broken_hold |= broken_hold
        return

class StrangleFormInfo: 

    def __init__(self,info_type,info): 
        assert info_type in {0,1,2,3} 
        self.info_type = info 
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

    def __init__(self,G,num_comm_range,break_prg,comm_prg,force_per_node_range):  
        assert type(G) == defaultdict
        assert is_valid_range(num_comm_range,True,False)
        assert type(break_prg) in {FunctionType,MethodType}
        assert type(comm_prg) in {FunctionType,MethodType}

        self.G = G 
        self.num_comm_range = num_comm_range
        self.break_prg = break_prg
        self.comm_prg = comm_prg 
        self.force_per_node_range = force_per_node_range
        self.communities = None 

        self.surface_info = None 

        # (nodeset,float: cumulative force)
        self.break_decision = None 
        return

    def calculate_communities(self):
        num_comm = modulo_in_range(int(self.comm_prg()),self.num_comm_range) 
        self.communities = ReinforcementCommunityFinder.partition_into_n_communities(\
            self.G,num_comm,self.comm_prg,verbose=False) 
        return

    def receive_surface_info(self,sfi:StrangleFormInfo):
        assert type(sfi) == StrangleFormInfo
        self.surface_info = sfi 
        return

    def break_decision(self):
        if self.sfi.info_type == 0: 
            self.break_decision = self.estimate_force_info_type_0()
        if self.sfi.info_type == 1: 
            self.break_decision = self.estimate_force_info_type_1()
        if self.sfi.info_type == 2: 
            self.break_decision = self.estimate_force_info_type_2()
        else: 
            self.break_decision = self.estimate_force_info_type_3()
        return self.break_decision 

    def estimate_force_info_type_0(self): 
        assert self.sfi.info_type == 0  

        # choose a component 
        q = int(self.break_prg()) % len(self.communities) 
        comm = self.communities[q] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_1(self): 
        assert self.sfi.info_type == 1 
        comms = self.sfi.info 

        if len(comms) == 0: 
            return 0 

        q = int(self.break_prg()) % len(comms) 
        comm = self.communities[q] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_2(self): 
        assert self.sfi.info_type == 2 

        cx = self.communities_strangled_node_count(self.sfi.info)
        cx = prg_seqsort_ties(cx,prg__single_to_int(self.prg),vf=lambda x:x[1])
        comm = cx[-1] 
        return comm,self.guess_force_for_component(comm) 

    def estimate_force_info_type_3(self): 

        # get strangled nodes 
        q = {k for k,v in self.sfi.info[0].items() if v != 0.} 
        cx = self.communities_strangled_node_count(q) 

        # choose a community 
        cx = prg_seqsort_ties(cx,prg__single_to_int(self.prg),vf=lambda x:x[1])
        comm = cx[-1] 

        # get the minumum breaking force for strangled nodes of community 
        d0 = {k:v for k,v in self.sfi.info[0].items() if k in comm} 
        d1 = {k:v for k,v in self.sfi.info[1].items() if k in comm} 
        return comm,min_strangle_breaking_force(d0,node_weight_map=d1) 

    def communities_strangled_node_count(self,active_nodes): 

        def number_of_strangled_in_community(comm): 
            q = 0 
            for c in comm: 
                if c in active_nodes: 
                    q += 1 
            return q 

        cx = [] 
        for c in self.communities: 
            q = number_of_strangled_in_community(c)
            cx.append((c,q))
        return cx 

    def guess_force_for_component(self,component): 

        # guess the max node force based on interval 
        q = modulo_in_range(int(self.break_prg()),DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION+1)
        q = q / DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION 

        b = np.array([self.force_per_node_range])
        rv = np.array([q]) 
        p0 = point_on_bounds_by_ratio_vector(b,rv)[0] 

        # guess the (min,max) breaking force
        M = guess_min_max_strangle_breaking_force(len(component),p0) 
        
        # choose a value in the (min,max) 
        q = modulo_in_range(int(self.break_prg()),DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION+1)
        q = q / DEFAULT_STRANGLESUBJECT_PR_DIST_PARTITION 

        b = np.array([M])
        rv1 = np.array([q]) 
        p1 = point_on_bounds_by_ratio_vector(b,rv1)[0] 
        return p1