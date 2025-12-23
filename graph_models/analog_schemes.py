from .graph_gen import * 
from .shortest_paths import * 
from morebs2.graph_basics import * 
from morebs2.numerical_generator import prg_choose_n,prg_seqsort,modulo_in_range
from morebs2.measures import zero_div 

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

"""
transforms graph into automorphism of it using counter function 
`ctr_function`. 
"""
def graph_automorphism(G,ctr_function): 
    # make basic isomap for G 
    isomap = dict() 
    gnodes = sorted(G.keys()) 
    for gn in gnodes:
        isomap[gn] = ctr_function()

    # isotransform graph to start at current index 
    mg = MicroGraph(G) 
    G = MicroGraph.isotransform_MG(mg,isomap).dg  
    return G,isomap 

#----------------------------------------- for subgraph generation scheme #2

def shortest_paths_graph_analogue(G,start_node,num_paths_per_node,num_paths_selection,prg,ctr_function): 

    # calculate shortest paths 
    is_bfs = bool(int(prg()) % 2)
    bdfs = BDFSCache(start_node,G,is_bfs=is_bfs,prg=prg,\
        edge_cost_function=lambda u,v:1,\
        num_paths_per_node=num_paths_per_node) 
    bdfs.exec() 

    # iterate through each sequence of shortest paths and select 
    min_paths = bdfs.min_paths

    def prg_(): return int(prg())

    all_selected_paths = [] 
    for paths_seq in min_paths.values():
        lx = min([len(paths_seq),num_paths_selection])
        if lx == 0: continue 

        selected_paths = prg_choose_n(paths_seq,lx,prg_,is_unique_picker=True)
        all_selected_paths.extend(selected_paths)

    # piece NodePath instances into graph 
    G = NodePath.nodepath_set_to_graph(all_selected_paths) 
    return graph_automorphism(G,ctr_function) 

#----------------------------------------- for subgraph generation scheme #3

def one_edge_change(d:defaultdict,is_dsg:bool,add_edge:bool,prg): 
    def prg_(): return int(prg())

    nodes = sorted(d.keys())
    nodes = prg_seqsort(nodes,prg_) 
    if add_edge: 
        for n in nodes: 
            neighbors = d[n] 
            new_neighbor_candidates = sorted(set(d.keys()) - neighbors) 
            if len(new_neighbor_candidates) == 0: continue 

            i = prg_() % len(new_neighbor_candidates) 
            neighbor = new_neighbor_candidates[i] 

            d[n] |= {neighbor} 

            if not is_dsg:
                d[neighbor] |= {n} 
            return 

    for n in nodes: 
        neighbors = d[n] 
        if len(neighbors) == 0: continue 

        neighbors = sorted(neighbors)
        i = prg_() % len(neighbors)  
        neighbor = neighbors[i] 

        d[n] -= {neighbor} 

        if not is_dsg: 
            d[neighbor] -= {n}  
    return 

def graph_derivation(g:defaultdict,is_dsg:bool,node_change_ratio,edge_change_ratio,prg,ctr_function):
    def prg_(): return int(prg())

    # node changes first 
    num_nodes = ceil(len(g) * abs(node_change_ratio)) 
    if node_change_ratio < 0: num_nodes = -num_nodes
    
    old_nodes = sorted(g.keys()) 
    # case: pos node change  
    if num_nodes > 0: 
        new_nodes = [] 
        for _ in range(num_nodes): 
            x = ctr_function()
            g[x] = set() 
            new_nodes.append(x) 

        # iterate through new nodes and make a single edge w/ the other nodes 
        for n in new_nodes: 
            i = int(prg()) % len(old_nodes) 
            n2 = old_nodes[i] 

            # NOTE: constant direction of conn. 
            g[n2] |= {n}

            if not is_dsg: 
                g[n] |= {n2} 
    # case: negative node change 
    else: 
        to_delete = prg_choose_n(old_nodes,-num_nodes,prg_,is_unique_picker=True)
        mg = MicroGraph(deepcopy(g))  
        mg.subgraph_nodeset_exclusion(to_delete)
        g = mg.dg  

    mg = MicroGraph(g) 
    vscore,escore = mg.ve_score()
    if not is_dsg: 
        escore = int(escore / 2) 

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
        one_edge_change(g,is_dsg,stat,prg)

    # automorphism  
    return graph_automorphism(g,ctr_function) 

#---------------------------------------------------------------------------------------------------------

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
        self.verbose = verbose 

        # new node counter 
        self.c = max(self.d.keys()) + 1 
        self.preproc()
        self.set_counter_function() 
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
        def prg_(): return int(self.prg())


        # select prior nodes 
        r0 = self.prng_decimal([10**-5,self.sg2sg_conn_ratios[0]])
        num_nodes = ceil(r0 * len(prior_sg))
        prior_nodes = sorted(prior_sg.keys())
        selected_nodes = prg_choose_n(prior_nodes,num_nodes,prg_,is_unique_picker=True) 

        # calculate possible number of edges between prior nodes and current sg 
        r1 = self.prng_decimal([10**-5,self.sg2sg_conn_ratios[1]])
        max_edges = len(current_sg) * num_nodes
        wanted_edges = ceil(r1 * max_edges)
        current_nodes = sorted(current_sg.keys())

        # add the two graphs 
        new_sg = (MicroGraph(prior_sg) + MicroGraph(current_sg)).dg 

        # make edges between the pair of nodesets  
        for _ in range(max_edges): 
            n0 = prg_() % num_nodes 
            n1 = prg_() % len(current_nodes) 

            n0 = selected_nodes[n0] 
            n1 = current_nodes[n1] 

            node_pair = [n0,n1] if prg_() % 2 else [n1,n0] 

            new_sg[node_pair[0]] |= {node_pair[1]} 

            if not self.is_dsg: 
                new_sg[node_pair[1]] |= {node_pair[0]}  
        return new_sg 

    #--------------------- generation scheme #1 

    def prng_generate_subgraph(self): 

        is_realtime_gen = bool(int(self.prg()) % 2)
        vertex_degree = int(modulo_in_range(self.prg(),self.gen_scheme_subgraph_degree_range))
 
        edge_connectivity = self.prng_decimal(self.gen_subgraph_conn_range)
        gg = GraphGen(self.is_dsg,self.prg,is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity)
        gg.full_run() 
        return isotransform_graph(gg.d,self.ctr_function)

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

        return shortest_paths_graph_analogue(G,start_node,\
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
        edge_change = self.prng_decimal(edge_range)
        eneg = int(self.prg()) % 2
        eneg = -1 if eneg else 1 
        edge_change = eneg * edge_change 

        # get pos./neg. node change 
        node_range = [10**-5,self.gen_subgraph_derivation_ratios[1]]
        node_change = self.prng_decimal(node_range)
        nneg = int(self.prg()) % 2
        nneg = -1 if nneg else 1 
        node_change = nneg * node_change 

        return graph_derivation(G,self.is_dsg,node_change,edge_change,self.prg,self.ctr_function)[0]

    #----------------- accessory methods 

    def prng_decimal(self,output_range): 
        r0,r1 = abs(self.prg()),abs(self.prg())
        rx = sorted([r0,r1]) 
        rx = zero_div(rx[0],rx[1],0.5) 
        return modulo_in_range(rx,output_range)