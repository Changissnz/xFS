from .node_path import * 
from morebs2.numerical_generator import default_std_Python_prng,prg_seqsort,prg_seqsort_ties
from morebs2.graph_basics import is_undirected_graph
from types import MethodType,FunctionType

#---------------------------------------- functions related to node eccentricities 
#---------------------------------------- NOTE: could be refactored

# TODO: relocate
"""
nodepair_path_info := defaultdict, (source node,target node) -> NodePath 

return:
- list, nodes ranked from least to greatest eccentricity
"""
def node_eccentricity_ranking(nodepair_path_info,prg=None,return_type="node"):  

    if type(prg) == type(None): 
        prg = default_std_Python_prng() 
    assert type(prg) in {MethodType,FunctionType}  
    assert return_type in {"node","all"}
    def prg_(): return int(prg())

    DX = defaultdict(float) 
    for k,v in nodepair_path_info.items(): 
        assert type(k) == tuple and len(k) == 2 

        n0,n1 = k 
        q = v.cost() if type(v) == NodePath else v 

        if q > DX[n0]:
            DX[n0] = q 
        if q > DX[n1]: 
            DX[n1] = q 

    ecc_list = [(k,v) for k,v in DX.items()] 
    ecc_list = prg_seqsort_ties(ecc_list,prg_,vf=lambda x:x[1]) 

    if return_type == "all": return ecc_list 
    return [n[0] for n in ecc_list]

# TODO: add more tests. 
"""
"""
def peripheral_node_partition(G,part1_size,part2_size,prg,nodepair_path_info=None):   
    assert type(G) == defaultdict 
    assert is_undirected_graph(G) 
    assert part1_size + part2_size <= len(G) 
    assert part1_size > 0 and part2_size > 0 
    assert type(prg) in {MethodType,FunctionType} 

    if type(nodepair_path_info) == type(None):
        nodepair_path_info,components = BDFSCache.BFS_full(G,return_type="paths",prg=prg)  
        assert len(components) == 1

    ranked_by_ecc = node_eccentricity_ranking(nodepair_path_info,prg=prg)[::-1]
    part1 = set() 
    part2 = set() 
    stat1,stat2 = True,True 

    while stat1 and stat2: 
        stat1,stat2 = len(part1) < part1_size,len(part2) < part2_size 

        # case: add pair of nodes
        if stat1 and stat2: 
            n0 = ranked_by_ecc.pop(0)  
            partx = closer_nodeset_to_node(part1,part2,n0,nodepair_path_info,prg=prg) 
            partx2 = part2 if partx == part1 else part1 
            
            partx |= {n0}

            i = most_distant_node_to_node(n0,ranked_by_ecc,nodepair_path_info,\
                return_type="index",prg=prg) 
            n1 = ranked_by_ecc.pop(i) 
            ##print("farthest to {}: {}".format(n0,n1))
            partx2 |= {n1} 

        # case: add remaining nodes to part2 XOR part1 
        elif stat1 or stat2:
            if stat2: 
                partx,partx2,partx2_size = part1,part2,part2_size 
            else: 
                partx,partx2,partx2_size = part2,part1,part1_size 

            cx = ranked_node_distances_from_nodeset(partx,ranked_by_ecc,nodepair_path_info,prg) 
            rem_nodes = partx2_size - len(partx2) 
            new_nodes = cx[-rem_nodes:]
            new_nodes = [c[0] for c in new_nodes] 
            partx2 |= set(new_nodes)
        else: 
            continue 
    return part1,part2  

# aux method for <peripheral_node_partition>
def most_distant_node_to_node(ref_node,candidate_nodeseq,nodepair_path_info,\
    return_type="index",prg=None): 

    assert return_type in {"index","node"} 
    if type(prg) == type(None): 
        prg = default_std_Python_prng() 
    assert type(prg) in {MethodType,FunctionType}

    # get the relevant node pairs 
    relevant_nodepairs = [(ref_node,c) for c in candidate_nodeseq] 

    most_distant_node,max_distance,j = None,0,-1 
    for (i,pair) in enumerate(relevant_nodepairs):
        #? 
        if pair not in nodepair_path_info: continue 

        p = nodepair_path_info[pair]
        c = p.cost() if type(p) == NodePath else p

        if c == max_distance: 
            if int(prg()) % 2: 
                most_distant_node = pair[1]
                max_distance = c 
                j = i 
        elif c > max_distance: 
            most_distant_node = pair[1]
            max_distance = c 
            j = i 
    
    if return_type == "index": return j 
    return most_distant_node

def average_distance(nodeset,ref_node,nodepair_path_info):
    if len(nodeset) == 0: return float('inf')

    q = [] 
    for n in nodeset: 
        if (ref_node,n) not in nodepair_path_info: 
            continue 

        p = nodepair_path_info[(ref_node,n)]         
        c = p.cost() if type(p) == NodePath else p 
        q.append(c) 
    if len(q) == 0: return float('inf') 
    return np.mean(q) 

"""
determines which nodeset 1 XOR 2 is closer in average distance to `ref_node`
"""
def closer_nodeset_to_node(nodeset1,nodeset2,ref_node,nodepair_path_info,prg=None):

    if type(prg) == type(None): 
        prg = default_std_Python_prng() 
    assert type(prg) in {MethodType,FunctionType}

    if len(nodeset1) == 0: 
        return nodeset1 
    
    if len(nodeset2) == 0: 
        return nodeset2 

    D1 = average_distance(nodeset1,ref_node,nodepair_path_info) 
    D2 = average_distance(nodeset2,ref_node,nodepair_path_info)   

    if D1 == D2: 
        if int(prg()) % 2: return nodeset1 
        return nodeset2 
    
    if D1 < D2: 
        return nodeset1 
    return nodeset2 

"""
ranks nodes of `candidate_nodeseq` from least to greatest average distance to `ref_nodeset`. 
"""
def ranked_node_distances_from_nodeset(ref_nodeset,candidate_nodeseq,nodepair_path_info,prg=None):

    if len(ref_nodeset) == 0 or len(candidate_nodeseq) == 0: return None 

    if type(prg) == type(None): 
        prg = default_std_Python_prng() 
    assert type(prg) in {MethodType,FunctionType}
    def prg_(): return int(prg())

    cx = [] 
    for c in candidate_nodeseq: 
        dx = average_distance(ref_nodeset,c,nodepair_path_info) 
        cx.append((c,dx)) 

    cx = prg_seqsort_ties(cx,prg,lambda x:x[1])
    return cx 

#-------------------------------------------------------------------------------------------------

"""
designed for use with bigger graphs (> 50 nodes).
"""
class BDFSCache(XFSCache):

    def __init__(self,start_node,d:defaultdict,is_bfs:bool=True,prg=None,\
        edge_cost_function=lambda u,v:1,num_paths_per_node=10,max_search_radius=float('inf'),\
        verbose=False):  

        super().__init__(start_node,d,edge_cost_function,None)

        assert type(is_bfs) == bool 
        self.is_bfs = is_bfs 

        if type(prg) == type(None): 
            prg = default_std_Python_prng()

        assert type(prg) in {MethodType,FunctionType} 
        assert type(num_paths_per_node) == int and num_paths_per_node > 0 
        assert type(max_search_radius) in {int,float} and max_search_radius > 0. 

        self.prg = prg 

        self.min_paths[self.reference] = [NodePath(self.reference)] 
        self.num_paths_per_node = num_paths_per_node 
        self.max_search_radius = max_search_radius
        self.verbose = verbose 

    """
    return: 
    - (source node, target node) -> path|distance between them 
    - components, list of sets 
    """
    @staticmethod 
    def BFS_full(G:defaultdict,return_type="distance",prg=None,max_search_radius=float('inf'),\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False):  
        assert return_type in {"distance","paths"} 

        if type(prg) == type(None): 
            prg = default_std_Python_prng()

        is_directed = not is_undirected_graph(G) 

        paths_info = {} 
        components = [] 

        def one_bfs(start_node):
            if verbose: print("breadth-first search from node ",start_node) 
            bc = BDFSCache(start_node,G,is_bfs=True,prg=prg,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,num_paths_per_node=1,\
                max_search_radius=max_search_radius,verbose=verbose)
            bc.exec() 

            for k,paths in bc.min_paths.items():
                q = paths[0] 
                if return_type == "distance": 
                    q = q.cost() 

                paths_info[(start_node,k)] = q 
                if not is_directed: 
                    if return_type == "paths": 
                        paths_info[(k,start_node)] = q.invert() 
                    else: 
                        paths_info[(k,start_node)] = q 

            component = set(bc.min_paths.keys()) | {start_node} 
            if component not in components: 
                components.append(component) 

        nodeset = sorted(G.keys())
        for s in nodeset: 
            one_bfs(s) 
        return paths_info, components

    def move_one(self): 
        def prg_(): return int(self.prg())

        self.previous_edges.clear() 

        if type(self.reference) == type(None): 
            return False 

        if self.verbose: print("queue length: ",len(self.reference_varcache))

        # get untravelled nodes 
        untravelled = self.d[self.reference] - self.ref_neighbors_travelled[self.reference] 
        untravelled = sorted(untravelled) 

        if len(untravelled) == 0: 
            self.reference = None 
            if len(self.reference_varcache) == 0: 
                return False 

            self.reference = self.reference_varcache.pop(0)
            return True 

        if self.is_bfs: 
            max_distance_reached = [] 
            for n in untravelled: 
                new_paths = self.add_node_to_prev_min_paths(self.reference,n)
                stat_vec = self.insert_new_paths(n,new_paths)
                ##print("LEN ",stat_vec,len(new_paths))

                if len(stat_vec) > 0 and True not in stat_vec: 
                    max_distance_reached.append(n)

            untravelled = set(untravelled) - set(max_distance_reached)
        else: 
            # choose a node 
            ni = int(self.prg()) % len(untravelled)
            node = untravelled.pop(ni)

            new_paths = self.add_node_to_prev_min_paths(self.reference,node) 
            stat_vec = self.insert_new_paths(node,new_paths) 
            ##print("LEN2: ",stat_vec)

            if len(stat_vec) > 0 and True not in stat_vec: 
                untravelled = set() 
            else: 
                untravelled = set([node]) 
            
        self.ref_neighbors_travelled[self.reference] |= untravelled
        untravelled = prg_seqsort(sorted(untravelled),prg_)

        self.previous_edges = [(self.reference,n) for n in untravelled] 

        self.reference_varcache.extend(untravelled) 

        if self.verbose: 
            print("ref {}, edges travelled {}".format(self.reference,len(untravelled)))

        if self.is_bfs: 
            if len(self.reference_varcache) > 0: 
                self.reference = self.reference_varcache.pop(0)
            else: 
                return False 
        else: 
            if len(untravelled) == 0: 
                if len(self.reference_varcache) == 0: 
                    return False 
                self.reference = self.reference_varcache.pop(-1) 

        return True 

    """
    return:
    - each path of previous node `prev` extended with `node`. 
    """
    def add_node_to_prev_min_paths(self,prev,node): 
        prev_paths = self.min_paths[prev]
        cost = self.ecf(prev,node)

        paths = [] 
        for p in prev_paths: 
            new_path = p + (node,cost) 
            paths.append(new_path)
        return paths 

    def insert_new_paths(self,node,new_paths): 

        def insert_one(path): 
            cost = path.cost() 
            if cost > self.max_search_radius: 
                return False 

            # iterate through paths of node to sort it 
            node_paths = self.min_paths[node] 
            for j,p in enumerate(node_paths): 
                cost2 = p.cost() 
                if cost <= cost2: 
                    node_paths.insert(j,path)  
                    return True 
            
            node_paths.insert(len(node_paths),path) 
            return True 

        stat_vec = [] 
        for p in new_paths:
            stat = insert_one(p) 
            stat_vec.append(stat) 

        node_paths = self.min_paths[node] 
        while len(node_paths) > self.num_paths_per_node: 
            node_paths.pop(-1)
        return stat_vec 