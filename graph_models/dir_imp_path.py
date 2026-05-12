from .graph_gen import * 
from .bfs import * 
from types import MethodType,FunctionType
from math import ceil 

"""
A directed implication path is a graph consisting of a 
a spine S, a directed path, connecting all nodes of the graph 
from head h to tail t. 

Nodes n_i of N = S - {t} can also have edges to other any other node n_j, 
given the condition that if n_i is distance x from tail t on spine S, then 
n_j is of distance x_ < x from t on S. 
"""

# NOTE: not designed for graphs of many nodes. 
"""
return: 
- head,tail, all paths from head to tail, ?is directed implication path? 
"""
def verify_directed_implication_path(G):  
    
    graph_childkey_fillin(G) 
    if is_undirected_graph(G): return None,None,[],False 
    if len(G) < 2: return None,None,[],False  

    # find the tail: out-degree (0) 
    t = None 
    c = 0 
    for k,v in G.items(): 
        if len(v) == 0: 
            c += 1 
            t = k 
    
    if c != 1: return None,None,[],False  

    # find the head 
    h = None 
    keys = set(G.keys()) 
    c = 0  
    for k_ in keys: 
        stat = False 
        for k,v in G.items(): 
            if k_ in v:
                stat = True   
                break 

        if not stat: 
            h = k_ 
            c += 1  

    if c != 1: return None,t,[],False 
    # make sure no two nodes n0,n1 can have both edges (n0,n1) and (n1,n0) 
    for k,v in G.items(): 
        for v_ in v:
            if k in G[v_]: 
                return None,t,[],False 

    # do a shortest path search 
    bc = BFSCache(start_node=h,d=G,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None,no_duplicate_touch_nodes=False) 
    bc.exec() 
    bc.store_minpaths(ns=None,num_paths=float('inf'),cost_func=sum,prg=None) 

    # get the longest path from head to tail, and make sure path includes all 
    # nodes of G. 
    q = bc.min_paths[t][-1].invert().p 
    nodeset = set(q)  

    if nodeset != set(G.keys()): 
        return h,t,[],False 
    for (i,q_) in enumerate(q) : 
        x = set(q[:i]) 
        if G[q_].intersection(x) != set(): 
            return h,t,[],False 

    return h,t,[p.invert() for p in bc.min_paths[t]],True 

def generate_directed_implication_path(num_nodes,extra_edge_ratio:float,prg,start_node_idn:int=0): 
    assert type(num_nodes) == int and num_nodes > 1 
    assert 0. <= extra_edge_ratio <= 1. 
    assert type(prg) in {MethodType,FunctionType} 
    assert type(start_node_idn) == int  

    # calculate number of extra edges 
    m = num_nodes - 2 
    max_edges = sum([i for i in range(1,m+1)]) 
    extra_edges = ceil(max_edges * extra_edge_ratio) 

    # calculate spine of graph 
    G = generate_graph__path(num_nodes,start_node_idn,is_dsg=True) 
    graph_childkey_fillin(G) 
    nodeseq = [i for i in range(start_node_idn,start_node_idn + num_nodes - 1)]  
    i = 0 
    while i < extra_edges: 
        j = int(prg()) % len(nodeseq) 
        source_node = nodeseq[j] 

        possible_candidates = set(nodeseq[j+1:]) | {start_node_idn + num_nodes - 1} 
        possible_candidates = possible_candidates - G[source_node]

        # case: no more candidates
        if len(possible_candidates) == 0: 
            nodeseq.pop(j) 
            continue 

        possible_candidates = sorted(possible_candidates) 
        j2 = int(prg()) % len(possible_candidates) 
        target_node = possible_candidates[j2] 
        G[source_node] |= {target_node}
        i += 1 
    return G 

class DirectedImplicationPath: 

    def __init__(self,G):  
        h,t,min_paths,stat = verify_directed_implication_path(G) 
        assert stat 

        self.h = h 
        self.t = t 
        self.min_paths = min_paths 
        self.G = G 
        return
