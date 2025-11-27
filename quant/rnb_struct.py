from .usg_controller import * 
from .graph_gen import * 
from morebs2.numerical_generator import modulo_in_range

# TODO: test 
class DelegationRuleOperator:

    """
    d := defaultdict, graph 
    d2 := defaultdict|(function f: (delegating node,node candidate) --> bool) 
    """
    def __init__(self,d,d2=None): 
        self.d = d 
        self.d2 = d2 
        return

    def delegate_from_node(self,n,q,rstruct_map): 
        if type(self.d2) == defaultdict:
            return self.delegate_from_node__typeX(n,q,rstruct_map,1)
        return self.delegate_from_node__typeX(n,q,rstruct_map,2) 

    def delegate_from_node__typeX(self,n,q,rstruct_map,dtype):
        assert dtype in {1,2}

        usg = USGController() 
        usg.set_new_search(False,n,self.d)

        stat = True 
        D = set()
        S = usg.searches[0]

        def type_1_delegation(ref): 
            X = set([x[1] for x in S.previous_edges])
            acc = self.d2[ref].intersection(X)  
            rej = X - acc 
            D |= acc 
            S.remove_nodeset_from_refvarcache(rej)

        def type_2_delegation():

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
            return

        while stat: 
            ref = S.reference
            usg.move_search(0) 
            if len(S.previous_edges) == 0 and len(S.reference_varcache) == 0: 
                stat = False 
                continue 

            if dtype == 1:
                type_1_delegation()
            else: 
                type_2_delegation()

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

    def __init__(self,node_idn,resistance:float,answers:dict,answer_objective:dict,answers_range:dict,prg):   
        self.node_idn = node_idn
        # question idn -> answer 
        self.answers = answers 
        # question idn -> 0|1|2
        # 0 := actual, 1 := lie, 2 := vary 
        self.answer_objective = answer_objective
        # question idn -> answer space 
        self.answers_range = answers_range 
        self.prg = prg 
        # 0 -> no feedback, -1 -> negative feedback, 1 -> positive feedback 
        self.prev_feedback = dict() 
        for k in self.answers: self.prev_feedback[k] = 0 

        self.resistance = resistance 
        # used in the case of `answer_objective` == 1 
        self.tiebreaker_end = int(self.prg()) % 2 
        return

    def cmp_answer(self,rstruct):
        assert type(rstruct) == RStruct 
        D = {} 
        D2 = set()
        for k,v in self.answers.items(): 
            if k in rstruct.answers:
                D[k] = v - rstruct.answers[k] 
            else: 
                D2 |= {k} 
        return D,D2 

    def __str__(self): 
        s = "node idn: {}\n".format(self.node_idn) 
        s += "answers: \n{}\n".format(self.answers) 
        s += "answer obj: \n{}\n".format(self.answer_objective) 
        s += "resistance: \n{}\n".format(self.resistance)  
        return s

    # TODO: test 
    """
    num_nodes := number of nodes in the network. 
    resistance := positive integer 
    num_questions := positive integer 
    answer_objective := 0|1|2 
    answer_range := integer range 
    num_questions_to_vary := integer, <= num_questions, uses `prg` for different answers. 
    """
    @staticmethod
    def generate_RStructGraph__type_uniform(num_nodes,resistance,num_questions,answer_objective,\
        answer_range,num_questions_to_vary,prg,start_node_idn:int=0): 

        assert num_nodes > 0 and type(num_nodes) == int 
        assert resistance > 0 
        assert num_questions > 0 and type(num_questions) == int 
        assert answer_objective in {0,1,2} 
        assert answer_range[0] < answer_range[1] and \
            type(answer_range[0]) == type(answer_range[1]) and \
            type(answer_range[0]) == int 
        assert type(num_questions_to_vary) == int and 0 <= num_questions_to_vary <= num_questions

        # declare the identifiers for uniform&varied answers 
        uniform_answers = [i for i in range(num_questions)] 
        varied_answers = [] 
        while num_questions_to_vary > 0: 
            i = int(prg()) % len(uniform_answers)
            varied_answers.append(uniform_answers.pop(i)) 
            num_questions_to_vary -= 1 

        # set uniform answers 
        uniform_answer_dict = dict()
        for u in uniform_answers: 
            uniform_answer_dict[u] = int(modulo_in_range(prg(),answer_range)) 

        def one_answer_dict():
            X = deepcopy(uniform_answer_dict) 
            for c in varied_answers: 
                X[c] = int(modulo_in_range(prg(),answer_range)) 
            return X 

        def one_rnode(n_idn): 
            ans = one_answer_dict() 
            return RStruct(n_idn,resistance,ans,answer_objective,answer_range,prg)  


        is_realtime_gen = bool(int(prg()) % 2)
        e0,e1 = prg(),prg() 
        if e0 > e1: e0,e1 = e1,e0 
        edge_connectivity = e0 / e1 

        # generate the graph 
        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
            vertex_degree=num_nodes,edge_connectivity=edge_connectivity)
        gg.full_run() 
        gg.isotransform(start_node_idn) 
        D = gg.d 

        # generate the 
        rstruct_map = dict() 
        for i in range(start_node_idn,start_node_idn+num_nodes):
            rstruct_map[i] = one_rnode(i) 
        return rstruct_map,D 

    def answer(self,question):
        assert question in self.answers
        
        return -1 
    
"""
Respondent Network Bot 
"""
class RNBot:

    def __init__(self,d:defaultdict,rstruct_map,q,delegation_rule,delegation_effect_rule):
        return -1