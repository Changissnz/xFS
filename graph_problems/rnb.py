from quant.rnb_struct import * 
from morebs2.graph_basics import is_undirected_graph

"""
Respondent Network Bot 
"""
class RNBot:

    def __init__(self,d:defaultdict,rstruct_map,q,delegation_rule,delegation_effect_rule=None):
        assert is_undirected_graph(d) 
        for v in rstruct_map.values(): assert type(v) == RStruct 
        assert type(q) == QStruct
        assert type(delegation_rule) == DelegationRuleOperator
        
        self.d = d 
        self.rstruct_map = rstruct_map
        self.qstruct = q 
        self.delegation_rule = delegation_rule

    @staticmethod 
    def generate_instance(num_nodes,resistance,num_questions,answer_objective,\
        answer_range,num_questions_to_vary,prg,start_node_idn,qstructgen_answer_type): 

        Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,\
            num_questions,answer_objective,answer_range,num_questions_to_vary,\
            prg,start_node_idn) 

        rs_map = Q[0] 
        qs0 = QStruct.generate_instance_from_RStructMap(rs_map,qstructgen_answer_type,prg) 
        dro = DelegationRuleOperator(Q[1],d2=default_delegation_function)

        rnbot = RNBot(Q[1],rs_map,qs0,dro)
        return rnbot

    def facilitate_question(self,n,q): 
        return self.delegation_rule.delegate_from_node__typeX(n,q,self.rstruct_map)