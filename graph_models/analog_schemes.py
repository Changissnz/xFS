from .graph_gen import * 
from .shortest_paths import * 

# these five default parameters are used for generation schemes of <GraphAnalogAdder> 
    # min for range of these ratios is 10 ** -5 
# [0]-> ratio for number of nodes from prior subgraph to connect to current subgraph 
# [1]-> ratio for max number of edges possible from prior subgraph nodes to current subgraph 
DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH2SUBGRAPH_DEGCONN_RATIOS = [0.15,0.4] 

    # 
DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DEGREE_RANGE = [5,35] 
DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_CONN_RANGE = [0.05,0.5]

# [0] -> max number of considered paths per node pair 
# [1] -> max for range (1,[1]==3) to select shortest paths between every node pair  
DEFAULT_GRAPH_ANALOG_ADDER_SHORTEST_PATHS_PARAMETERS = [10,3]

# [0] -> pos./neg. change in edges to subgraph 
# [1] -> pos./neg. change in nodes to subgraph 
DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DERIVATION_RATIOS = [0.2,0.25]

class GraphAnalogAdder:

    def __init__(self,starting_graph:defaultdict,is_dsg:bool,prg=default_std_Python_prng(),\
        sg2sg_degconn_ratios = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH2SUBGRAPH_DEGCONN_RATIOS,\
        gen_scheme_subgraph_degree_range = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DEGREE_RANGE,\
        gen_subgraph_conn_range = DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_CONN_RANGE,
        gen_subgraph_shortest_paths_parameters=DEFAULT_GRAPH_ANALOG_ADDER_SHORTEST_PATHS_PARAMETERS,\
        gen_subgraph_derivation_ratios=DEFAULT_GRAPH_ANALOG_ADDER_SUBGRAPH_DERIVATION_RATIOS): 

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
        assert gen_subgraph_shortest_paths_parameters[0] >= gen_subgraph_shortest_paths_parameters[1] > 0 

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

        # new node counter 
        self.c = max(self.d.keys()) + 1 
        self.preproc()
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
            x_ = flatten_setseq(x)
            self.components.append(x_) 

        self.new_nodesets = [] 
        return 

    def add_subgraph_to_nodeset(self): 
        print("ASSHIT")
        return -1 

    #--------------------- connection scheme 

    def connecting_edges_for_subgraph_to_nodeset(self,subgraph:defaultdict,\
        subgraph_nodeset:set,additive_subgraph:defaultdict,connectivity:float):  
        print("ASSHIT")
        return

    #--------------------- generation scheme #1 

    def prng_generate_subgraph(self,start_integer:int): 

        is_realtime_gen = bool(int(self.prg()) % 2)
        vertex_degree = int(modulo_in_range(self.prg(),self.gen_scheme_subgraph_degree_range))
 
        edge_connectivity = self.prng_decimal(self.gen_subgraph_conn_range)
        gg = GraphGen(self.is_dsg,self.prg,is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity)
        gg.full_run() 
        return self.isotransform_graph(gg.d)

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

        # calculate shortest paths 
        is_bfs = bool(int(self.prg()) % 2)
        bdfs = BDFSCache(start_node,G,is_bfs=is_bfs,prg=self.prg,\
            edge_cost_function=lambda u,v:1,\
            num_paths_per_node=self.gen_subgraph_sp_param[0]) 
        bdfs.exec() 

        # iterate through each sequence of shortest paths and select 
        min_paths = bcache.min_paths

        def prg_(): return int(self.prg())

        all_selected_paths = [] 
        for paths_seq in min_paths.values():
            lx = min([len(paths_seq),self.gen_subgraph_sp_param[1]])
            if lx == 0: continue 

            selected_paths = prg_choose_n(paths_seq,lx,prg_,is_unique_picker=True)
            all_selected_paths.extend(selected_paths)

        # piece NodePath instances into graph 
        G = NodePath.nodepath_set_to_graph(all_selected_paths)
        return self.isotransform_graph(G)

    #-------------------- generation scheme #3 

    def prng_generate_subgraph_derivative(self,nodeset): 
        assert len(nodeset) > 0 

        # gather the subgraph 
        mg = MicroGraph(self.d) 
        G = mg.subgraph_by_nodeset_(nodeset).dg
        assert len(G) > 0

        # get pos./neg. edge change 
        edge_range = [10**-5,self.gen_subgraph_derivation_ratios[0]]
        edge_change = prng_decimal(edge_range)
        eneg = int(self.prg()) % 2
        eneg = -1 if eneg else 1 
        edge_change = eneg * edge_change 

        # get pos./neg. node change 
        node_range = [10**-5,self.gen_subgraph_derivation_ratios[1]]
        node_range = prng_decimal(node_range)
        nneg = int(self.prg()) % 2
        nneg = -1 if nneg else 1 
        node_change = nneg * node_change 

        return self.graph_derivation(G,node_change,edge_change)

    #----------------- accessory methods 

    def isotransform_graph(self,G): 
        # make basic isomap for G 
        isomap = dict() 
        gnodes = sorted(G.keys()) 
        for gn in gnodes:
            isomap[gn] = self.c 
            self.c += 1 

        # isotransform graph to start at current index 
        mg = MicroGraph(G) 
        G = MicroGraph.isotransform_MG(mg,isomap).dg  
        return G 

    def graph_derivation(self,g:defaultdict,node_change_ratio,edge_change_ratio):
        def prg_(): return int(self.prg())

        # node changes first 
        num_nodes = ceil(len(g) * abs(node_change_ratio)) 
        if node_change_ratio < 0: num_nodes = -num_nodes
        
        old_nodes = sorted(g.keys()) 
        # case: pos node change  
        if num_nodes > 0: 
            new_nodes = [] 
            for _ in range(num_nodes): 
                g[self.c] = set() 
                new_nodes.append(self.c) 
                self.c += 1 

            # iterate through new nodes and make a single edge w/ the other nodes 
            for n in new_nodes: 
                i = int(self.prg()) % len(old_nodes) 
                n2 = old_nodes[i] 

                g[n2] |= {n}

                if not self.is_dsg: 
                    g[n] |= {n2} 
        # case: negative node change 
        else: 
            to_delete = prg_choose_n(old_nodes,-num_nodes,prg_,is_unique_picker=True)
            mg = MicroGraph(g) 
            g = mg.subgraph_nodeset_exclusion(to_delete).dg 

        mg = MicroGraph(g) 
        vscore,escore = mg.ve_score()
        
        num_edges = None 
        if edge_change_ratio < 0: 
            num_edges = ceil(escore * -edge_change_ratio) 
        else: 
            # NOTE: directedness of graph matters for this. 
            rem_edges = max_simple_edges(vscore) - escore 
            num_edges = ceil(rem_edges * edge_change_ratio) 

        # cases: add or delete edges 
        stat = edge_change_ratio >= 0 

        for _ in range(num_edges): 
            self.one_edge_change(g,stat)
        return g

    def one_edge_change(self,d:defaultdict,add_edge): 
        def prg_(): return int(self.prg())

        nodes = sorted(d.keys())
        nodes = prg_seqsort(nodes,prg_) 
        if add_edge: 
            for n in nodes: 
                neighbors = d[n] 
                new_neighbor_candidates = sorted(set(d.keys()) - neighbors) 
                if len(new_neighbor_candidates) == 0: continue 

                i = int(self.prg()) % len(new_neighbor_candidates) 
                neighbor = new_neighbor_candidates[i] 

                d[n] |= {neighbor} 

                if not self.is_dsg:
                    d[neighbor] |= {n} 
                return 

        for n in nodes: 
            neighbors = d[n] 
            if len(neighbors) == 0: continue 

            neighbors = sorted(neighbors)
            i = int(self.prg()) % len(neighbors)  
            neighbor = neighbors[i] 

            d[n] -= {neighbor} 

            if not self.is_dsg: 
                d[neighbor] -= {n} 
        return 

    def prng_decimal(self,output_range): 
        r0,r1 = abs(self.prg()),abs(self.prg())
        rx = sorted([r0,r1]) 
        rx = zero_div(rx[0],rx[1],0.5) 
        edge_connectivity = modulo_in_range(rx,output_range)