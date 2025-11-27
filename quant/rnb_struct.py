from .usg_controller import * 

class DelegationRuleOperator:

    def __init__(self,d,d2=None): 
        self.d = d 
        self.d2 = d2 
        return

    def delegate_from_node(self,n,q,rstruct_map): 
        if type(self.d2) == defaultdict:
            return -1#self.d2[n]
        return -1 

    def delegate_from_node__type1(self,n,q,rstruct_map):
        usg = USGController() 
        usg.set_new_search(False,n,self.d)

        stat = True 
        D = set()
        S = usg.searches[0]
        while stat: 
            usg.move_search(0) 
            if len(S.previous_edges) == 0 and len(S.reference_varcache) == 0: 
                stat = False 
                continue 

            X = [x[1] for x in S.previous_edges]
            D2 = set()
            D3 = set()
            for x in X: 
                stat2 = self.cmp_two_nodes_at_q(n,x,q,rstruct_map)
                if stat2: 
                    D2 |= {x} 
                else: 
                    D3 |= {x} 

            D |= D2 
            S.remove_nodeset_from_refvarcache(D3) 

            if len(S.reference_varcache) == 0:
                stat = False 

        return D 

    def cmp_two_nodes_at_q(self,n,n2,q,rstruct_map):
        a1 = rstruct_map[n].answers[q]
        a2 = rstruct_map[n].answers[q] 
        return self.d2(a1,a2) 

    @staticmethod
    def generate_delegation_rule__type1(prg):
        return -1 

class QStruct:

    def __init__(self,dim,answers:dict): 
        assert len(dim) == 2
        assert type(dim[0]) == type(dim[1]) 
        assert min(dim) > 0 and type(dim[0]) == int 
        self.dim = dim 
        self.answers = answers 
        self.init_mat() 
    
    def init_mat(self): 
        # delegation rate
        self.drate = np.zeros(self.dim) 
        # contradiction rate 
        self.crate = np.zeros(self.dim) 
        # question frequency rate 
        self.frate = np.zeros(self.dim) 
        # average answers 
        self.arate = np.zeros(self.dim)  
        return

    def update(self,node_idn,q_idn,answer):
        f = self.frate[node_idn,q_idn]
        self.frate[node_idn,q_idn] += 1 
        assert False 

class RStruct: 

    def __init__(self,node_idn,resistance:float,answers:dict,answer_objective:dict,prg):   
        self.node_idn = node_idn
        # question idn -> answer 
        self.answers = answers 
        # question idn -> 0|1|2
        self.answer_objective = answer_objective
        self.prg = prg 
        self.prev_feedback = 0 
        self.resistance = resistance 
        return

    def answer(self,question):
        return -1 
    
class RNet:

    def __init__(self,d:defaultdict,rstruct_map,q,delegation_rule,delegation_effect_rule):
        return -1