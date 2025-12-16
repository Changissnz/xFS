#from quant.rnb_struct import * 
from quant.rstruct import * 
from quant.qstruct import * 
from morebs2.graph_basics import is_undirected_graph

"""
Respondent Network Bot 

qstruct_open_info_mode := list, 4 x (0|1). 
            [0] -> delegation nodes known? 
            [1] -> feedback on resistance changes given? 
            [2] -> current node resistances known?
            [3] -> graph structure of <RStruct>s known? 
"""
class RNBot:

    def __init__(self,d:defaultdict,rstruct_map,q,delegation_rule,\
        delegation_effect_rule=default_delegation_effect,\
        qstruct_open_info_mode=(0,0,0,0)):

        assert is_undirected_graph(d) 
        for v in rstruct_map.values(): assert type(v) == RStruct 
        assert type(q) == QStruct
        assert type(delegation_rule) == DelegationRuleOperator
        assert type(delegation_effect_rule) in {MethodType,FunctionType}
        assert is_valid_rnb_info_mode(qstruct_open_info_mode)

        self.d = d 
        self.rstruct_map = rstruct_map
        self.qstruct = q 
        self.delegation_rule = delegation_rule
        self.delegation_effect_rule = delegation_effect_rule 
        self.open_info = qstruct_open_info_mode 

        self.relay_basic_info_to_Q()

        self.fin_stat = False 

    @staticmethod 
    def generate_instance(num_nodes,resistance,num_questions,answer_objective,\
        answer_range,num_questions_to_vary,prg,start_node_idn,qstructgen_answer_type,\
        qstruct_open_info_mode=(0,0,0,0)): 

        Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,\
            num_questions,answer_objective,answer_range,num_questions_to_vary,\
            prg,start_node_idn) 

        rs_map = Q[0] 
        qs0 = QStruct.generate_instance_from_RStructMap(rs_map,qstructgen_answer_type,prg) 
        dro = DelegationRuleOperator(Q[1],d2=default_delegation)

        rnbot = RNBot(Q[1],rs_map,qs0,dro,qstruct_open_info_mode=qstruct_open_info_mode)
        return rnbot

    #------------------------------- preprocessing 

    def relay_basic_info_to_Q(self):
        D = self.rstruct_node_resistances()
        G = self.d if self.open_info[3] else None 
        self.qstruct.load_initial_info(D,G) 

    #------------------------------ F1-fix methods 

    def rstruct_node_resistances(self): 
        D = dict() 
        for k,rs in self.rstruct_map.items():
            D[k] = rs.resistance 
        return D 

    def facilitate_question(self,n,q): 
        return self.delegation_rule.delegate_from_node(n,q,self.rstruct_map)

    def exec_question(self,n,q): 
        ans,del_nodeset = self.facilitate_question(n,q) 

        di = None 
        if self.open_info[0]: 
            di = int(len(del_nodeset) > 1)

        self.qstruct.update(n,q,ans,di)
        self.relay_info_to_Q(n,q,ans,del_nodeset)

    def relay_info_to_Q(self,n,q,node_ans,del_nodeset): 

        x0 = None if not self.open_info[0] else del_nodeset 

        ans2 = self.qstruct.answer_()
        ans_diff = abs(ans2 - node_ans)
        res_change = self.delegation_effect_rule(ans_diff,del_nodeset)

        # apply resistance change to node 
        self.rstruct_map[n].update_resistance(res_change) 
        
        # case: RStruct has been terminated. 
        if self.rstruct_map[n].resistance <= 0.: 
            self.delegation_rule.add_no_delegation({n}) 
            self.qstruct.add_terminated_nodes({n})

        # load up two variables for QStruct open info mode 
        x1,x2 = None,None 
        if self.open_info[1]: 
            x1 = res_change 

        if self.open_info[2]:
            x2 = self.rstruct_node_resistances() 
        self.qstruct.accept_info(n,q,x0,x1,x2)
        return

    #------------------------------ F2-fix methods 

    def f2_fix_node(self,n): 
        assert n in self.rstruct_map
        rs = self.rstruct_map[n] 
        f2cost = self.qstruct.f2_fix_cost(n)
        
        self.qstruct.energy -= f2cost 
        self.delegation_rule.add_no_delegation({n})
        self.qstruct.add_f2_fixed_nodes({n}) 

    #------------------------------- move methods 

    def __next__(self): 
        self.exec_QStruct_move()
        return

    def exec_QStruct_move(self):
        if self.fin_stat: return 

        cat,info = self.qstruct.next_move()
        if type(cat) == type(None): 
            self.fin_stat = True 
            return 

        if cat in {"initial scan", "f1-fix node"}:
            n,q = info[0],info[1]
            self.exec_question(n,q) 
        else: 
            self.f2_fix_node(n)
        return