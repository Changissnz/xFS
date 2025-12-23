from .analog_schemes_aux import * 

"""
calculates derivatives (analogues) of `starting_graph`. After adding those derivatives 
to each of the `starting_graph` components, structure calculates analogues of those 
analogues, and the cycle repeats. 

There are three analogue generation schemes: 
1. Solely by the variable of `prg` (a pseudo-random number generator). 
2. Using a reference subgraph S of the running graph `d`, calculates shortest 
   paths of S and pieces those paths together for an automorphic subgraph A of 
   S', S' a subgraph of S. 
3. Using a reference subgraph S of the running graph `d`, (adds XOR deletes nodes) 
   AND (adds XOR deletes edges) from S. 

Every generated analogue is added to exactly one reference subgraph of running graph `d`. 
"""
class GraphAnalogAdder:

    def __init__(self,starting_graph:defaultdict,is_dsg:bool,prg=default_std_Python_prng(),\
        sg2sg_degconn_ratios = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH2SUBGRAPH_DEGCONN_RATIOS,\
        gen_scheme_subgraph_degree_range = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DEGREE_RANGE,\
        gen_subgraph_conn_range = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_CONN_RANGE,
        gen_subgraph_shortest_paths_parameters=DEFAULT_GRAPH_ANALOG_ADDER_SHORTEST_PATHS_PARAMETERS,\
        gen_subgraph_derivation_ratios=DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DERIVATION_RATIOS,\
        verbose=False): 

        assert type(is_dsg) == bool 

        stat = is_undirected_graph(starting_graph) 
        if not is_dsg: 
            assert stat

        assert type(prg) in {MethodType,FunctionType} 

        assert 0.0 <= sg2sg_degconn_ratios[0] <= 1.0
        assert 0.0 <= sg2sg_degconn_ratios[1] <= 1.0

        assert type(gen_scheme_subgraph_degree_range[0]) == type(gen_scheme_subgraph_degree_range[1]) == \
            int
        assert 0 < gen_scheme_subgraph_degree_range[0] < gen_scheme_subgraph_degree_range[1]  
        
        assert type(gen_subgraph_conn_range[0]) == type(gen_subgraph_conn_range[1]) == float 
        assert 0. <= gen_subgraph_conn_range[0] <= gen_subgraph_conn_range[1] <= 1. 

        assert type(gen_subgraph_shortest_paths_parameters[0]) == type(gen_subgraph_shortest_paths_parameters[1]) \
            == int 
        assert gen_subgraph_shortest_paths_parameters[0] > 0 
        assert gen_subgraph_shortest_paths_parameters[1] > 0

        assert 0.0 <= gen_subgraph_derivation_ratios[0] <= 1.0
        assert 0.0 <= gen_subgraph_derivation_ratios[1] <= 1.0

        self.d = starting_graph
        self.is_dsg = is_dsg 
        self.prg = prg 

        self.sg2sg_conn_ratios = sg2sg_degconn_ratios
        self.gen_scheme_subgraph_degree_range = gen_scheme_subgraph_degree_range
        self.gen_subgraph_conn_range = gen_subgraph_conn_range
        self.gen_subgraph_sp_param = gen_subgraph_shortest_paths_parameters
        self.gen_subgraph_derivation_ratios = gen_subgraph_derivation_ratios
        self.verbose = verbose 

        # new node counter 
        self.c = max(self.d.keys()) + 1 
        self.preproc()
        self.set_counter_function() 
        self.gen_scheme_log = [] 
        return 

    """
    calculates components of starting graph. Disregards directedness attribute 
    of each component. 
    """
    def preproc(self):
        gcd = GraphComponentDecomposition(self.d)
        gcd.decompose()
        self.components = []

        for x in gcd.components: 
            x_ = flatten_setseq(x) if type(x) != set else x 
            self.components.append(x_) 

        self.nodeset_cache = deepcopy(self.components) 
        self.new_nodesets = [] 
        return 

    def set_counter_function(self): 

        def f(): 
            q = self.c 
            self.c += 1 
            return q 

        self.ctr_function = f 
        return f 

    """
    main method 
    """
    def extend(self):  
        scheme_type = int(self.prg()) % 3 + 1 
        return self.new_subgraph(scheme_type)  

    def new_subgraph(self,scheme_type:int):
        assert scheme_type in {1,2,3} 
        if len(self.nodeset_cache) == 0: 
            self.nodeset_cache.extend(self.new_nodesets) 
            self.new_nodesets.clear() 
        assert len(self.nodeset_cache) > 0 

        index0 = int(self.prg()) % len(self.nodeset_cache) 
        ref_nodeset = self.nodeset_cache[index0] 

        # generate the subgraph 
        new_sg = None 
        if scheme_type == 1: 
            new_sg = self.prng_generate_subgraph() 
        elif scheme_type == 2: 
            new_sg = self.prng_generate_shortest_paths_analogue(ref_nodeset)
        else: 
            new_sg = self.prng_generate_subgraph_derivative(ref_nodeset) 

        self.gen_scheme_log.append(scheme_type)
        # delete the reference nodeset and add the new nodeset
        self.nodeset_cache.pop(index0) 
        new_nodeset = set(new_sg.keys()) 
        self.new_nodesets.append(new_nodeset) 

        # add the new subgraph to a reference subgraph 
        prior_sg = MicroGraph(self.d).subgraph_by_nodeset_(ref_nodeset).dg 
        new_sg_ = self.connect_subgraphs__prior_to_current(prior_sg,new_sg) 

        # update the entire graph 
        self.d = (MicroGraph(self.d) + MicroGraph(new_sg_)).dg

        if self.verbose: 
            print("generating subgraph of scheme type #{}".format(scheme_type)) 
            
        return prior_sg,new_sg 

    #--------------------- connection scheme 

    def connect_subgraphs__prior_to_current(self,prior_sg:defaultdict,current_sg:defaultdict): 
        return connect_subgraphs__prior_to_current(prior_sg,current_sg,self.is_dsg,\
            self.sg2sg_conn_ratios,self.prg)  

    #--------------------- generation scheme #1 

    def prng_generate_subgraph(self): 

        is_realtime_gen = bool(int(self.prg()) % 2)
        vertex_degree = int(modulo_in_range(self.prg(),self.gen_scheme_subgraph_degree_range))
 
        edge_connectivity = prng_decimal(self.prg,self.gen_subgraph_conn_range)
        gg = GraphGen(self.is_dsg,self.prg,is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity)
        gg.full_run() 
        return graph_automorphism(gg.d,self.ctr_function)[0]

    #-------------------- generation scheme #2 

    def prng_generate_shortest_paths_analogue(self,nodeset): 
        assert len(nodeset) > 0 

        # gather the subgraph 
        mg = MicroGraph(self.d) 
        G = mg.subgraph_by_nodeset_(nodeset).dg 
        assert len(G) > 0 

        # choose a random node from G 
        nodes = sorted(G.keys())
        node_index = int(self.prg()) % len(nodes)
        start_node = nodes.pop(node_index)

        return shortest_paths_graph_analogue(G,start_node,self.is_dsg,\
            self.gen_subgraph_sp_param[0],self.gen_subgraph_sp_param[1],\
            self.prg,self.ctr_function)[0] 

    #-------------------- generation scheme #3 

    def prng_generate_subgraph_derivative(self,nodeset): 
        assert len(nodeset) > 0 

        # gather the subgraph 
        mg = MicroGraph(self.d) 
        G = mg.subgraph_by_nodeset_(nodeset).dg
        assert len(G) > 0

        # get pos./neg. edge change 
        edge_range = [10**-5,self.gen_subgraph_derivation_ratios[0]]
        edge_change = prng_decimal(self.prg,edge_range)
        eneg = int(self.prg()) % 2
        eneg = -1 if eneg else 1 
        edge_change = eneg * edge_change 

        # get pos./neg. node change 
        node_range = [10**-5,self.gen_subgraph_derivation_ratios[1]]
        node_change = prng_decimal(self.prg,node_range)
        nneg = int(self.prg()) % 2
        nneg = -1 if nneg else 1 
        node_change = nneg * node_change 

        return graph_derivation(G,self.is_dsg,node_change,edge_change,self.prg,self.ctr_function)[0]
