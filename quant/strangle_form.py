from graph_models.community import * 
from .usg_controller import * 
from types import FunctionType,MethodType
from morebs2.matrix_methods import is_valid_range
from morebs2.numerical_generator import modulo_in_range

def default_strangle_breaking_function(node_map,F): 
    if len(node_map) == 0: return dict() 

    q = F / len(node_map) 
    smap = {k:q for k in node_map.keys()} 
    
    # get nodes that are not being strangled.
    neg_set = {k for k,v in node_map.items() if v <= 0.}
    pos_set = {k for k in node_map.keys() if k not in neg_set} 
    q2 = q * len(neg_set) 

    for s in smap.keys(): 
        if s in pos_set: 
            smap[s] -= q2 
    return smap 

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

    def load_info(self,sform,communities):  
        assert type(sform) == StrangleForm 

        if self.info_type == 0: 
            self.info = sform.node_status(bool(self.info_type)) 
        elif self.info_type == 1: 
            q = set(sform.held_nodes.keys())
            active_comm = [] 
            for c in communities: 
                if c.intersection(q) != set(): 
                    active_comm.append(c) 
            self.info = active_comm 
        elif self.info_type == 2: 
            q = set(sform.held_nodes.keys())
            self.info = q
        else: 
            self.info = sform.node_status(bool(self.info_type)) 
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

    def decide(self): 
        assert type(self.surface_info) == sfi 

        # case: 
        #if self.surface_info.info_type == 0: 
        return -1 

    def estimate_for_closed_info(self): 
        return -1 

