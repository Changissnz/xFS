from graph_models.bfs import * 
from graph_models.dfs import * 
from graph_models.node_to_cycle import * 
from graph_models.node_priority_function import * 
from morebs2.numerical_generator import prg_decimal

"""
Static Graph Introspector, Type (C)ylical (N)ode (O)utput. 

Used to traverse a static simple graph, by either the BFS or DFS algorithm. 
Traversal methodology is not identical to that of <BFSCache> (breadth-first search) 
or <DFSCache>, but revolving around BFS or DFS. There are some additional variables 
that alter this structure's traversal pattern. 

The boolean variables `edges_can_be_forgotten` and `ref_nodes_can_be_repeated` alter 
<XFSCache> traversal. 

    *`ref_nodes_can_be_repeated` == True*
- variable<reference_varcache> : can re-add previous reference node back to cache for 
    traveling again. 

    *`edges_can_be_forgotten` == True*
- variable<costfrom_table> : can delete (node from, node to) cost of travel. 
- variable<ref_neighbors_travelled> : can delete neighbors of reference travelled. 


At every node or set of nodes N travelled, outputs a map M, 

    M: n -> v; v a value from a cycle corresponding to node n in the 
    <Node2Cycle> instance, `node2output_function`. 
"""
class StaticGraphIntrospectorTypeCNO:  

    def __init__(self,G,edge_cost_function,is_bfs:bool,node2cyclical_outputter,\
        node_priority_outputter,edges_can_be_forgotten:bool,ref_nodes_can_be_repeated:bool,prg): 
        assert type(G) == defaultdict
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert type(is_bfs) == bool 
        assert type(node2cyclical_outputter) == Node2CycleOutputter
        assert type(node_priority_outputter) == NodePriorityFunctionStruct 
        assert type(edges_can_be_forgotten) == bool 
        assert type(ref_nodes_can_be_repeated) == bool 
        assert type(prg) in {MethodType,FunctionType} 

        if is_bfs: assert node_priority_outputter.output_type == "sequence"
        else: assert node_priority_outputter.output_type == "single" 

        self.G = G 
        self.edge_cost_function = edge_cost_function
        self.is_bfs = is_bfs 
        self.n2c_outputter = node2cyclical_outputter 
        self.np_outputter = node_priority_outputter
        self.edges_can_be_forgotten = edges_can_be_forgotten
        self.ref_nodes_can_be_repeated = ref_nodes_can_be_repeated
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

    """
    main method #1 

    return:
    [0] dict, node -> cyclical value 
    [1] reference node used to travel to next neighbors 
    [1] traversal cost for this timestamp 
    """
    def __next__(self): 
        assert type(self.introspector) != type(None)

        if self.introspector.fin_stat: 
            return dict() 

        # traverse one and log 
        ref = self.introspector.reference 

        q = self.introspector.move_one()
        M,traversal_cost = self.log_one_traversal()

        # determine whether to add ref back into cache
        self.add_ref_back_to_cache(ref) 

        # forget any edges? 
        self.forget_travelled_edges(self.introspector.previous_edges)
        return M,ref,traversal_cost

    #-------------------------------- logging edges + repeat node travel + forget travelled edges 

    def log_one_traversal(self): 
        edges = self.introspector.previous_edges

        d = {}
        traversal_cost = 0 
        for edge in edges: 
            x = edge[1] 
            c = self.register_node_contact(x)
            d[x] = c 
            traversal_cost += self.introspector.fetch_edge_cost(edge[0],edge[1]) 
        return d,traversal_cost

    def register_node_contact(self,n): 
        return self.n2c_outputter.node_to_output(n) 

    def add_ref_back_to_cache(self,ref_node): 
        if not self.ref_nodes_can_be_repeated: 
            return 

        d = prg_decimal(self.prg,[0.,1.])
        if d >= 0.5: 
            d2 = prg_decimal(self.prg,[0.,1]) 

            # at back
            if d2 >= 0.5: 
                self.introspector.reference_varcache.append(ref_node) 
            # at front 
            else: 
                self.introspector.reference_varcache.appendleft(ref_node) 
        return 

    def forget_travelled_edges(self,edges): 
        if not self.edges_can_be_forgotten: 
            return 

        for edge in edges: 
            v0,v1 = edge[0],edge[1] 

            # delete cost from? 
            if prg_decimal(self.prg,[0.,1.]) >= 0.5: 
                del self.introspector.costfrom_table[v0][v1] 
    
            # delete neighbors travelled? 
            if prg_decimal(self.prg,[0.,1.]) >= 0.5: 
                self.introspector.ref_neighbors_travelled[v0] = \
                    self.introspector.ref_neighbors_travelled[v0] - {v1} 

            if prg_decimal(self.prg,[0.,1.]) >= 0.5: 
                self.introspector.ref_neighbors_travelled[v1] = \
                    self.introspector.ref_neighbors_travelled[v1] - {v0} 
