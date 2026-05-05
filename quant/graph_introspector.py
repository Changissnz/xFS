from graph_models.bfs import * 
from graph_models.dfs import * 
from graph_models.node_to_cycle import * 
from graph_models.node_priority_function import * 
from morebs2.numerical_generator import prg_decimal
from graph_models.graph_gen import * 

"""
Graph Introspector, Type (C)ylical (N)ode (O)utput. 

Parent class of 

"""
class GraphIntrospectorTypeCNO: 

    def __init__(self,G,edge_cost_function,is_bfs:bool,node2cyclical_outputter,\
        node_priority_outputter,prg): 

        assert type(G) == defaultdict
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert type(is_bfs) == bool 
        assert type(node2cyclical_outputter) == Node2CycleOutputter
        assert type(node_priority_outputter) == NodePriorityFunctionStruct 
        assert type(prg) in {MethodType,FunctionType} 

        if is_bfs: assert node_priority_outputter.output_type == "sequence"
        else: assert node_priority_outputter.output_type == "single" 

        self.G = G 
        self.edge_cost_function = edge_cost_function
        self.is_bfs = is_bfs 
        self.n2c_outputter = node2cyclical_outputter 
        self.np_outputter = node_priority_outputter
        self.prg = prg 

        self.starting_ref = None 
        self.introspector = None 
        self.cumulative_traversal_cost = 0 
        
        return


    """
    main method #2
    """
    def output_minpaths(self,num_paths_per_node:int):
        assert type(self.introspector) != type(None) 
        self.introspector.min_paths.clear() 

        self.introspector.store_minpaths(ns=None,num_paths=num_paths_per_node,\
            cost_func = sum, prg = self.prg) 

        return self.introspector.min_paths 

    """
    pre-main method 
    """
    def set_ref_node(self,r): 
        assert r in self.G 
        self.starting_ref = r 

        x = None 
        if self.is_bfs: 
            x = BFSCache(self.starting_ref,self.G,edge_cost_function=self.edge_cost_function,\
                nextnode_priority_function=self.np_outputter.next_node,no_duplicate_touch_nodes=False)
        else: 
            x = DFSCache(self.starting_ref,self.G,edge_cost_function=self.edge_cost_function,\
                search_head_type=1,nextnode_priority_function=self.np_outputter.next_node,\
                no_duplicate_touch_nodes=False)

        self.introspector = x 
        return

