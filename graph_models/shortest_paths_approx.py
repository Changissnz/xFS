from .shortest_paths import * 
from .micrograph import * 
from morebs2.graph_basics import flatten_setseq
from math import ceil 

# TODO: work in progress. More testing needed. 
"""
Approximates shortest paths for graphs. Useful for finding paths between connected 
nodes in large graphs (>= 1000 nodes).  

NOTE: designed for only undirected graphs
"""
class ShortestPathsApproximator: 

    def __init__(self,G:defaultdict,is_dfs:bool,max_subgraph_radius,prg,max_periphery=50,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False): 
        assert type(G) == defaultdict 
        assert type(is_dfs) == bool 
        assert max_subgraph_radius > 0
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}
        assert type(edge_cost_function) in {MethodType,FunctionType}

        self.G = G 
        ##assert not is_undirected_graph(self.G) 
        self.is_dfs = is_dfs 
        self.max_subgraph_radius = max_subgraph_radius 
        self.prg = prg 
        self.max_periphery = max_periphery
        self.edge_cost_function = edge_cost_function
        self.verbose = verbose 
        self.subgraph_nodeset_map = defaultdict(set) 

        self.preproc() 
        self.next_ref_queue = [] 
        self.fin_stat = False 
        return 

    """
    instantiate relevant variables to store subgraph data 
    """
    def preproc(self): 
        self.covered_nodes = set() 

        K = sorted(self.G.keys()) 
        i = int(self.prg())  % len(K)
        self.ref_node = K[i]
        self.ref_sg_parent = None 

        # (source node,target node) -> path 
        self.nodepair_path_info = dict() 
        # 
        self.covered_nodes = set()
        self.subgraph_nodesets = []
        self.subgraph_heads = [] 
        # subgraph idn -> parent subgraph idn 
        self.subgraph_parent_map = dict()
        return

    @staticmethod 
    def default_shortest_paths_search(G,prg): 
        assert type(G) == defaultdict 
        l = len(G)  

        R = None 
        if l <= 100: 
            R = 2 
        if l <= 1000: 
            R = 5 
        if l <= 10000:
            R = 50 
        else: 
            R = 122 

        spa = ShortestPathsApproximator(G,is_dfs=bool(int(prg())%2),max_subgraph_radius=R,prg=prg)
        spa.exec() 
        spa.add_12000_new_paths() 
        return spa 

    def add_12000_new_paths(self): 
        for i in range(12): 
            self.add_new_paths_to_info(1000) 

    """
    main method #1 

    calculates and stores every subgraph 
    """
    def exec(self): 
        while not self.fin_stat: 
            if self.verbose: print("REF: node={},subgraph={}".format(self.ref_node,self.ref_sg_parent))
            next(self) 
            if self.verbose: print()


    def __next__(self): 
        if self.fin_stat: return 

        if type(self.ref_node) == type(None): 
            self.fin_stat = True 
            return 
        
        self.subgraph_proc() 
        self.ref_node,self.ref_sg_parent = None,None 
        
        if self.verbose: print("queue size: ",len(self.next_ref_queue))

        if len(self.next_ref_queue) > 0: 
            q = self.next_ref_queue.pop(0)
            self.ref_node = q[0]
            self.ref_sg_parent = q[1]
        else: 
            S = sorted(set(self.G.keys()) - self.covered_nodes) 
            if len(S) > 0: 
                i = int(self.prg()) % len(S) 
                self.ref_node = S[i] 
                self.ref_sg_parent = None 

    """
    stores data from method<shortest_paths_from_ref> on `ref_node`. 
    """
    def subgraph_proc(self): 
        exclusive_index = 0 if type(self.ref_sg_parent) == type(None) else \
            self.ref_sg_parent
        nodepair_path_info,subgraph_nodeset,peripheral_nodes = \
            self.shortest_paths_from_ref(self.ref_node,exclusive_index)
        
        self.covered_nodes |= subgraph_nodeset         
        if len(subgraph_nodeset) == 1: 
            return 

        self.nodepair_path_info.update(nodepair_path_info)

        l = len(self.subgraph_nodesets)  
        if subgraph_nodeset in self.subgraph_nodesets: 
            return 
        self.subgraph_heads.append(self.ref_node)
        self.subgraph_nodesets.append(subgraph_nodeset)
        self.subgraph_parent_map[l] = self.ref_sg_parent 
        peripheral_nodes = prg_seqsort(peripheral_nodes,self.prg)
        
        ##?? 
        peripheral_parent_nodes = [(p,l) for p in peripheral_nodes] 
        self.next_ref_queue.extend(peripheral_parent_nodes) 

    """
    calculates shortest paths from reference node. All paths cannot 
    exceed `max_subgraph_radius`. 
    """
    def shortest_paths_from_ref(self,ref_node,exclusive_index): 
        nodepair_path_info = self.bdfs_on_node(ref_node,exclusive_index) 
        if len(nodepair_path_info) == 1: 
            return nodepair_path_info,{ref_node},set()

        ranked_nodes = node_eccentricity_ranking(nodepair_path_info,prg=self.prg,return_type="all")[::-1]
        if self.verbose: print("# of connected nodes: ",len(ranked_nodes))

        q = ranked_nodes.pop(0)
        peripheral_nodes = [q[0]] 
        l = q[1] 

        while len(ranked_nodes) > 0: 
            q = ranked_nodes.pop(0) 
            if q[1] == l: 
                peripheral_nodes.append(q[0]) 
            else: 
                break 

        for (i,x) in enumerate(peripheral_nodes): 
            if x == ref_node: 
                peripheral_nodes.pop(i) 
                break 

        if self.verbose: print("# of peripheral nodes: ",len(peripheral_nodes))

        subgraph_nodeset = set([x[1] for x in nodepair_path_info.keys()]) 
        return nodepair_path_info,subgraph_nodeset,peripheral_nodes[:self.max_periphery]

    def bdfs_on_node(self,ref_node,exclusive_index):  
        relevant_nodeset = flatten_setseq(self.subgraph_nodesets[:exclusive_index+1]) 
        mg = MicroGraph(deepcopy(self.G))
        mg.subgraph_nodeset_exclusion(relevant_nodeset - {ref_node})
        D = mg.dg 

        bdfs = BDFSCache(ref_node,D,is_bfs=not self.is_dfs,\
            prg=self.prg,edge_cost_function=self.edge_cost_function,num_paths_per_node=1,\
            max_search_radius=self.max_subgraph_radius) 
        bdfs.exec() 

        Q = bdfs.min_paths
        ks = set(Q.keys()) 
        for k in ks: 
            if len(Q[k]) == 0: 
                del Q[k]
        return {(ref_node,k):v[0] for k,v in Q.items()} 

    #------------------------------------------------------------------------------------------

    """
    main method #2 

    approximation of shortest path using direct subgraph-to-subgraph 
    tracing. 
    """ 
    def paths(self,source,target): 
        ps = self.paths_(source,target) 
        if len(ps) > 0: return ps

        ps = self.paths_(target,source) 
        return [p.invert() for p in ps]  

    def paths_(self,source,target): 

        # fetch all subgraph indices of target 
        subgraph_indices = self.subgraph_indices_of_node(target)
        assert len(subgraph_indices) > 0 

        # get the subgraph path 
        ps = [] 
        for x in subgraph_indices: 
            sp,stat = self.subgraph_path(source,target,x)
            if not stat: continue 
            p = self.peripheral_trace(target,source,sp)  
            if type(p) != type(None): 
                ps.append(p.invert())
        return ps 

    def subgraph_indices_of_node(self,n): 
        return [i for (i,s) in enumerate(self.subgraph_nodesets) if n in s] 

    #-------------------------------------------------------------------------------------------

    """
    main method #3 

    approximation of shortest path using intermediary subgraph-to-subgraph 
    tracing. 
    """ 
    def deduce_path(self,source,target): 
        KS = prg_seqsort(sorted(self.G.keys() - {source,target}),\
            self.prg)
        
        def merge_paths(px0,px1):  
            P = [] 
            for p0 in px0: 
                for p1 in px1: 
                    p_ = deepcopy(p0)
                    p_.add_path(p1) 
                    P.append(p_)
            return P 

        for k in KS: 
            p0 = self.paths(source,k)
            if len(p0) == 0: continue 
            p1 = self.paths(k,target) 
            if len(p1) == 0: continue 
            return merge_paths(p0,p1) 
        return [] 
    
    #---------------------------------- auxiliary methods for shortest paths approximation 

    """
    return:
    - list(subgraphs from target to source), ?direct subgraph-to-subgraph possible? 
    """
    def subgraph_path(self,source,target,subgraph_index): 
        assert target in self.subgraph_nodesets[subgraph_index]

        subgraph_seq = [subgraph_index] 

        while True: 

            # check parent subgraph
            x = subgraph_seq[-1]
            if type(x) == type(None): 
                return subgraph_seq,False 

            if source in self.subgraph_nodesets[x]: 
                break 

            psg = self.subgraph_parent_map[x] 
            subgraph_seq.append(psg) 
        return subgraph_seq,True 

    """
    merges subpaths from subgraphs of `subgraph_seq` to
    obtain a path from `target` to `source`. 
    """
    def peripheral_trace(self,target,source,subgraph_seq): 
        T = target 
        px = NodePath(T)
        for i in range(len(subgraph_seq) - 1): 
            x0,x1 = subgraph_seq[i],subgraph_seq[i+1] 
            sg0,sg1 = self.subgraph_nodesets[x0],self.subgraph_nodesets[x1]
            possible = sg0.intersection(sg1) 

            # case: target not connected to next subgraph 
            #       move to the closest node in `possible`
            if T not in possible:
                P = self.shortest_internal_path_to_peripheral(T,possible,x0)
                if type(P) == type(None): return 
                px.add_path(P) 
            #
            T = px.tail() 

        if px.tail() != source: 
            p = self.internal_path(px.tail(),source,subgraph_seq[-1]) 
            px.add_path(p)
        return px

    """
    finds a shortest path between `source` and one of the nodes in `target_nodeset`
    """
    def shortest_internal_path_to_peripheral(self,source,target_nodeset,subgraph_index): 
        p,d = None,float('inf')
        for t in target_nodeset:
            P = self.internal_path(source,t,subgraph_index)
            if P.cost() < d: 
                p = P 
                d = P.cost() 
        return p 

    """
    calculates a path between `source` and `target`
    """
    def internal_path(self,source,target,subgraph_index): 
        x0 = self.subgraph_nodesets[subgraph_index]
        assert source in x0 and target in x0 
        h0 = self.subgraph_heads[subgraph_index]
        p = self.nodepair_path_info[(h0,source)].invert()

        if target in p.p: 
            i = p.p.index(target)
            new_p = p.p[:i+1] 
            new_w = p.pweights[:i] 
            return NodePath.preload(new_p,new_w) 

        p.add_path(self.nodepair_path_info[(h0,target)]) 
        return p 

    def add_new_paths_to_info(self,max_num_paths):  
        nodes = prg_seqsort(sorted(self.G.keys()),self.prg)  

        q = ceil(max_num_paths * 0.1) 
        c = 0 

        for n in nodes:  
            if c >= max_num_paths: break 
            c_ = min([max_num_paths,c + q]) 
            num_paths = c_ - c 
            new_paths = self.add_new_paths_to_info_(n,num_paths)
            c += new_paths 
        return 

    def add_new_paths_to_info_(self,n,max_num_paths): 
        c = 0 
        for x in self.G: 
            if c >= max_num_paths: 
                break 
            if (n,x) not in self.nodepair_path_info: 
                p = self.paths(n,x) 
                if len(p) != 0:
                    qi = np.argmin([p_.cost() for p_ in p]) 
                    self.nodepair_path_info[(n,x)] = p[qi]
                    c += 1 
                    continue 
                
                p = self.deduce_path(n,x) 
                if len(p) != 0:
                    qi = np.argmin([p_.cost() for p_ in p]) 
                    self.nodepair_path_info[(n,x)] = p[qi]
                    c += 1 
                    continue 
        return c 
