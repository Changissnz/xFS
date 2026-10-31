from .node_path import * 
from .graph_gen import * 
from morebs2.matrix_methods import is_number
from morebs2.numerical_generator import safe_modulo_in_range,\
    prg_decimal,safe_prg_decimal,prg_partition_for_sz__n_rounds,prg_choose_n

'''
Storage container and operator for Directed Acyclic Graphs. Stores 
nodesets per DAG `level`. Calculates proper children and parents 
of any arbitrary node of DAG. Proper children/parent nodes of 
a node `n` cannot be at the same level as `n`. 

NOTE: the terms `level` and `layer` are interchangeable, and are 
integers assigned to nodes that signify their minimum distances from 
the root node/s. 

Calculates any variable k' <= k number of paths that have node `n` 
of `G` in them. 
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
        self.G_rev = reverse_graph_edges(self.G) 
        self.l2n_map = l2n_map 

        # path traversal cache + queue, 
        # used for method<n_paths_with_node>. 
        #   element := (NodePath, ?finished head?, ?finished tail?)
        self.ptrav_queue = deque()
        self.ptrav_cache = deque() 

        self.erroneous_node = None 
        if check_input_graph: 
            self.verify()
            self.G = deepcopy(self.G_) 
            self.G_ = None 
        return

    def add_edge(self,source,target):
        self.G[source] |= {target} 
        self.G_rev[target] |= {source}  

    def parents_of_node(self,n):  
        q = children_of(self.G_rev,n) 
        l = self.node_to_level(n) 
        return q - self.l2n_map[l]

    def children_of_node(self,n): 
        q = children_of(self.G,n) 
        l = self.node_to_level(n) 
        return q - self.l2n_map[l]  

    def node_to_level(self,n): 
        for l,v in self.l2n_map.items(): 
            if n in v: return l 
        return -1 

    def level_to_nodeset(self,l): 
        if l not in self.l2n_map: 
            return None 
        return deepcopy(self.l2n_map[l])

    #------------------------- intralayer edge operations 

    def intrasets_of_layer(self,l): 
        nodes = sorted(self.l2n_map[l]) 
        return -1 

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

    #-------------------------- path operations  

    def n_paths_with_node(self,node,num_paths,prg=None): 
        self.ptrav_queue.clear()
        self.ptrav_cache.clear() 

        if node not in self.G: 
            return deque() 

        N = NodePath(node) 
        self.ptrav_queue.append([N,False,False]) 

        stat = True 
        while stat and len(self.ptrav_cache) < num_paths: 
            stat = self.next_from_queue(prg) 

        return self.ptrav_cache 

    def next_from_queue(self,prg): 
        if len(self.ptrav_queue) == 0: 
            return False 

        x = self.ptrav_queue.popleft() 
        P = x[0] 
        
        parents = self.parents_of_node(P.head())
        C = self.children_of_node(P.tail()) 

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

    #------------------------------- verifying instantiating parameters 

    def verify(self): 
        self.G_ = deepcopy(self.G) 

        for k_ in self.l2n_map.keys(): 
            self.clear_intralayer_edges(k_) 

        for k,v in self.l2n_map.items(): 

            for v_ in v: 
                P = self.n_paths_with_node(v_,1)
                if len(P) == 0: 
                    self.erroneous_node = v_ 
                    print("[!] non-existent node??")
                    return False 

                level = P[0].p.index(v_)  
                if level != k: 
                    self.erroneous_node = v_
                    print("[!] wrong level for node {}: got {},expected {}".format(v_,level,k))
                    return False 
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

        q = safe_prg_decimal(self.prg,self.intra_conn_range) 
        nodeset = self.l2n_map[l] 

        max_edges = max_simple_edges(len(self.l2n_map[l]))
        num_edges = ceil(max_edges * q)

        available_nodes = sorted(nodeset) 

        # agent idn -> parent nodeset 
        parent_node_map = defaultdict(set) 

        def one_edge(): 
            i = int(self.prg()) % len(available_nodes) 
            n = available_nodes[i] 

            A = nodeset - {n} - parent_node_map[n] - self.G[n] 
            if len(A) == 0: 
                available_nodes.pop(i) 
                return one_edge() 
            
            A = sorted(A) 
            j = int(self.prg()) % len(A) 
            n2 = A[j] 

            parent_node_map[n2] |= {n} 
            self.add_edge(n,n2) 
            ##self.G[n] |= {n2} 
            return (n,n2) 

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