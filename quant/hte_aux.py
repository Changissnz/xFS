from graph_models.analog_graph import * 
from graph_models.analog_schemes import * 
from graph_models.community import * 
from graph_models.shortest_paths_approx import * 

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

    def reproduce(self): 
        return HTEThreat(self.node_idn,self.activation_lifespan,self.derivative_type) 

    def load_navigator_path_info(self,navigator_path_info,other_threat_locs): 
        assert type(navigator_path_info) == list 
        assert type(other_threat_locs) == set 

        self.navigator_path_info = navigator_path_info
        self.other_threat_locs = other_threat_locs
        return

    def activate(self,navigator_path_info,other_threat_locs): 
        if self.fin_stat: 
            return 

        if self.c >= self.activation_lifespan:
            self.fin_stat = True 
            return

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

HTE_SURFACE_DERIVATION_RADIUS_RATIO_RANGE = [0.1,0.525]

# TODO: test. 
"""
Surface (setting) for Hidden Threat Exposure problem. 
""" 
class HTESurface: 

    def __init__(self,base_graph:defaultdict,entry_points:set,objective_points:set,threat_map,\
        surface_derivation_radius_ratio_range=HTE_SURFACE_DERIVATION_RADIUS_RATIO_RANGE,prg=None):

        assert type(base_graph) == defaultdict
        assert type(entry_points) == set 
        assert type(objective_points) == set 
        assert type(threat_map) == dict 
        assert set(threat_map.keys()).intersection(objective_points) == set() 
        assert is_valid_range(surface_derivation_radius_ratio_range,False,False)
        assert 0. < surface_derivation_radius_ratio_range[0] <= surface_derivation_radius_ratio_range[1]\
            <= 1. 
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        ## NOTE: graph should be undirected
        self.base_graph = base_graph 
        #assert is_undirected_graph(self.base_graph)
        self.entry_points = entry_points
        self.objective_points = objective_points 
        self.threat_map = threat_map 
        self.surface_derivation_radius_ratio_range = surface_derivation_radius_ratio_range
        self.prg = prg 

    #----------------------- methods for information on <HTESurface> 

    def __str__(self): 
        S = "total # of points:\t" + str(len(self.base_graph)) + "\n"
        #S += "GRAPH" + str(self.base_graph) + "\n" 
        S += "entry points\n" + str(self.entry_points)
        S += "\n" + "objective points\n" + str(self.objective_points) 
        S += "\n" + "threat points\n" + str(sorted(self.threat_map.keys())) 
        return S 

    def threat_node_identifiers(self,derivative_types = HTE_THREAT_TYPES): 
        N = set() 
        for k,v in self.threat_map.items(): 
            if v.derivative_type in derivative_types: 
                N |= {k} 
        return N 

    #------------------------ methods for reproduction and generation 

    # NOTE: this reproduction scheme tends to produce graphs of smaller node size 
    #       than original. 
    def prng_reproduction(self,gen_subgraph_shortest_paths_parameters=[10,40]):
        # calculate 4 communities  
        communities = ReinforcementCommunityFinder.partition_into_n_communities(\
            self.base_graph,4,self.prg,max_reassignment=False,fast_part=True,verbose=False)

        # gather communities into disjoint subgraphs
        mg = MicroGraph(deepcopy(self.base_graph))
        mg_ = MicroGraph(defaultdict(set,{})) 
        for cns in communities: 
            sg = mg.subgraph_by_nodeset_(cns) 
            mg_ = mg_ + MicroGraph(graph_to_one_component(sg.dg,self.prg))
        assert len(mg_.dg) == len(self.base_graph)

        g2 = mg_.dg 
        # make analogical subgraphs 
        lx = len(communities) 

        gaa = GraphAnalogAdder(mg_.dg,is_dsg=False,prg=self.prg,\
            gen_subgraph_shortest_paths_parameters=gen_subgraph_shortest_paths_parameters,\
            gen_scheme_types=[1,2],connect_components=False,every_subgraph_is_connected=True,\
            max_edge_changes=10000,store_isomaps=True,verbose=True)

        for i in range(lx): gaa.extend() 

        # assign entry,obj, and threat points 
        new_entry_points,new_obj_points,threat_map = self.prng_reproduction__assign_nodesets(gaa)
        new_nodeset = gaa.subgraph_nodeset_log[-lx:]

        # merge analogical subgraphs into one connected graph 
        new_nodeset = flatten_setseq(new_nodeset) 
        sg = MicroGraph(gaa.d).subgraph_by_nodeset_(new_nodeset).dg 
        sg = graph_to_one_component(sg,self.prg)

        cumulative_isolog = dict() 
        for x in gaa.isomap_log[-lx:]: 
            cumulative_isolog.update(x) 

        return HTESurface(sg,new_entry_points,new_obj_points,threat_map,\
        surface_derivation_radius_ratio_range=self.surface_derivation_radius_ratio_range,\
        prg=self.prg), cumulative_isolog 

    # NOTE: this reproduction scheme typically bears a graph more similar to the original. 
    def prng_reproduction_scheme2(self): 

        gaa = GraphAnalogAdder(self.base_graph,is_dsg=False,prg=self.prg,\
            gen_subgraph_derivation_ratios=[0.2,0],
            gen_scheme_types=[2],connect_components=False,every_subgraph_is_connected=True,\
            max_edge_changes=10000,store_isomaps=True,verbose=True)
        gaa.extend() 

        # assign entry,obj, and threat points 
        new_entry_points,new_obj_points,threat_map = self.prng_reproduction__assign_nodesets(gaa)
 
        new_nodeset = gaa.subgraph_nodeset_log[-1] 
        sg = MicroGraph(gaa.d).subgraph_by_nodeset_(new_nodeset).dg 
        sg = graph_to_one_component(sg,self.prg)
        return HTESurface(sg,new_entry_points,new_obj_points,threat_map,\
        surface_derivation_radius_ratio_range=self.surface_derivation_radius_ratio_range,\
        prg=self.prg), gaa.isomap_log[-1] 

    # TODO: test 
    # NOTE: method should be used only by method<prng_reproduction>
    def prng_reproduction__assign_nodesets(self,gaa,verbose=False): 

        def find_point_in_isomap(p): 
            for isomap in gaa.isomap_log: 
                if p in isomap: 
                    return isomap[p] 
            return None 

        new_entry_points = set()
        new_obj_points = set() 

        for epoint in self.entry_points:
            equivalent = find_point_in_isomap(epoint)
            if type(equivalent) == type(None): 
                if verbose: print("no equivalent for entry {}".format(epoint))
                continue 
            new_entry_points |= {equivalent}

        for opoint in self.objective_points:
            equivalent = find_point_in_isomap(opoint) 
            if type(equivalent) == type(None): 
                if verbose: print("no equivalent for objective {}".format(opoint))
                continue 
            new_obj_points |= {equivalent}
        
        ks = sorted(self.base_graph.keys())

        # ensure at least one entry point and one objective point 
        if len(new_entry_points) == 0: 
            index = int(self.prg()) % len(ks) 
            epoint = ks[index] 
            new_entry_points |= {epoint} 
        
        if len(new_obj_points) == 0: 
            index = int(self.prg()) % len(ks)
            opoint = ks[index] 
            new_obj_points |= {opoint} 

        # assign as many threats as iso-nodes exist that are not 
        # objectives 
        threat_map = {} 
        for k,v in self.threat_map.items(): 
            tpoint = find_point_in_isomap(k) 
            if type(tpoint) == type(None): 
                if verbose: print("no equivalent for threat {}".format(tpoint))
                continue 
            if tpoint in new_obj_points: continue 
            threat_map[tpoint] = v.reproduce() 
            threat_map[tpoint].node_idn = tpoint 
        return new_entry_points,new_obj_points,threat_map 

    # TODO: test.
    # NOTE:  
    @staticmethod 
    def generate_instance(base_graph,num_entry_points,num_objective_points,threat_ratio,\
        threat_mobility_ratio,threat_nodes_include_entry_points:bool,\
        prg,surface_derivation_radius_ratio_range= HTE_SURFACE_DERIVATION_RADIUS_RATIO_RANGE,\
        activation_lifespan_range=HTE_THREAT_DEFAULT_ACTIVATION_LIFESPAN): 
        
        def prg_(): return int(prg()) 
        
        assert num_entry_points + num_objective_points < len(base_graph)

        x1 = deepcopy(base_graph)
        gd = GraphComponentDecomposition(x1)
        gd.decompose() 
        assert x1 == base_graph
        assert len(gd.components) == 1 and not gd.is_directed, "connected undirected graph required" 

        # determine the entry and objective points 
        spa = ShortestPathsApproximator.default_shortest_paths_search(base_graph,prg) 
        entry_points,objective_points = peripheral_node_partition(base_graph,\
            part1_size=num_entry_points,part2_size=num_objective_points,prg=prg,\
            nodepair_path_info=spa.nodepair_path_info)  

        # assign threats 
        x = set() if threat_nodes_include_entry_points else entry_points
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
            htd = HTEThreat(m,activation_lifespan,"contra") 
            threat_map[m] = htd 

        for m in threat_nodes:  
            activation_lifespan = modulo_in_range(int(prg()),activation_lifespan_range)
            htd = HTEThreat(m,activation_lifespan,"constant") 
            threat_map[m] = htd 

        
        return HTESurface(base_graph,entry_points,objective_points,threat_map,\
            surface_derivation_radius_ratio_range=surface_derivation_radius_ratio_range,\
            prg=prg)  

    #--------------------------------------------------------------------------------------------

    def update_threat_activation(self,threat_idn,navigator_path_info,other_threat_locs): 
        assert threat_idn in self.threat_map 

        T = self.threat_map[threat_idn] 
        T2 = T.activate(navigator_path_info,other_threat_locs)
    
        # case: nullified threat 
        if type(T2) == type(None): 
            return 

        # case: threat relocated 
        if T2 != threat_idn: 
            T.node_idn = T2 
            del self.threat_map[threat_idn] 
            self.threat_map[T2] = T 
        return