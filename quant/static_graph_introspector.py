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
"""
class StaticGraphIntrospectorTypeCNO(GraphIntrospectorTypeCNO):  

    def __init__(self,G,edge_cost_function,is_bfs:bool,node2cyclical_outputter,\
        node_priority_outputter,edges_can_be_forgotten:bool,ref_nodes_can_be_repeated:bool,prg): 

        super().__init__(G,edge_cost_function,is_bfs,node2cyclical_outputter,\
            node_priority_outputter,prg) 

        assert type(edges_can_be_forgotten) == bool 
        assert type(ref_nodes_can_be_repeated) == bool 

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
            return dict() 

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

    def run_n_rounds(self,n=float('inf')): 
        assert type(self.introspector) != type(None)

        while n > 0 and not self.introspector.fin_stat: 
            next(self) 
            n -= 1 


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

    @staticmethod
    def generate_instance(G,node_weight_range,edge_weight_range,is_dsg,is_bfs,ascending_priority,cycle_length_range,\
        edges_can_be_forgotten:bool,ref_nodes_can_be_repeated:bool,prg): 

        if type(edge_weight_range) == type(None): 
            edge_cost_function = DEFAULT_EDGE_COST_FUNCTION
        else: 
            gwg = GraphWeightGen(G,prg,is_dsg,edge_weight_range)
            edge_cost_function = gwg.weight_

        prg_ = prg__single_to_int(prg)
        node2cyclical_outputter = Node2CycleOutputter.generate_instance(set(G.keys()),prg_,cycle_length_range)
        node_priority_outputter = NodePriorityFunctionStruct.generate_instance(\
            G,node_weight_range,is_dsg,is_bfs,ascending_priority,prg)

        return StaticGraphIntrospectorTypeCNO(G,edge_cost_function,is_bfs,node2cyclical_outputter,\
        node_priority_outputter,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg)