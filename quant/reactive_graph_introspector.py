from .graph_introspector import * 
from graph_models.reactive_simple_graph_rules import * 

class ReactiveGraphIntrospectorTypeCNO(GraphIntrospectorTypeCNO):

    def __init__(self,G,edge_cost_function,is_bfs,node2cyclical_outputter,\
        node_priority_function,rule_op,prg):  

        super().__init__(G,edge_cost_function,is_bfs,node2cyclical_outputter,\
            node_priority_function,prg) 

        assert type(rule_op) == RealtimeReactiveGraphRuleOperatorTypeS
        self.rule_op = rule_op 
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

        assert self.introspector.d == self.G 
        q = self.introspector.move_one()
        M,traversal_cost = self.log_one_traversal()

        # case: traversal process is still active 
        if not self.introspector.fin_stat: 
            self.exec_reaction() 

        self.cumulative_traversal_cost += traversal_cost 

        return M,ref,traversal_cost

    def exec_reaction(self): 
        edges = self.introspector.previous_edges
        self.rule_op.react(self.G,edges) 
        # ineff.
        self.rule_op.clean_up_rules(self.G) 


    @staticmethod
    def generate_instance(G,nodechange_range,edgechange_range,period_range,maintain_connectivity:bool,\
        is_rule_constant:bool,   node_weight_range,is_dsg,is_bfs,ascending_priority,cycle_length_range,prg):  

        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION #GraphIntrospectorTypeCNO.generate_edge_weight_function(G,prg,is_dsg,edge_weight_range)
        
        prg_ = prg__single_to_int(prg)
        node2cyclical_outputter = CumulativeNode2Cycle.generate_instance(set(G.keys()),cycle_length_range,prg_)

        node_priority_outputter = NodePriorityFunctionStruct.generate_instance(\
            G,node_weight_range,is_dsg,is_bfs,ascending_priority,prg)

        N = set(G.keys()) 
        rule_op = RealtimeReactiveGraphRuleOperatorTypeS(N,is_dsg,nodechange_range,\
            edgechange_range,period_range,maintain_connectivity,is_rule_constant,prg) 

        return ReactiveGraphIntrospectorTypeCNO(G,edge_cost_function,is_bfs,\
            node2cyclical_outputter,node_priority_outputter,rule_op,prg)