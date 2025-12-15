from .graph_gen import * 
from .usg_controller import * 
from morebs2.numerical_generator import modulo_in_range,prg__LCG,default_std_Python_prng
from types import MethodType,FunctionType 
from collections import Counter 

def default_delegation(a,a2):
    return round(a-a2,5) == 0 

def default_delegation_effect(ans_diff,del_nodeset):
    assert ans_diff >= 0. 
    if len(del_nodeset) > 1: return 0 
    return -ans_diff 

#---------------------------------------------------------------------------------------------

# TODO: test 
class DelegationRuleOperator:

    """
    d := defaultdict, graph 
    d2 := function f: (delegating node answer,delegate candidate answer) --> bool
    """
    def __init__(self,d,d2=None): 
        self.d = d 
        self.d2 = d2 
        self.no_delegation = set() 
        return

    def delegate_from_node(self,n,q,rstruct_map): 
        return self.delegate_from_node_(n,q,rstruct_map) 

    def delegate_from_node_(self,n,q,rstruct_map):
        usg = USGController() 
        #print("SET NEW SEARCH: ",self.d)
        usg.set_new_search(False,n,self.d)

        stat = True 
        D = set()
        S = usg.searches[0]

        def type_2_delegation():
            nonlocal D 
            X = [x[1] for x in S.previous_edges]
            D2 = set()
            D3 = set()
            for x in X: 
                #print("\tcmp {}+{}".format(n,x)) 

                # case: node cannot be used as a delegate 
                if x in self.no_delegation: 
                    D3 |= {x} 
                    continue 

                stat2 = self.cmp_two_nodes_at_q(n,x,q,rstruct_map)
                if stat2: 
                    D2 |= {x} 
                else: 
                    D3 |= {x} 

            D = D | D2 
            S.remove_nodeset_from_refvarcache(D3) 
            return

        def ask_nodeset(): 
            nonlocal D 
            if len(D) == 0: return None 
            S = 0 
            for d in D: 
                rs = rstruct_map[d]
                ans = rs.answer_(q)
                S += ans 
            return S / len(D) 

        while stat: 
            ref = S.reference
            #print("MOVING")
            _,stat,_ = usg.move_search(0) 
            #print("STAT: ",stat)
            if not stat: 
                continue 

            type_2_delegation()
            if type(S.reference) == type(None): 
                stat = False 
        #print("n={},q={}, D={}".format(n,q,D)) 
        D |= {n} 
        return ask_nodeset(),D 

    def cmp_two_nodes_at_q(self,n,n2,q,rstruct_map):
        a1 = rstruct_map[n].answer_(q)
        a2 = rstruct_map[n2].answer_(q) 
        #print("ANS ",a1,a2) 
        return self.d2(a1,a2) 

    @staticmethod
    def generate_delegation_rule__type1(prg):
        return -1 

#---------------------------------------------------------------------------------------------


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

        def one_answers_range_dict(): 
            X = dict() 
            for i in range(num_questions):
                X[i] = deepcopy(answer_range)
            return X 

        def one_rnode(n_idn): 
            ans = one_answer_dict() 
            ans_range = one_answers_range_dict()
            return RStruct(n_idn,resistance,ans,answer_objective,ans_range,prg)  


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

    def answer_(self,question):
        assert question in self.answers
        
        # truth 
        if self.answer_objective == 0: 
            return self.answers[question] 

        arange = self.answers_range[question] 

        # lie 
        if self.answer_objective == 1:
            # left diff,right diff 
            ld,rd = abs(self.answers[question] - arange[0]),\
                    abs(self.answers[question] - arange[1]) 
            if ld > rd: 
                ans = arange[0]
            elif rd > ld: 
                ans = arange[1] 
            else: 
                ans = arange[self.tiebreaker_end] 
            return ans 

        # vary 
        return int(modulo_in_range(self.prg(), arange))

    def answer_map(self): 
        c = Counter() 
        for k in self.answers.keys(): 
            c[k] = self.answer_(k) 
        return c 

    def update_resistance(self,change): 
        assert change <= 0. 
        self.resistance += change 