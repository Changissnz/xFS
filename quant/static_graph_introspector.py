from .graph_introspector import * 

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

    M: n -> v; n in N, v a value from a cycle corresponding to node n in the 
    <Node2Cycle> instance, `node2output_function`, 
and the cumulative travel cost from the reference node to N, the neighbor set of 
nodes travelled. 

See parent class<GraphIntrospectorTypeCNO> for details on important methods such as 
method<log_one_traversal>. 
"""
class StaticGraphIntrospectorTypeCNO(GraphIntrospectorTypeCNO):  

    def __init__(self,G,edge_cost_function,is_bfs:bool,node2cyclical_outputter,\
        node_priority_outputter,edges_can_be_forgotten:float,ref_nodes_can_be_repeated:float,prg): 

        super().__init__(G,edge_cost_function,is_bfs,node2cyclical_outputter,\
            node_priority_outputter,prg) 

        assert 0. <= edges_can_be_forgotten <= 1.  
        assert 0. <= ref_nodes_can_be_repeated <= 1.

        self.edges_can_be_forgotten = edges_can_be_forgotten
        self.ref_nodes_can_be_repeated = ref_nodes_can_be_repeated
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
            return dict(),None,0 

        # traverse one and log 
        ref = self.introspector.reference 

        q = self.introspector.move_one()
        M,traversal_cost = self.log_one_traversal()

        # determine whether to add ref back into cache
        self.add_ref_back_to_cache(ref) 
        # forget any edges? 
        self.forget_travelled_edges(self.introspector.previous_edges)

        self.cumulative_traversal_cost += traversal_cost 

        return M,ref,traversal_cost

    #-------------------------------- logging edges + repeat node travel + forget travelled edges 

    def add_ref_back_to_cache(self,ref_node): 
        d = prg_decimal(self.prg,[0.,1.])

        if d > self.ref_nodes_can_be_repeated: 
            return 

        d_ = prg_decimal(self.prg,[0.,1])
        if d_ > 0.5: return 

        d2 = prg_decimal(self.prg,[0.,1.]) 
        # front 
        if d2 >= 0.5: 
            self.introspector.reference_varcache.append(ref_node)
        else: 
            self.introspector.reference_varcache.appendleft(ref_node) 
        return 

    def forget_travelled_edges(self,edges): 

        d = prg_decimal(self.prg,[0.,1.])
        if d > self.edges_can_be_forgotten: 
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

    @staticmethod
    def generate_instance(G,node_weight_range,edge_weight_range,is_dsg,is_bfs,ascending_priority,cycle_length_range,\
        edges_can_be_forgotten:float,ref_nodes_can_be_repeated:float,prg): 

        edge_cost_function = GraphIntrospectorTypeCNO.generate_edge_weight_function(G,prg,is_dsg,edge_weight_range)

        prg_ = prg__single_to_int(prg)
        node2cyclical_outputter = Node2CycleOutputter.generate_instance(set(G.keys()),cycle_length_range,prg_)
        node_priority_outputter = NodePriorityFunctionStruct.generate_instance(\
            G,node_weight_range,is_dsg,is_bfs,ascending_priority,prg)

        return StaticGraphIntrospectorTypeCNO(G,edge_cost_function,is_bfs,node2cyclical_outputter,\
        node_priority_outputter,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg)