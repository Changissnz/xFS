#from .node_path import * 
from .analog_schemes_aux import * 

DEFAULT_JAMMING_GRAPH_TYPES = ["c","o"]

DEFAULT_JAMMING_GRAPH_ALTER_NODE_RATIO_RANGE = [-0.2,0.2] 
DEFAULT_JAMMING_GRAPH_ALTER_EDGE_RATIO_RANGE = [-0.2,0.2]

DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE = [3,15] 
DEFAULT_JAMMING_GRAPH_TYPE_O_CONNECTIVITY_RANGE = [0.05,0.22] 

"""
Instance is instantiated with a <NodePath> from node s to t, and with 
additional parameters specifying the numerical qualities for the jam 
process. 

The jam process is given as function<JammingGraph.one_jam>. <NodePath> 
must consist of unique nodes N, these nodes comprising the base nodes for 
the graph G_k (keys of variable<node2nodesets>), built from k calls to 
function<JammingGraph.one_jam>. Variable `modifiable_nodeset` is a subset 
of N and specifies the nodes that JammingGraph can "modify", as part of its 
jam process. 

Jam variants are of Type (C)ircumvention and Type (O)bstruction. In both types, 
function<JammingGraph.one_jam> receives one base node n_b as input at timestamp k. 
It generates a subgraph G2, with no nodes of G_k, and adds nodes of G2 to the nodeset 
`node2nodesets[n_b]`. If parameter `remove_original_node`, then node n_b2, a node that 
is n_b or part of the same nodeset `node2nodesets[n_b]`, is removed. 

The number of calls to function<JammingGraph.one_jam> positively correlates to longer 
paths on average between nodes s and t. 
"""
class JammingGraph: 

    def __init__(self,nodepath,modifiable_nodeset,prg,\
        is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None): 

        assert type(prg) in {MethodType,FunctionType}
        assert len(nodepath) >= 2 and len(set(nodepath.p)) == len(nodepath)  
        assert modifiable_nodeset.issubset(set(nodepath.p))
        assert len(modifiable_nodeset) > 0
        assert is_valid_range(jam_nodesize_range,True,False) 

        self.npath = nodepath 
        self.modifiable_nodeset = modifiable_nodeset 
        self.prg = prg 
        self.is_directed = is_path_directed
        self.jam_nodesize_range = jam_nodesize_range 
        if type(ctr_function) != type(None): 
            assert type(ctr_function) in {MethodType,FunctionType}
            self.ctr = ctr_function
        else: 
            self.ctr = SimpleCounter(max(self.npath.p) + 1).__next__ 
        self.node2nodesets = defaultdict(list) 
        for k in nodepath.p: 
            self.node2nodesets[k] = [{k}]  

        self.G = nodepath.to_graph(is_path_directed)
        self.dead_nodes = set() 

        # from the most recent jam 
        self.new_nodes = set() 
        return

    def __len__(self): 
        return len(self.G) 

    def one_jam(self,node,remove_original_node:bool):
        return -1 

    def entire_nodeset_for_node(self,q): 
        if q not in self.node2nodesets: 
            return set()  
        return flatten_setseq(self.node2nodesets[q]) 

    def alter_nodeset(self,disconnect_possible:bool):  

        i = int(self.prg()) % len(self.modifiable_nodeset) 
        n = sorted(self.modifiable_nodeset)[i]
        if len(self.node2nodesets[n]) == 0: 
            return 

        j = int(self.prg()) % len(self.node2nodesets[n]) 
        self.alter_nodeset_(n,j,disconnect_possible)
        return

    def alter_nodeset_(self,base_node,nodeset_index,disconnect_possible:bool,max_edge_changes = 1000):  

        nodeset = self.node2nodesets[base_node][nodeset_index] 
        # case: no alter 
        if len(nodeset) < 3: 
            return 

        G2 = MicroGraph(self.G).subgraph_by_nodeset_(nodeset).dg   
        
        nc_ratio = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_ALTER_NODE_RATIO_RANGE) 
        ec_ratio = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_ALTER_EDGE_RATIO_RANGE)  

        G3,_ = graph_derivation(deepcopy(G2),self.is_directed,nc_ratio,ec_ratio,self.prg,self.ctr,\
            max_edge_changes)
        self.node2nodesets[base_node][nodeset_index] = set(G3.keys())

        mg = MicroGraph(self.G) 
        mg = mg - MicroGraph(G2) 
        mg = mg + MicroGraph(G3)
        self.G = mg.dg 

        if not self.is_directed: 
            self.G = directed_to_undirected_graph(self.G) 

        if not disconnect_possible: 
            self.ensure_connected(base_node)
        return

    def ensure_connected(self,base_node): 

        # get the neighbors of base_node 
        left,right = self.neighbor_nodesets_to_base_nodeset(base_node)
        
        base_nodeset = self.entire_nodeset_for_node(base_node) 
        G1 = MicroGraph(self.G).subgraph_by_nodeset_(base_nodeset) 
        G10,G11 = MicroGraph(defaultdict(set)),MicroGraph(defaultdict(set))
        G0,G2 = None,None 

        if type(left) != type(None): 
            left_nodeset = self.entire_nodeset_for_node(left)
            G0 = MicroGraph(self.G).subgraph_by_nodeset_(left_nodeset)
            G10 = graph_to_one_component((G0+deepcopy(G1)).dg,self.prg)
            G10 = MicroGraph(G10)  

        if type(right) != type(None): 
            right_nodeset = self.entire_nodeset_for_node(right)
            G2 = MicroGraph(self.G).subgraph_by_nodeset_(right_nodeset)
            G11 = graph_to_one_component((deepcopy(G1)+G2).dg,self.prg)
            G11 = MicroGraph(G11)

        self.G = (MicroGraph(self.G) + G1 + G10 + G11).dg
        return

    def disconnect_neighbors(self,base_node1,base_node2):
        ns1 = self.entire_nodeset_for_node(base_node1)
        ns2 = self.entire_nodeset_for_node(base_node2) 

        for n in ns1: 
            self.G[n] -= ns2 
        
        if self.is_directed: return 

        for n in ns2: 
            self.G[n] -= ns1
        return 
    
    def neighbor_nodesets_to_base_nodeset(self,base_node): 
        i = self.npath.p.index(base_node) 

        left,right = None,None 
        if i == 0: 
            right = self.npath.p[i+1] 
        elif i == len(self.npath) -1: 
            left = self.npath.p[i-1] 
        else: 
            left,right = self.npath.p[i-1],\
                    self.npath.p[i+1] 
        return left,right 

    def prng_choose_jam_mod_info(self,base_node): 
        num_nodes = modulo_in_range(int(self.prg()),self.jam_nodesize_range) 
        assert num_nodes > 1 
        node = self.prng_choose_node_in_base_nodeset(base_node,False)
        return num_nodes,node 

    def prng_choose_node_in_base_nodeset(self,base_node,choose_minimally_connected:bool): 
        q = self.entire_nodeset_for_node(base_node)
        if len(q) == 0: return None 

        q = sorted(q) 
        if not choose_minimally_connected: 
            i = int(self.prg()) % len(q) 
            return q[i] 
        
        G_ = MicroGraph(self.G).subgraph_by_nodeset_(set(q)).dg 
        q = [(q_,len(G_[q_])) for q_ in q] 
        q = prg_seqsort_ties(q,self.prg,vf=lambda x: x[1])
        return q[0][0] 

    def connect_nodesets(self,ref_base_node,base_node0): 
        left_nodeset = self.entire_nodeset_for_node(ref_base_node)
        right_nodeset = self.entire_nodeset_for_node(base_node0)
        conn0 = are_nodesets_connected(self.G,left_nodeset,right_nodeset) 
        if not conn0: 
            q0 = self.prng_choose_node_in_base_nodeset(ref_base_node,True)
            q1 = self.prng_choose_node_in_base_nodeset(base_node0,True) 
            if type(q0) == type(None) or type(q1) == type(None): return 

            self.G[q0] |= {q1} 
            if not self.is_directed: 
                self.G[q1] |= {q0} 
        return 

    def nodeset_index_for_node(self,node): 
        for k,v in self.node2nodesets.items(): 
            for (i,v_) in enumerate(v): 
                if node in v_:
                    return (k,i)
        return None,None 

    def subgraph_edit(self,node,G_,remove_original_node:bool): 
        # replace the direct nodeset and subgraph 
        q0,q1 = self.nodeset_index_for_node(node)

        # TODO: delete this. 
        """
        if type(q0) == type(None): 
            print("NODE IS: ",q0) 
            mg = MicroGraph(self.G) + MicroGraph(G_)  
            self.G = mg.dg
            self.G = graph_to_one_component(self.G,self.prg)
            self.node2nodesets[node].append(set(G_.keys()))
            return 
        """

        nodeset_ = self.node2nodesets[q0][q1]
        subgraph = MicroGraph(self.G).subgraph_by_nodeset_(nodeset_)

        if remove_original_node: 
            self.node2nodesets[q0][q1] -= {node} 
            if len(self.node2nodesets[q0][q1]) == 0: 
                self.node2nodesets[q0].pop(q1) 
            self.node2nodesets[q0].append(set(G_.keys()))
            mg = MicroGraph(self.G)
            mg.subgraph_nodeset_exclusion({node})
            self.G = mg.dg 
        else: 
            self.node2nodesets[q0][q1] |= set(G_.keys()) 

            # cut connection from node to other nodes not of G_ 
            cut_conn = self.G[node] - self.node2nodesets[q0][q1]

            self.G[node] -= cut_conn 

            if not self.is_directed: 
                for c in cut_conn: 
                    self.G[c] -= {node} 
            
        # update graph 
        nodeset = flatten_setseq(self.node2nodesets[q0])

        mg = MicroGraph(self.G) + MicroGraph(G_)  
        self.G = mg.dg 

        # ensure entire nodeset of node is connected 
        G = MicroGraph(self.G).subgraph_by_nodeset_(nodeset).dg 
        G = graph_to_one_component(G,self.prg)
        self.G = (MicroGraph(self.G) + MicroGraph(G)).dg 

        # connect the new graph to neighbors 
        left,right = self.neighbor_nodesets_to_base_nodeset(q0)

        if type(left) != type(None): 
            self.connect_nodesets(left,q0)

        if type(right) != type(None): 
            self.connect_nodesets(q0,right)

        # case: add removed node to dead nodes
        if remove_original_node:
            self.dead_nodes |= {node}
        return G,node 

    """
    NOTE: deletion of nodeset could lead to disconnected graph 
    """
    def delete_nodeset(self,nodeset): 
        # delete nodeset from `node2nodesets` 
        for k in self.node2nodesets.keys(): 
            q = self.node2nodesets[k] 

            i = 0   
            while i < len(q): 
                q_ = q[i] - nodeset 
                q[i] = q_ 
                if len(q[i]) == 0: 
                    q.pop(i) 
                else: 
                    i += 1 
            self.node2nodesets[k] = q 

        # delete nodeset from G 
        G_ = self.G
        d = MicroGraph(G_)
        d.subgraph_nodeset_exclusion(nodeset) 
        self.G = d.dg 
        return 

    """
    generates a Type C or Type O instance, with 3 base nodes 
    0,1,2, such that base node 1 is the only modifiable node. 
    """
    @staticmethod
    def generate_3node_instance(is_directed,jam_type,prg,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE):
        assert jam_type in DEFAULT_JAMMING_GRAPH_TYPES 

        p = NodePath.preload([0,1,2],[1,1]) 
        modifiable = {1} 

        if jam_type == "c": 
            return JammingGraphTypeC(p,modifiable,prg,is_directed,jam_nodesize_range) 
        return JammingGraphTypeO(p,modifiable,prg,is_directed,jam_nodesize_range)        


"""
Type (C)ircumvention of Jamming Graph, based on the principle of forming 
monotonically longer paths between two target nodes. 
"""
class JammingGraphTypeC(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg,is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None): 
        super().__init__(nodepath,modifiable_nodeset,prg,is_path_directed,jam_nodesize_range,ctr_function)
        return

    """
    main method 
    """
    def one_jam(self,base_node,remove_original_node:bool):
        assert base_node in self.modifiable_nodeset

        num_nodes,node = self.prng_choose_jam_mod_info(base_node) 

        start_node = self.ctr() 
        if remove_original_node: 
            G = generate_graph__path(num_nodes,start_node,self.is_directed)
            for _ in range(num_nodes - 1): 
                self.ctr() 
        else: 
            G = defaultdict(set) 
            num_forward = int(self.prg()) % num_nodes 
            num_backward = num_nodes - num_forward 
            # get forward 
            prev = node 
            for _ in range(num_forward): 
                q = self.ctr() 
                G[prev] |= {q} 
                if not self.is_directed: 
                    G[q] |= {prev}
                prev = q 
            if prev not in G: 
                G[prev] = set() 

            # get backward
            prev = node 
            for _ in range(num_backward): 
                q = self.ctr() 
                G[q] |= {prev} 
                if not self.is_directed: 
                    G[prev] |= {q}
                prev = q 
            if prev not in G: 
                G[prev] = set()
        
        self.new_nodes = set(G.keys())
        return self.subgraph_edit(node,G,remove_original_node) 

"""
Type (O)bstruction of Jamming Graph, based on the principle of adding 
unwanted masses (obstruction in the form of subgraphs) between two target nodes. 
"""
class JammingGraphTypeO(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg,is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None):
        super().__init__(nodepath,modifiable_nodeset,prg,is_path_directed,jam_nodesize_range,ctr_function)
        return

    """
    main method 
    """
    def one_jam(self,base_node,remove_original_node:bool):
        assert base_node in self.modifiable_nodeset

        num_nodes,node = self.prng_choose_jam_mod_info(base_node)

        is_realtime_gen = bool(int(self.prg()) % 2)
        edge_connectivity = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_TYPE_O_CONNECTIVITY_RANGE)
        gg = GraphGen(self.is_directed,self.prg,is_realtime_gen,num_nodes,edge_connectivity)
        gg.full_run()
        G = gg.d 
        graph_childkey_fillin(G)  
        G,_ = graph_automorphism(G,self.ctr)

        if not remove_original_node: 
            ratio_conn = modulo_in_range(self.prg(),[0.05,0.3]) 
            num_conn = ceil(len(G) * ratio_conn)
            node_candidates = sorted(G.keys())
            node_conn = prg_choose_n(node_candidates,num_conn,prg__single_to_int(self.prg),True)

            for x in node_conn: 
                G[node] |= {x} 
                if not self.is_directed: G[x] |= {node} 
        self.new_nodes = set(G.keys())
        return self.subgraph_edit(node,G,remove_original_node)  