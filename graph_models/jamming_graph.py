#from .node_path import * 
from .analog_schemes_aux import * 

DEFAULT_JAMMING_GRAPH_ALTER_NODE_RATIO_RANGE = [-0.2,0.2] 
DEFAULT_JAMMING_GRAPH_ALTER_EDGE_RATIO_RANGE = [-0.2,0.2]

DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE = [3,15] 
DEFAULT_JAMMING_GRAPH_TYPE_O_CONNECTIVITY_RANGE = [0.05,0.22] 

class JammingGraph: 

    def __init__(self,nodepath,modifiable_nodeset,prg,\
        is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None): 

        assert type(prg) in {MethodType,FunctionType}
        assert len(nodepath) >= 2 and len(set(nodepath.p)) == len(nodepath)  
        assert modifiable_nodeset.issubset(set(nodepath.p))
        assert is_valid_range(jam_nodesize_range,True,False) 

        self.npath = nodepath 
        self.modifiable_nodeset = modifiable_nodeset 
        self.prg = prg 
        self.is_directed = is_path_directed
        self.jam_nodesize_range = jam_nodesize_range 
        if type(ctr_function) != type(None): 
            assert type(ctr_function) in {MethodType,FunctionType}
            self.ctr_function = ctr_function
        else: 
            self.ctr_function = SimpleCounter(max(self.npath.p) + 1).__next__ 
        self.node2nodesets = defaultdict(list) 
        for k in self.modifiable_nodeset: 
            self.node2nodesets[k] = []  

        self.G = nodepath.to_graph(is_path_directed)

        return

    def one_jam(self,node,remove_original_node:bool):
        return -1 

    def entire_nodeset_for_node(self,q): 
        if q not in self.node2nodesets: 
            return {q} 
        return flatten_setseq(self.node2nodesets) 

    def alter_nodeset(self,disconnect_possible:bool):  
        nodes = set(self.node2nodesets.keys()) 
        if len(nodes) == 0: 
            return 

        i = int(self.prg()) % len(nodes) 
        n = nodes[i]
        if len(self.node2nodesets[n]) == 0: 
            return 

        j = int(self.prg()) % len(self.node2nodesets[n]) 
        self.alter_nodeset_(n,j,disconnect_possible)
        return

    def alter_nodeset_(self,base_node,nodeset_index,disconnect_possible:bool,max_edge_changes = 1000):  
        # graph_derivation(g:defaultdict,is_dsg:bool,node_change_ratio,edge_change_ratio,prg,ctr_function,\
        # max_edge_changes=float('inf'))

        nodeset = self.node2nodesets[base_node][nodeset_index] 
        # case: no alter 
        if len(nodeset) < 3: 
            return 

        G2 = MicroGraph(self.G).subgraph_by_nodeset_(nodeset).dg   
        
        nc_ratio = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_ALTER_NODE_RATIO_RANGE) 
        ec_ratio = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_ALTER_EDGE_RATIO_RANGE)  

        G3 = graph_derivation(deepcopy(G2),self.is_directed,nc_ratio,ec_ratio,self.prg,self.ctr_function,\
            max_edge_changes)
        self.node2nodesets[base_node][nodeset_index] = set(G3.keys())

        mg = MicroGraph(self.G) 
        mg = mg - MicroGraph(G2) 
        mg = mg + MicroGraph(G3)
        self.G = mg.dg 
        self.ensure_connected(base_node)
        return

    def ensure_connected(self,base_node): 

        # get the neighbors of base_node 
        left,right = self.neighbor_nodesets_to_base_nodeset(base_node)

        base_nodeset = self.entire_nodeset_for_node(base_node) 

        if type(left) != type(None): 
            q = self.entire_nodeset_for_node(left) 
            base_nodeset |= q 

        if type(right) != type(None): 
            q = self.entire_nodeset_for_node(right) 
            base_nodeset |= q  

        G2 = MicroGraph(self.G).subgraph_by_nodeset_(base_nodeset).dg   
        G3 = graph_to_one_component(G2,self.prg) 

        self.G = MicroGraph(self.G) + MicroGraph(G3) 
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

    def prng_choose_node_in_base_nodeset(self,base_node,choose_minimally_connected:bool): 
        q = self.entire_nodeset_for_node(base_node)
        if len(q) == 0: return None 
        q = sorted(q) 
        if not choose_minimally_connected: 
            i = int(self.prg()) % len(q) 
            return q[i] 
        
        G_ = MicroGraph(self.G).subgraph_by_nodeset_(q).dg 
        q = [(q_,len(G_[q_])) for q_ in q] 
        q = prg_seqsort_ties(q,self.prg,vf=lambda x: x[1])
        return q[0][0] 

    def nodeset_index_for_node(self,node): 
        for k,v in self.node2nodesets.items(): 
            for (i,v_) in enumerate(v): 
                if node in v_:
                    return (k,i)
        return None,None 

    def subgraph_edit(self,node,G): 
        # replace the direct nodeset 
        q0,q1 = self.nodeset_index_for_node(node)
        self.node2nodesets[q0][q1] = set(G.keys()) 

        # ensure entire nodeset of node is connected 
        G = MicroGraph(self.G).subgraph_by_nodeset_(self.entire_nodeset_for_node(node)).dg 
        G = graph_to_one_component(G,self.prg)

        # connect the new graph to neighbors 
        left,right = self.neighbor_nodesets_to_base_nodeset(node) 
        keys = sorted(G.keys())
        node_candidates = [(k,len(G[k])) for k in keys] 
        node_candidates = sorted(node_candidates,key=lambda x:x[1]) 
        
        left0 = node_candidates.pop(0)[0] 
        if len(node_candidates) == 0: 
            right0 = left0 
        else: 
            right0 = node_candidates.pop(0)[0] 

        if type(left) != type(None): 
            # choose a node 
            left_node = self.prng_choose_node_in_base_nodeset(left,choose_minimally_connected=True)
            G[left0] |= {left_node} 
            if not self.is_directed: G[left_node] |= {left0}

        if type(right) != type(None): 
            # choose a node 
            right_node = self.prng_choose_node_in_base_nodeset(right,choose_minimally_connected=True)
            G[right0] |= {right_node} 
            if not self.is_directed: G[right_node] |= {right0}

        self.G = (MicroGraph(self.G) + MicroGraph(G)).dg
        return


"""
Type (C)ircumvention of Jamming Graph, based on the principle of forming 
monotonically longer paths between two target nodes. 
"""
class JammingGraphTypeC(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg,is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None): 
        super().__init__(nodepath,modifiable_nodeset,prg,is_path_directed,jam_nodesize_range,ctr_function)
        return

    def one_jam(self,node,remove_original_node:bool):
        num_nodes = modulo_in_range(int(self.prg()),self.jam_nodesize_range) 
        assert num_nodes > 1 

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
            if _ not in G: 
                G[_] = set() 

            # get backward
            prev = node 
            for _ in range(num_backward): 
                q = self.ctr() 
                G[q] |= {prev} 
                if not self.is_directed: 
                    G[prev] |= {q}
                prev = q 
            if _ not in G: 
                G[_] = set() 
        
        self.subgraph_edit(node,G) 

"""
Type (O)bstruction of Jamming Graph, based on the principle of adding 
unwanted masses (obstruction in the form of subgraphs) between two target nodes. 
"""
class JammingGraphTypeO(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg,is_path_directed:bool,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE,ctr_function=None):
        super().__init__(nodepath,modifiable_nodeset,prg,is_path_directed,jam_nodesize_range,ctr_function)
        return

    def one_jam(self,node,remove_original_node:bool):

        num_nodes = modulo_in_range(int(self.prg()),self.jam_nodesize_range) 
        assert num_nodes > 1 

        is_realtime_gen = bool(int(self.prg()) % 2)
        edge_connectivity = modulo_in_range(self.prg(),DEFAULT_JAMMING_GRAPH_TYPE_O_CONNECTIVITY_RANGE)
        gg = GraphGen(self.is_directed,self.prg,is_realtime_gen,num_nodes,edge_connectivity)
        gg.full_run()
        G = gg.d 
        for _ in range(num_nodes): self.ctr() 

        if not remove_original_node: 
            ratio_conn = modulo_in_range(self.prg(),[0.05,0.3]) 
            num_conn = ceil(gg.keys() * ratio_conn)
            node_candidates = sorted(gg.keys())
            node_conn = prg_choose_n(node_candidates,num_conn,prg__single_to_int(self.prg),True)

            for x in node_conn: 
                G[node] |= {x} 
                if not self.is_directed: G[x] |= {node} 
        
        self.subgraph_edit(node,G) 
        return