from graph_models.analog_graph import * 
from graph_models.analog_schemes import * 

HTE_THREAT_TYPES = {"contra","constant"}
HTE_THREAT_DEFAULT_ACTIVATION_LIFESPAN = [1,13]

# TODO: test. 
"""
Threat object for Hidden Threat Exposure problem. 
"""
class HTEThreat:

    def __init__(self,node_idn,activation_lifespan,derivative_type): 
        assert type(activation_lifespan) == int and activation_lifespan > 0 
        assert derivative_type in HTE_THREAT_TYPES 

        self.node_idn = node_idn 
        self.activation_lifespan = activation_lifespan
        self.c = 0 
        self.fin_stat = False 
        self.derivative_type = derivative_type
        self.navigator_path_info = [] 
        self.other_threat_locs = set() 
        return

    def load_navigator_path_info(self,navigator_path_info,other_threat_locs): 
        assert type(navigator_path_info) == list 
        assert type(other_threat_locs) == set 

        self.navigator_path_info = navigator_path_info
        self.other_threat_locs = other_threat_locs
        return

    def activate(self,navigator_path_info,other_threat_locs): 
        if self.fin_stat: 
            return False 

        if self.c >= self.activation_lifespan:
            self.fin_stat = True 
            return False 

        self.c += 1 
        self.load_navigator_path_info(navigator_path_info,other_threat_locs) 

        if self.derivative_type == "contra": 
            return self.contra_location()
        return self.node_idn 

    def contra_location(self): 
        assert self.derivative_type == "contra" 

        # case: no navigator path info provided. 
        if len(self.navigator_path_info) == 0: 
            return self.node_idn 
        
        # case: choose a node on the subpath of 
        #       `navigator_path_info`, with tail 
        #       at `node_idn` 

        #   subcase: `node_idn` not in `navigator_path_info`, 
        #             due to bug. Stay at `node_idn``
        subpath = self.subpath_to_loc() 
        if type(subpath) == type(None): 
            return self.node_idn 

        X = sorted(set(subpath) - self.other_threat_locs - {self.node_idn})  
        if len(X) == 0: 
            return self.node_idn 

        i = int(self.prg()) % len(X) 
        return X[i] 

    def subpath_to_loc(self): 
        # calculates the first subpath to node location 
        if self.node_idn not in self.navigator_path_info: 
            return None 
        
        subpath_index = self.navigator_path_info.index(self.node_idn)
        return self.navigator_path_info[:subpath_index + 1] 


# TODO: test. 
"""
Surface (setting) for Hidden Threat Exposure problem. 
""" 
class HTESurface: 

    def __init__(self,base_graph:defaultdict,entry_points:set,objective_points:set,threat_map):  
        assert type(base_graph) == defaultdict
        assert type(entry_points) == set 
        assert type(objective_points) == set 
        assert type(threat_map) == dict 
        assert set(threat_map.keys()).intersection(objective_points) == set() 

        self.base_graph = base_graph 
        self.entry_points = entry_points
        self.objective_points = objective_points 
        self.threat_map = threat_map 

    # TODO: test. 
    @staticmethod 
    def generate_instance(base_graph,num_entry_points,num_objective_points,threat_ratio,\ 
        threat_lifespan_range,threat_mobility_ratio,threat_nodes_include_entry_points:bool,\
        prg,activation_lifespan_range=HTE_THREAT_DEFAULT_ACTIVATION_LIFESPAN): 
        
        def prg_(): return int(prg()) 
        assert num_entry_points + num_objective_points < len(base_graph)

        # determine the entry and objective points 
        X0,X1 = BDFSCache.BFS_full(G,return_type="distance",prg=prg) 
        assert len(X1) == 1, "connected graph required" 

        stat = is_undirected_graph(base_graph) 
        bg = base_graph if not stat else undirected_graph_to_directed_graph
        entry_points,objective_points = peripheral_node_partition(base_graph,\
            part1_size=num_entry_points,part2_size=num_objective_points,prg=prg,\
            nodepair_path_info=X0) 

        # assign threats 
        x = set() if not threat_nodes_include_entry_points else entry_points
        threat_candidates = sorted(set(base_graph.keys()) - x - objective_points)
        num_threats = threat_ratio * len(threat_candidates)
        threat_nodes = prg_choose_n(threat_candidates,num_threats,prg_,is_unique_picker=True) 

        # assign mobile threats 
        num_mthreats = threat_mobility_ratio * len(threat_nodes) 
        mobile_threats = prg_choose_n(threat_nodes,num_mthreats,prg_,is_unique_picker=True) 

        # assign threat map 
        threat_map = dict() 
        for m in mobile_threats: 
            activation_lifespan = modulo_in_range(int(prg()),activation_lifespan_range)
            htd = HTEThreatDerivation(m,activation_lifespan,"contra") 
            threat_map[m] = htd 

        for m in threat_candidates: 
            activation_lifespan = modulo_in_range(int(prg()),activation_lifespan_range)
            htd = HTEThreatDerivation(m,activation_lifespan,"constant") 
            threat_map[m] = htd 
        return HTESurface(base_graph,entry_points,objective_points,threat_map) 