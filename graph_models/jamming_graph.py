#from .node_path import * 
from .analog_schemes_aux import * 

DEFAULT_JAMMING_GRAPH_ALTER_NODE_RATIO_RANGE = [-0.2,0.2] 
DEFAULT_JAMMING_GRAPH_ALTER_EDGE_RATIO_RANGE = [-0.2,0.2]

DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE = [3,15] 

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

        self.G = nodepath.to_graph(is_path_directed)

        return

    def one_jam(self,remove_original_node:bool):
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
        i = self.npath.p.index(base_node) 

        left,right = None,None 
        if i == 0: 
            right = self.npath.p[i+1] 
        elif i == len(self.npath) -1: 
            left = self.npath.p[i-1] 
        else: 
            left,right = self.npath.p[i-1],\
                    self.npath.p[i+1] 

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


"""
Type (C)ircumvention of Jamming Graph, based on the principle of forming 
monotonically longer paths between two target nodes. 
"""
class JammingGraphTypeC(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg): 
        super().__init__(nodepath,modifiable_nodeset,prg)
        return

    def one_jam(self,remove_original_node:bool):
        return -1 

"""
Type (O)bstruction of Jamming Graph, based on the principle of adding 
unwanted masses (obstruction in the form of subgraphs) between two target nodes. 
"""
class JammingGraphTypeO(JammingGraph): 

    def __init__(self,nodepath,modifiable_nodeset,prg):
        assert type(nodepath) == NodePath 
        self.npath = nodepath 
        self.modif

        return -1 

    def one_jam(self,remove_original_node:bool):
        return -1 