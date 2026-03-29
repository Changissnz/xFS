"""
auxiliary methods for file<analog_schemes>. 
Focused on graph derivation. 
"""

from .tree_gen import * 
from .graph_gen import * 
from .shortest_paths_approx import * 
from morebs2.numerical_generator import prg_choose_n,prg_seqsort,modulo_in_range,prg_decimal
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

def shortest_paths_graph_analogue(G,start_node,is_dsg,num_paths_per_node,num_paths_selection,prg,ctr_function): 
    # calculate shortest paths 
    if len(G) <= 75: 
        is_bfs = bool(int(prg()) % 2)
        bdfs = BDFSCache(start_node,G,is_bfs=is_bfs,prg=prg,\
            edge_cost_function=lambda u,v:1,\
            num_paths_per_node=num_paths_per_node) 
        bdfs.exec() 
        min_paths = bdfs.min_paths
        min_paths_ = [] 
        for v in min_paths.values(): min_paths_.extend(v) 
    else: 
        spa = ShortestPathsApproximator.default_shortest_paths_search(G,prg) 
        min_paths = spa.nodepair_path_info
        min_paths_ = list(min_paths.values())

    # iterate through each sequence of shortest paths and select 
    prg_ = prg__single_to_int(prg,False)

    all_selected_paths = None 

    if num_paths_selection >= len(min_paths_): 
        all_selected_paths = min_paths_ 
    else: 
        all_selected_paths = prg_choose_n(min_paths_,num_paths_selection,prg_,is_unique_picker=True)

    # piece NodePath instances into graph 
    G = NodePath.nodepath_set_to_graph(all_selected_paths,is_dsg) 
    return graph_automorphism(G,ctr_function) 

#----------------------------------------- for subgraph generation scheme #3

def one_edge_change(d:defaultdict,is_dsg:bool,add_edge:bool,prg): 
    prg_ = prg__single_to_int(prg,False)

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
    return 

"""
adds or deletes nodes for graph g. 
"""
def node_changes_to_graph(g:default_dict,is_dsg,num_nodes,prg,ctr_function): 

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
        to_delete = prg_choose_n(old_nodes,-num_nodes,prg,is_unique_picker=True)
        mg = MicroGraph(deepcopy(g))  
        mg.subgraph_nodeset_exclusion(to_delete)
        g = mg.dg  

    return g 

# NOTE: new nodes will always be connected to at least 1 node in reference graph `g`.
def graph_derivation(g:defaultdict,is_dsg:bool,node_change_ratio,edge_change_ratio,prg,ctr_function,\
    max_edge_changes=float('inf')):
    
    prg_ = prg__single_to_int(prg,False) 

    # node changes first 
    num_nodes = ceil(len(g) * abs(node_change_ratio)) 
    if node_change_ratio < 0: num_nodes = -num_nodes

    g = node_changes_to_graph(g,is_dsg,num_nodes,prg_,ctr_function) 

    mg = MicroGraph(g) 
    vscore,escore = mg.ve_score()
    if not is_dsg: 
        escore = int(escore / 2) 

    num_edges = None 
    if edge_change_ratio < 0: 
        num_edges = ceil(escore * -edge_change_ratio) 
    else: 
        # NOTE: directedness of graph matters for this.
        rem_edges = max_simple_edges(vscore)
        rem_edges = int(rem_edges / 2) if not is_dsg else rem_edges 
        rem_edges -= escore 
        num_edges = ceil(rem_edges * edge_change_ratio) 

    num_edges = min([num_edges,max_edge_changes])

    # cases: add or delete edges 
    stat = edge_change_ratio >= 0 
    for _ in range(num_edges):
        one_edge_change(g,is_dsg,stat,prg)

    # automorphism  
    return graph_automorphism(g,ctr_function) 

#---------------------------------------------- subgraph-to-subgraph connection

# NOTE: scheme ensures every node of current_sg connected to at least one node in 
#       prior_sg 
def connect_subgraphs__prior_to_current(prior_sg:defaultdict,current_sg:defaultdict,\
    is_dsg:bool,sg2sg_conn_ratios,prg): 

    assert 0. <= sg2sg_conn_ratios[0] <= 1.
    assert 0. <= sg2sg_conn_ratios[1] <= 1.

    prg_ = prg__single_to_int(prg,False)

    # select prior nodes 
    rx = sorted([0.08,sg2sg_conn_ratios[0]])
    r0 = prg_decimal(prg,rx)
    num_nodes = ceil(r0 * len(prior_sg))
    prior_nodes = sorted(prior_sg.keys())
    selected_nodes = prg_choose_n(prior_nodes,num_nodes,prg_,is_unique_picker=True) 

    # calculate possible number of edges between prior nodes and current sg 
    current_nodes = sorted(current_sg.keys())

    # add the two graphs 
    new_sg = (MicroGraph(prior_sg) + MicroGraph(current_sg)).dg 

    # connect the two graphs first, node by node 
    for c in current_nodes: 
        n0 = prg_() % len(selected_nodes) 
        n0 = selected_nodes[n0] 

        if is_dsg: 
            if prg_() % 2: 
                new_sg[n0] |= {c}
            else: 
                new_sg[c] |= {n0} 
        else: 
            new_sg[n0] |= {c} 
            new_sg[c] |= {n0} 

    rx = sorted([0.08,sg2sg_conn_ratios[1]])
    r1 = prg_decimal(prg,rx)
    max_edges = len(current_sg) * num_nodes
    if not is_dsg: 
        max_edges = int(max_edges * 2) 
    max_edges -= len(current_nodes)
    wanted_edges = ceil(r1 * max_edges)

    # make edges between the pair of nodesets  
    for _ in range(max_edges): 
        n0 = prg_() % num_nodes 
        n1 = prg_() % len(current_nodes) 

        n0 = selected_nodes[n0] 
        n1 = current_nodes[n1] 

        node_pair = [n0,n1] if prg_() % 2 else [n1,n0] 

        new_sg[node_pair[0]] |= {node_pair[1]} 

        if not is_dsg: 
            new_sg[node_pair[1]] |= {node_pair[0]}  
    return new_sg 

#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------

# method for checking generative scheme #2 
def check_for_shortest_paths_of_isomorphic_subgraph(supergraph,subgraph,super2sub_nodemap,\
    num_paths_per_node,prg): 
    
    sub2super_nodemap = {v:k for k,v in super2sub_nodemap.items()} 

    # conduct BFS on min keys for each of supergraph,subgraph. 
    super_key = min(supergraph.keys())
    sub_key = super2sub_nodemap[super_key] 

    bdfs = BDFSCache(super_key,supergraph,is_bfs=True,num_paths_per_node=num_paths_per_node,prg=prg) 
    bdfs.exec() 
    bdfs2 = BDFSCache(sub_key,subgraph,is_bfs=True,num_paths_per_node=num_paths_per_node,prg=prg)  
    bdfs2.exec()

    count = 0 
    for k,paths in bdfs2.min_paths.items(): 

        for p in paths: 
            p2 = [sub2super_nodemap[p_] for p_ in p.p] 
            stat = False 
            x2 = bdfs.min_paths[p2[-1]] 
            for x2_ in x2: 
                if x2_.p == p2: 
                    stat = True 
                    break 
            count += int(stat)

            if stat: break 
    return count