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
        assert 0. < surface_derivation_radius_ratio_range[0] <= surface_derivation_radius_ratio_range[1]\
            <= 1. 
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        self.base_graph = base_graph 
        self.is_directed = not is_undirected_graph(self.base_graph)
        self.entry_points = entry_points
        self.objective_points = objective_points 
        self.threat_map = threat_map 
        self.surface_derivation_radius_ratio_range = surface_derivation_radius_ratio_range
        self.prg = prg 
        self.preproc() 

    def preproc(self): 
        self.rsf = RadialSubgraphFetcher(self.base_graph,prg=self.prg,return_type="paths")  
        return 

    def __str__(self): 
        S = "entry points\n" + str(self.entry_points)
        S += "\n" + "objective points\n" + str(self.objective_points) 
        S += "\n" + "threat points\n" + str(sorted(self.threat_map.keys())) 
        return S 

    def threat_node_identifiers(self,derivative_types = HTE_THREAT_TYPES): 
        N = set() 
        for k,v in self.threat_map.items(): 
            if v.derivative_type in derivative_types: 
                N |= {k} 
        return N 

    # TODO: test. 
    def prng_reproduction(self):
        # find community by radius 
        radius_ratio = modulo_in_range(self.prg(),self.surface_derivation_radius_ratio_range)
        rs = RadialGraphCommunities(self.base_graph,self.prg,radius_ratio,self.rsf) 
        rs.exec()

        # gather communities into disjoint subgraphs
        mg = MicroGraph(self.base_graph)
        mg_ = MicroGraph(defaultdict(set,{})) 
        for cns in rs.community_nodesets: 
            sg = mg.subgraph_by_nodeset_(cns) 
            mg_ = mg_ + sg 
        
        # 
        lx = len(rs.community_nodesets)
        gaa = GraphAnalogAdder(mg_.dg,is_dsg=self.is_directed,prg=self.prg,\
            gen_subgraph_shortest_paths_parameters=[10,6],gen_scheme_types=[1,2],\
            store_isomaps=True) 

        for _ in range(lx): 
            gaa.extend() 
        new_entry_points,new_obj_points,threat_map = self.prng_reproduction__assign_nodesets(gaa,lx)

        new_nodeset = gaa.nodeset_cache[-lx:] 
        new_nodeset = flatten_setseq(new_nodeset) 
        sg = MicroGraph(gaa.d).subgraph_by_nodeset_(new_nodeset).dg 
        sg = graph_to_one_component(sg,self.prg)

        return HTESurface(sg,new_entry_points,new_obj_points,threat_map,\
        surface_derivation_radius_ratio_range=self.surface_derivation_radius_ratio_range)

    # TODO: test 
    # NOTE: method should be used only by method<prng_reproduction>
    def prng_reproduction__assign_nodesets(self,gaa): 

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
                print("no equivalent for entry {}".format(epoint))
                continue 
            new_entry_points |= {equivalent}

        for opoint in self.objective_points:
            equivalent = find_point_in_isomap(opoint) 
            if type(equivalent) == type(None): 
                print("no equivalent for objective {}".format(opoint))
                continue 
            new_obj_points |= {equivalent}
        
        ks = sorted(self.base_graph.keys())

        # ensure at least one entry point and one objective point 
        if len(new_entry_points) == 0: 
            index = int(self.prg()) % ks 
            epoint = ks[index] 
            new_entry_points |= {epoint} 
        
        if len(new_obj_points) == 0: 
            index = int(self.prg()) % ks 
            opoint = ks[index] 
            new_obj_points |= {opoint} 

        # assign as many threats as iso-nodes exist that are not 
        # objectives 
        threat_map = {} 
        for k,v in self.threat_map.items(): 
            tpoint = find_point_in_isomap(k) 
            if type(tpoint) == type(None): 
                print("no equivalent for threat {}".format(tpoint))
                continue 
            if tpoint in new_obj_points: continue 
            threat_map[tpoint] = v.reproduce() 
            threat_map[tpoint].node_idn = tpoint 
        return new_entry_points,new_obj_points,threat_map 

    # TODO: test. 
    @staticmethod 
    def generate_instance(base_graph,num_entry_points,num_objective_points,threat_ratio,\
        threat_mobility_ratio,threat_nodes_include_entry_points:bool,\
        prg,activation_lifespan_range=HTE_THREAT_DEFAULT_ACTIVATION_LIFESPAN): 
        
        def prg_(): return int(prg()) 
        assert num_entry_points + num_objective_points < len(base_graph)

        # determine the entry and objective points 
        X0,X1 = BDFSCache.BFS_full(base_graph,return_type="distance",prg=prg) 
        assert len(X1) == 1, "connected graph required" 

        stat = is_undirected_graph(base_graph) 
        bg = base_graph if not stat else directed_to_undirected_graph(deepcopy(base_graph))
        entry_points,objective_points = peripheral_node_partition(bg,\
            part1_size=num_entry_points,part2_size=num_objective_points,prg=prg,\
            nodepair_path_info=X0) 

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
        return HTESurface(base_graph,entry_points,objective_points,threat_map) 