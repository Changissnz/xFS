from .graph_gen import * 
from .bfs import * 
from types import MethodType,FunctionType
from math import ceil 

DEFAULT_DIRIMP_PATH_MAX_NUMPATHS_PER_NODEPAIR = 20 

"""
A directed implication path is a graph consisting of a 
a spine S, a directed path, connecting all nodes of the graph 
from head h to tail t. 

Nodes n_i of N = S - {t} can also have edges to other any other node n_j, 
given the condition that if n_i is distance x from tail t on spine S, then 
n_j is of distance x_ < x from t on S. 
"""

def tail_of_directed_implication_path(G): 
    # find the tail: out-degree (0) 
    t = None 
    c = 0 
    for k,v in G.items(): 
        if len(v) == 0: 
            c += 1 
            t = k 

    if c != 1: 
        return None 
    return t 

def head_of_directed_implication_path(G): 

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

    if c != 1: 
        return None 
    return h 



# NOTE: not designed for graphs of many nodes. 
"""
return: 
- head,tail, all paths from head to tail, ?is directed implication path? 
"""
def verify_directed_implication_path(G):  
    
    graph_childkey_fillin(G) 
    if is_undirected_graph(G): return None,None,[],False 
    if len(G) < 2: return None,None,[],False  

    # find tail 
    t = tail_of_directed_implication_path(G)     
    if type(t) == type(None): return None,None,[],False  

    # find the head 
    h = head_of_directed_implication_path(G) 
    if type(h) == type(None): 
        return None,t,[],False 

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
    bc.store_minpaths(ns=None,num_paths=DEFAULT_DIRIMP_PATH_MAX_NUMPATHS_PER_NODEPAIR,\
        cost_func=sum,prg=None) 

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

def max_extra_edges_for_directed_implication_path(num_nodes):  
    m = num_nodes - 2 
    max_edges = sum([i for i in range(1,m+1)]) 
    return max_edges 

"""
return: 
- defaultdict, graph that includes path p, along with extra edges. 
"""
def extra_edges_for_directed_path(p:NodePath,extra_edges,prg):  
    assert len(p) > 1 
    assert extra_edges >= 0  

    G = p.to_graph(is_dsg=True) 
    graph_childkey_fillin(G) 
    if extra_edges == 0: 
        return G,[] 

    nodeseq = deepcopy(p.p[:-1])  

    i = 0 
    extra_edges_ = [] 
    while i < extra_edges: 
        j = int(prg()) % len(nodeseq) 
        source_node = nodeseq[j] 

        possible_candidates = set(nodeseq[j+1:]) | {p.p[-1]}  
        possible_candidates = possible_candidates - G[source_node]

        # case: no more candidates
        if len(possible_candidates) == 0: 
            nodeseq.pop(j) 
            continue 

        possible_candidates = sorted(possible_candidates) 
        j2 = int(prg()) % len(possible_candidates) 
        target_node = possible_candidates[j2] 
        G[source_node] |= {target_node}
        extra_edges_.append((source_node,target_node)) 
        i += 1 

    return G,extra_edges_

def generate_directed_implication_path(num_nodes,extra_edge_ratio:float,prg,start_node_idn:int=0): 
    assert type(num_nodes) == int and num_nodes > 1 
    assert 0. <= extra_edge_ratio <= 1. 
    assert type(prg) in {MethodType,FunctionType} 
    assert type(start_node_idn) == int  

    # calculate number of extra edges 
    max_edges = max_extra_edges_for_directed_implication_path(num_nodes) 
    extra_edges = ceil(max_edges * extra_edge_ratio) 

    p = [i for i in range(start_node_idn,start_node_idn+num_nodes)] 
    x = [1] * (len(p) - 1)
    N = NodePath.preload(p,x)
    G,_ = extra_edges_for_directed_path(N,extra_edges,prg)
    return G 

"""
Representation of directed implication path. See top of file for description 
of this graph category. 
"""
class DirectedImplicationPath: 

    def __init__(self,G):  
        h,t,min_paths,stat = verify_directed_implication_path(G) 
        assert stat 

        self.h = h 
        self.t = t 
        self.min_paths = min_paths 
        self.G = G 
        return

    def spine(self): 
        return self.min_paths[-1] 

    """
    outputs the appropriate number of `extra edges`, defined as any 
    pair of nodes (n_i,n_j) s.t. for tail T, 
        d(n_i,T) > d(n_j,T); d := pairwise edge distance. 
    """
    def possible_extra_edges(self,extra_edge_ratio,prg):  
        max_edges = max_extra_edges_for_directed_implication_path(len(self.G))  
        extra_edges = ceil(max_edges * extra_edge_ratio) 
        _,extra_edges_ = extra_edges_for_directed_path(self.spine(),extra_edges,prg)
        return extra_edges_ 
