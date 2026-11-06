from .node_path import * 
from .graph_gen import * 
from morebs2.matrix_methods import is_number
from morebs2.numerical_generator import safe_modulo_in_range,\
    prg_decimal,safe_prg_decimal,prg_partition_for_sz__n_rounds,prg_choose_n
from math import floor 

'''
Storage container and operator for Directed Acyclic Graphs. Stores 
nodesets per DAG `level`. Calculates proper children and parents 
of any arbitrary node of DAG. Proper children/parent nodes of 
a node `n` cannot be at the same level as `n`. 

NOTE: the terms `level` and `layer` are interchangeable, and are 
integers assigned to nodes that signify their minimum distances from 
the root node/s. 

Calculates any variable k' <= k number of paths that have node `n` 
of `G` in them. Paths can be proper paths or non-proper paths. Every 
node of a proper path P, s.t |P| > 1, is a proper child and/or proper 
parent node. Non-proper paths include source/target nodes that are at 
the same level as the reference nodes. 

NOTE: verification process also checks for circularity of layers. 
      This checking process is not suited for graphs with layers of 
      large size for the calculation ( > 50 nodes).
'''
class DAGraphContainer: 

    def __init__(self,G,l2n_map,check_input_graph:bool=True):
        assert type(G) == defaultdict 
        assert type(l2n_map) == dict 
        
        nodeset = set() 
        for k,v in l2n_map.items(): 
            assert type(k) == int and k >= 0 
            assert type(v) == set 
            nodeset |= v 
        nodeset2 = set(G.keys())
        assert nodeset == nodeset2, "diff of {}".format((nodeset - nodeset2) | (nodeset2 - nodeset)) 

        self.G = G 
        self.G_ = None 
        # reversed edges of `G`; used for quicker lookup of parent nodes
        self.G_rev = reverse_graph_edges(deepcopy(self.G))
        self.l2n_map = l2n_map 

        # path traversal cache + queue, 
        # used for method<n_paths_with_node>. 
        #   element := (NodePath, ?finished head?, ?finished tail?)
        self.ptrav_queue = deque()
        self.ptrav_cache = deque() 

        # extra queue used for calculating paths that require nodesets 
        self.ptrav_queue2 = deque() 

        self.erroneous_node = None 
        if check_input_graph: 
            self.verify()
            self.G_ = None 

        # status for calculating paths that include required nodeset 
        self.trav_error = False 
        return

    def add_edge(self,source,target):
        self.G[source] |= {target} 
        self.G_rev[target] |= {source}  

    def parents_of_node(self,n,is_proper:bool=True):  
        assert type(is_proper) == bool 

        q = children_of(self.G_rev,n) 
        if not is_proper: return q 

        l = self.node_to_level(n) 
        return q - self.l2n_map[l]

    def children_of_node(self,n,is_proper:bool=True): 
        assert type(is_proper) == bool 

        q = children_of(self.G,n) 
        if not is_proper: return q 

        l = self.node_to_level(n) 
        return q - self.l2n_map[l]  

    """
    A 'sibling' of `n` is a node at the same level as `n`, 
    one with either an edge to `n` (older sibling) or from `n` (younger sibling).  
    """
    def siblings_of_node(self,n,is_older:bool):
        assert type(is_older) == bool 

        if is_older: 
            P0 = self.parents_of_node(n,False) 
            P = self.parents_of_node(n,True) 
            return P0 - P 

        C0 = self.children_of_node(n,False) 
        C = self.children_of_node(n,True) 
        return C0 - C 

    def node_to_level(self,n): 
        for l,v in self.l2n_map.items(): 
            if n in v: return l 
        return -1 

    def level_to_nodeset(self,l): 
        if l not in self.l2n_map: 
            return None 
        return deepcopy(self.l2n_map[l])

    def leaf_nodeset(self): 
        l = sorted(self.l2n_map.keys()) 

        if len(l) == 0: return None 
        return deepcopy(self.l2n_map[l[-1]])

    #------------------------- intralayer edge operations 

    # NOTE: caution. Do NOT exceed size of 50 nodes or 
    #       so. Computation uses <GraphComponentDecomposition>, 
    #       not of the most efficient process. 
    # NOTE: also performs assertion of no circularity within 
    #       layer. 
    def intrasets_of_layer(self,l): 
        s = deepcopy(self.l2n_map[l])
        if len(s) == 0: return [] 

        M = MicroGraph(self.G) 
        M2 = M.subgraph_by_nodeset_(s) 

        g = GraphComponentDecomposition(M2.dg) 
        g.decompose() 

        assert len(g.cyclic_keys) == 0 
        if type(g.components[0]) == set: 
            return g.components 
        return [flatten_setseq(q) for q in g.components]

    def intralayer_edges(self,l): 
        N = self.l2n_map[l] 
        edges = []
        for n in N: 
            q = self.G[n].intersection(N)
            edges.extend([(n,q_) for q_ in q]) 
        return edges 

    def clear_intralayer_edges(self,l): 
        nodeset = self.l2n_map[l]

        for n in nodeset: 
            self.G[n] = self.G[n] - nodeset 
        return 

    #-------------------------------------- path operations  

    ##------------------- full paths (from roots to leaves) 

    """
    proper_paths_only := if set to True, every path has at most one 
        node per level. Otherwise, output paths vary in length according 
        to 
    """
    def n_paths_with_node(self,node,num_paths,proper_paths_only:bool=True,prg=None): 
        assert type(proper_paths_only) == bool 

        if node not in self.G: 
            return []  

        N = NodePath(node) 
        return self.run_full_traversal(N,num_paths,proper_paths_only,prg)  

    """
    calculates p < `num_paths` that include `nodeset`, every node of `nodeset` 
    being of the same level. 
    """
    def n_paths_with_intra_nodeset(self,nodeset,num_paths,proper_paths_only:bool=True,prg=None): 

        P = self.intralayer_nodeset_path(nodeset,prg)

        if type(P) == type(None): 
            return [] 

        return self.run_full_traversal(P,num_paths,proper_paths_only,prg) 

    """
    calculates p < `num_paths` that include every node from arbitrary `nodeset`.
    """
    def n_paths_with_nodeset(self,nodeset,num_paths,proper_paths_only:bool=True,prg=None): 
        
        if len(nodeset) == 0: return None 

        n2l_map = {n:[self.node_to_level(n)] for n in nodeset} 
        l2nodeset_map = invert_map__seqvalue(n2l_map) 
        l2nodeset_map = {k:set(v) for k,v in l2nodeset_map.items()}
        return self.run_full_traversal__nodeset_req(l2nodeset_map,\
            num_paths,proper_paths_only,prg)

    def run_full_traversal(self,starting_path:NodePath,\
        num_paths,proper_paths_only:bool=True,prg=None): 

        assert type(starting_path) == NodePath 

        self.ptrav_queue.clear()
        self.ptrav_cache.clear() 
        self.ptrav_queue.append([starting_path,False,False]) 
        self.trav_error = False 

        stat = True 
        while stat and len(self.ptrav_cache) < num_paths: 
            stat = self.next_from_queue(prg,proper_paths_only) 

        return list(self.ptrav_cache) 

    def run_full_traversal__nodeset_req(self,l2nodeset_map,num_paths,\
        proper_paths_only:bool,prg=None):

        self.ptrav_queue.clear()
        self.ptrav_cache.clear() 
        self.ptrav_queue2.clear() 

        L = sorted(l2nodeset_map.keys())
        i = floor(len(L) / 2) 
        start = L[i] 

        N = l2nodeset_map[start]

        if len(N) == 1: 
            P = NodePath(N.pop()) 
        else: 
            P = self.intralayer_nodeset_path(N,prg) 
        self.ptrav_queue.append([P,False,False]) 

        while len(self.ptrav_queue) > 0 and not self.trav_error and \
            len(self.ptrav_cache) < num_paths: 
            self.next_from_queue__nodeset_req(prg,proper_paths_only,\
                l2nodeset_map)
        return list(self.ptrav_cache)

    ##------------------ partial paths (intralayer paths that include selected nodes) 

    """
    calculates one path in a layer that includes all nodes of nset 
    """
    def intralayer_nodeset_path(self,nset,prg=None): 
        assert type(nset) == set and len(nset) > 1 

        L = set() 
        for n in nset: 
            l = self.node_to_level(n)
            assert type(l) != type(None) 

            L |= {l} 
        assert len(L) == 1 

        nset_ = sorted(nset) 
        if type(prg) != type(None): 
            nset_ = prg_seqsort(nset_,prg) 

        # declare starting paths 
        Q = deque() 
        for n in nset_: 
            P = NodePath(n) 
            Q.append(P)

        while len(Q) > 0: 
            P_ = Q.popleft()
            rem_nodes = nset - set(P_.p) 

            if len(rem_nodes) == 0: 
                return P_ 

            C = self.siblings_of_node(P_.tail(),False)
            if len(C) == 0: continue 


            C = sorted(C) 
            if type(prg) != type(None): 
                C = prg_seqsort(C,prg) 

            for c in C: 
                P1 = deepcopy(P_) 
                P1.append(c,1) 
                Q.appendleft(P1)

        return None 
        
    """
    calculates one path in a layer that includes nodes n0 and n1  
    """
    def intralayer_node2node_path(self,n0,n1,prg=None): 
        q0 = self.intralayer_node2node_path_(n0,n1,prg) 
        if type(q0) == NodePath: return q0 

        q1 = self.intralayer_node2node_path_(n1,n0,prg) 
        if type(q1) == NodePath: return q1 

        return None 


    def intralayer_node2node_path_(self,start_node,end_node,prg=None): 
        assert type(prg) == type(None) or type(prg) in {MethodType,FunctionType}

        l0 = self.node_to_level(start_node) 
        l1 = self.node_to_level(end_node) 
        assert l0 == l1 

        P = NodePath(start_node) 
        Q = deque([P]) 

        while len(Q) > 0: 
            P_ = Q.popleft()
            C = sorted(self.siblings_of_node(P_.tail(),False)) 

            if len(C) == 0: continue 

            if type(prg) != type(None): 
                C = prg_seqsort(C,prg) 

            if end_node in C: 
                P_.append(end_node,1) 
                return P_ 

            for c in C: 
                P1 = deepcopy(P_) 
                P1.append(c,1) 
                Q.appendleft(P1)
        return None 

    def next_from_queue(self,prg,is_proper_path:bool):
        assert type(is_proper_path) == bool 
        
        if len(self.ptrav_queue) == 0: 
            return False 

        x = self.ptrav_queue.popleft() 
        P = x[0] 
        
        parents = self.parents_of_node(P.head(),is_proper_path)
        C = self.children_of_node(P.tail(),is_proper_path) 

        # case: reached root node/s 
        if len(parents) == 0: 
            x[1] = True 

        # case: reached leaf node/s 
        if len(C) == 0: 
            x[2] = True 

        # case: finished 
        if x[1] and x[2]: 
            self.ptrav_cache.append(x[0]) 
            return True 

        new_paths = [] 

        # case: add parents
        if not x[1]: 
            parents = sorted(parents) 
            for p in parents: 
                pth = deepcopy(P) 
                pth.prepend(p,1) 
                new_paths.append([pth,x[1],x[2]])

        # case: add children 
        if not x[2]: 
            C = sorted(C) 
            for c in C: 
                pth = deepcopy(P) 
                pth.append(c,1) 
                new_paths.append([pth,x[1],x[2]])

        # use PRNG to sort 
        if type(prg) != type(None): 
            new_paths = prg_seqsort(new_paths,prg)
        
        for npth in new_paths: 
            self.ptrav_queue.appendleft(npth) 
        return True 

    def next_from_queue__nodeset_req(self,prg,is_proper_path:bool,\
        l2nodeset_map:dict): 
        assert type(is_proper_path) == bool 
        self.ptrav_queue2.clear() 

        if len(self.ptrav_queue) == 0: 
            return  

        x = self.ptrav_queue.popleft() 

        # case: done 
        if x[1] == x[2] == True: 
            self.ptrav_cache.appendleft(x[0]) 
            return 

        if not x[1]: 
            c0 = self.add_next_level_nodes__nodeset_req(x[0],prg,\
            is_proper_path,l2nodeset_map,add_parent=True)
            if c0 == 0: 
                x[1] = True   

        if not x[2]: 
            c1 = self.add_next_level_nodes__nodeset_req(x[0],prg,\
            is_proper_path,l2nodeset_map,add_parent=False) 
            if c1 == 0: 
                x[2] = True 

        if len(self.ptrav_queue2) == 0: 
            self.ptrav_queue.appendleft([x[0],x[1],x[2]])
            return 

        R = list(self.ptrav_queue2)
        if type(prg) != type(None): 
            R = prg_seqsort(R,prg) 

        for r in R: 
            self.ptrav_queue.appendleft([r,x[1],x[2]]) 
        return 

    """
    adds nodes to path `P`, at either the head (parents) or tail (children). 
    
    return:
    - integer, number of new paths produced from `P`. 
    """
    def add_next_level_nodes__nodeset_req(self,P:NodePath,prg,\
        is_proper_path:bool,l2nodeset_map:dict,add_parent:bool): 
        assert type(P) == NodePath 

        def add_to_path(pth,node): 
            if add_parent: 
                pth.prepend(node,1) 
            else: 
                pth.append(node,1)
            self.ptrav_queue2.appendleft(pth)  

        if add_parent: 
            l = self.node_to_level(P.head()) 
            C = self.parents_of_node(P.head(),is_proper_path)
            i = -1 
        else: 
            l = self.node_to_level(P.tail()) 
            C = self.children_of_node(P.tail(),is_proper_path) 
            i = 1 

        pset = set() 

        # case: next layer is in required nodeset 
        if l + i in l2nodeset_map: 
            pset = l2nodeset_map[l + i]

        # add sibling nodes first  
        C_ = set() 
            # subcase: no next layer 
        try: 
            C_ = C - self.l2n_map[l + i] 
        except: 
            pass 
        C2 = C - C_ 

        count = 0 
        for c in C_: 
            P_ = deepcopy(P) 
            add_to_path(P_,c)
            count += 1 

        # add the next layers 

            # case: 0 required nodes of next layer 
        if len(pset) == 0: 
            for c in C2: 
                P_ = deepcopy(P) 
                add_to_path(P_,c) 
                count += 1 

            # case: only one node per next layer 
        elif len(pset) == 1: 
            P_ = deepcopy(P) 
            x = pset.pop() 
            stat = False 
            if add_parent: 
                q = P.head() 
                if q in self.G[x]: 
                    stat = True 
            else: 
                q = P.tail() 
                if q in self.G_rev[x]: 
                    stat = True 

            if not stat: 
                self.trav_error = True 
                return count  
            add_to_path(P_,x)
            count += 1 

            # case: required nodeset of size > 1 
        else: 
            ppath = self.intralayer_nodeset_path(pset,prg) 
            
            # subcase: nodeset does not exist 
            if type(ppath) == type(None): 
                self.trav_error = True 
                return False 

            X = None 
            if add_parent: 
                ppath.add_path_v2(P) 
                X = ppath 
            else: 
                P.add_path_v2(ppath) 
                X = P 
            self.ptrav_queue2.appendleft(X) 
            count += 1 
        return count 

    #------------------------------- verifying instantiating parameters 

    def verify(self): 
        self.G_ = deepcopy(self.G) 

        for k_ in self.l2n_map.keys(): 
            self.intrasets_of_layer(k_) 
            self.clear_intralayer_edges(k_) 

        for k,v in self.l2n_map.items(): 

            for v_ in v: 
                P = self.n_paths_with_node(v_,1,True)
                if len(P) == 0: 
                    self.erroneous_node = v_ 
                    print("[!] non-existent node??")
                    self.G = deepcopy(self.G_) 
                    return False 

                level = P[0].p.index(v_)  

                if level != k: 
                    self.erroneous_node = v_
                    print("[!] wrong level for node {}: got {},expected {}".format(v_,level,k))
                    self.G = deepcopy(self.G_) 
                    return False 

        self.G = deepcopy(self.G_) 
        return True 

    #------------------------------- permuting nodes 

    # TODO: needs to be tested. 
    def permute_nodes(self,prg): 

        # case: empty graph 
        if len(self.G) == 0: return 

        # calculate the isomap first 
        nodes = sorted(self.G.keys()) 
        nodes2 = prg_seqsort(deepcopy(nodes),prg) 
        D = {n:n2 for (n,n2) in zip(nodes,nodes2)} 

        # change the graph 
        mg = MicroGraph(self.G) 
        mg2 = MicroGraph.isotransform_MG(mg,D) 
        G2 = mg2.dg 

        # change the level-to-nodeset map 
        l2n_map2 = dict() 

        for k,v in self.l2n_map.items(): 
            v2 = [D[v_] for v_ in v] 
            l2n_map2[k] = set(v2)  

        self.G = G2 
        self.G_rev = reverse_graph_edges(self.G) 
        self.l2n_map = l2n_map2
        return 

    def nodepath_to_level_map(self,P:NodePath): 
        assert type(P) == NodePath
        return {p:self.node_to_level(p) for p in P.p} 
            
"""
(D)irected (A)cyclic (G)raph Generator. 
"""
class DAGraphGen(DAGraphContainer): 

    """
    num_node_range_per_layer := int range | list<int range>; specifies the range of nodes per layer. 
            If format is list of ranges, cyclically iterates through list of ranges. 
    gen_scheme := "mult" -> every node has x number of children in range of `num_node_range_per_layer`,
                "constant" -> every layer has x number of nodes in range of `num_node_range_per_layer`.
    intralayer_conn_range := float range, of [0.,1.], ratios specify the possible number of directed 
            edges between nodes of the same layer. 
    prg := PRNG, inputless function.
    uniform_depth := bool, guarantees "uniform depth" of DAG: 
        for any non-leaf node, there exists a path from it to a leaf. 
    """
    def __init__(self,num_node_range_per_layer,gen_scheme,multiparent_pr_range,intralayer_conn_range,\
        prg,uniform_depth:bool=True): 

        if is_number(num_node_range_per_layer[0]):
            assert is_valid_range(num_node_range_per_layer,True,True) 
            assert num_node_range_per_layer[0] > 0 
            self.lranges = [num_node_range_per_layer] 
        else: 
            for x in num_node_range_per_layer: 
                assert is_valid_range(x,True,True) 
                assert x[0] > 0 
            self.lranges = num_node_range_per_layer
        self.lr_index = 0 

        assert gen_scheme in {"mult","constant"}
        assert is_valid_range(multiparent_pr_range,False,True) and \
            0.0 <= multiparent_pr_range[0] <= multiparent_pr_range[1] <= 1.0 
        assert is_valid_range(intralayer_conn_range,False,True) and \
            0.0 <= intralayer_conn_range[0] <= intralayer_conn_range[1] <= 1.0 

        assert type(prg) in {MethodType,FunctionType}
        assert type(uniform_depth) == bool 

        self.gen_scheme = gen_scheme
        self.mp_pr_range = multiparent_pr_range
        self.intra_conn_range = intralayer_conn_range
        self.prg = prg 
        self.uniform_depth = uniform_depth 

        super().__init__(defaultdict(set),dict(),False) 

        self.level = 0 
        self.prev_leaf_nodes = []  
        self.leaf_nodes = [] 

        self.node_index = 0 
        return 

    def __next__(self): 

        if self.gen_scheme == "constant": 
            self.next_layer__constant()
            return 

        self.next_layer__mult() 
        return 

    def next_layer__mult(self): 

        # case: start of graph 
        if self.level == 0: 
            self.generate_layer_nodes__constant()
            return 

        parent_nodes = self.connect_first_round__mult() 

        # multi-parent connections 
        self.multiparent_connect(parent_nodes) 
        return 

    def next_layer__constant(self): 
        
        self.generate_layer_nodes__constant() 

        # case: start of graph 
        if self.level == 1: 
            return 

        # case: connect to previous leaves
        # first round 
        parent_nodes = self.connect_first_round__constant()

        # multi-parent connections 
        self.multiparent_connect(parent_nodes) 
        return 

    #------------------------- edge generation methods 

    def intraconnect_layer(self,l): 
        # clear any present intralayer edges first 
        self.clear_intralayer_edges(l) 

        # case: less than two nodes in level 
        if len(self.l2n_map[l]) < 2: 
            return 

        q = safe_prg_decimal(self.prg,self.intra_conn_range) 
        nodeset = self.l2n_map[l] 

        max_edges = len(self.l2n_map[l]) - 1 
        num_edges = ceil(max_edges * q)
        available_nodes = sorted(nodeset) 
        intra_nodesets = [set([n]) for n in available_nodes]

        def one_edge(): 
            # choose two sets from `intra_nodesets`
            i = int(self.prg()) % len(intra_nodesets)
            s0 = intra_nodesets.pop(i) 

            j = int(self.prg()) % len(intra_nodesets)
            s1 = intra_nodesets.pop(j) 

            # choose a node from each of the sets 
            s0_ = sorted(s0)
            s1_ = sorted(s1) 

            n0 = int(self.prg()) % len(s0_)
            n1 = int(self.prg()) % len(s1_) 

            self.add_edge(s0_[n0],s1_[n1]) 

            intra_nodesets.append(s0 | s1) 
            return (n0,n1) 

        for _ in range(num_edges): 
            one_edge() 
        return 

    """
    generate the next layer's nodeset, based on the `constant` 
    scheme.
    """
    def generate_layer_nodes__constant(self): 
        lr = self.lranges[self.lr_index] 
        self.lr_index = (self.lr_index + 1) % len(self.lranges) 
        x = safe_modulo_in_range(int(self.prg()),lr)

        nodes = [] 
        for i in range(x): 
            nodes.append(self.node_index + i) 
        self.node_index += x 

        self.prev_leaf_nodes = deepcopy(self.leaf_nodes) 
        self.leaf_nodes = nodes 
        self.l2n_map[self.level] = set(nodes)

        for x in nodes: 
            self.G[x] = set() 

        self.intraconnect_layer(self.level) 
        self.level += 1 
        return 

    """
    conducts the first round of edge connections between parent and 
    leaf nodes. 

    Divides cases up into child nodesets of size less than XOR 
    (greater than or equal to) parent nodeset size. 
    """
    def connect_first_round__constant(self): 
        q = sorted(self.prev_leaf_nodes)
        prg_ = prg__single_to_int(self.prg)

        # case: not guarantee every parent connected to a child node 
        if not self.uniform_depth:
            lq = min([len(self.prev_leaf_nodes),len(self.leaf_nodes)])
            num_connected_parents = modulo_in_range(int(self.prg()),[1,lq+1])
            q = prg_choose_n(q,num_connected_parents,prg_,is_unique_picker=True) 

        if len(q) <= len(self.leaf_nodes): 
            return self.connect_first_round__childset_size_geq(q) 
        return self.connect_first_round__childset_size_lt(q) 

    def connect_first_round__childset_size_geq(self,parent_nodes): 
        assert type(parent_nodes) == list 
        prg_ = prg__single_to_int(self.prg)

        # partition the child nodes for the selected subset of 
        # parent nodes 
        cnodes = sorted(self.leaf_nodes) 
        cnodes = prg_seqsort(cnodes,prg_)

        P = prg_partition_for_sz__n_rounds(len(cnodes),len(parent_nodes),\
            prg_,var=0.5,n=50) 

        start_index = 0 

        for (i,q_) in enumerate(parent_nodes): 
            end_index = start_index + P[i]
            children = cnodes[start_index:end_index]

            for c in children: 
                self.add_edge(q_,c) 
            #self.G[q_] |= set(children) 
            start_index = end_index 
        return parent_nodes

    def connect_first_round__childset_size_lt(self,parent_nodes): 
        assert type(parent_nodes) == list 
        assert len(parent_nodes) > len(self.leaf_nodes)

        # case: uniform depth, every parent node must be connected to 
        #       at least one child node. 
        if self.uniform_depth: 
            L = prg_seqsort(deepcopy(self.leaf_nodes),self.prg)
            j = 0 
            for p in parent_nodes: 
                if j >= len(L): 
                    L = prg_seqsort(deepcopy(self.leaf_nodes),self.prg)
                    j = 0 
                
                c = L[j] 
                #self.G[p] |= {c} 
                self.add_edge(p,c) 
                j += 1
            return parent_nodes 
    
        # case: not uniform depth, number of parent nodes with child 
        #       node equal to number of child nodes. 
        prg_ = prg__single_to_int(self.prg)
        parents = prg_choose_n(parent_nodes,len(self.leaf_nodes),prg_,is_unique_picker=True)

        for (i,p) in enumerate(parents): 
            c = self.leaf_nodes[i] 
            #self.G[p] |= {c} 
            self.add_edge(p,c) 

        return parents

    #----------------------------------------   SUBCASE: gen. scheme == mult 

    """
    """
    def connect_first_round__mult(self):
        # get the leaf size range per parent node 
        lr = self.lranges[self.lr_index] 
        self.lr_index = (self.lr_index + 1) % len(self.lranges) 

        prg_ = prg__single_to_int(self.prg)

        # get the parent nodes 
        q = deepcopy(self.leaf_nodes) 

        # case: get subset of parent nodes 
        if not self.uniform_depth: 
            num_connected_parents = modulo_in_range(int(self.prg()),[1,len(q)+1]) 
            q = prg_choose_n(q,num_connected_parents,prg_,is_unique_picker=True) 

        new_leaves = [] 
        for l in q: 
            i = safe_modulo_in_range(int(self.prg()),lr)
            for _ in range(i): 
                self.G[self.node_index] = set()
                #self.G[l] |= {self.node_index} 
                self.add_edge(l,self.node_index) 
                new_leaves.append(self.node_index) 

                self.node_index += 1 
        self.prev_leaf_nodes = deepcopy(self.leaf_nodes) 
        self.leaf_nodes = new_leaves 

        self.l2n_map[self.level] = set(self.leaf_nodes)
        self.intraconnect_layer(self.level)  
        self.level += 1 
        return q


    """
    method called after method<connect_first_round> 
    """
    def multiparent_connect(self,parent_nodes): 
        # case: no multi-parents 
        if self.mp_pr_range[0] == self.mp_pr_range[1] == 0.: 
            return 

        assert set(parent_nodes).issubset(set(self.prev_leaf_nodes)) 
        parent_nodes = sorted(parent_nodes)

        for l in parent_nodes: 
            for l2 in self.leaf_nodes: 
                x = safe_prg_decimal(self.prg,self.mp_pr_range) 
                d = prg_decimal(self.prg,[0.,1.])

                # case: add edge 
                if d < x: 
                    #self.G[l] |= {l2}
                    self.add_edge(l,l2) 

    #----------------------------- extra ops: 
    #----------------------------- converting to <DAGraphContainer> and permuting nodes 

    def to_DAGraph(self): 
        return DAGraphContainer(self.G,self.l2n_map,check_input_graph=False)

    def permute_nodes(self): 
        if len(self.G) == 0: return 

        super().permute_nodes(self.prg)  

        # update the leaf variables 
        K = sorted(self.l2n_map.keys())
        i0 = K.pop(-1) 
        self.leaf_nodes = sorted(self.l2n_map[i0]) 

        if len(K) > 0: 
            i1 = K.pop(-1) 
            self.prev_leaf_nodes = sorted(self.l2n_map[i1]) 
        else: 
            self.prev_leaf_nodes = [] 