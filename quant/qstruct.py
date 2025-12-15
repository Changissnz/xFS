from .qstruct_aux import * 
from morebs2.matrix_methods import vector_to_string,string_to_vector
from morebs2.numerical_generator import modulo_in_range,prg__LCG,default_std_Python_prng,prg_seqsort_ties
from copy import deepcopy 
from collections import Counter,defaultdict 
from types import MethodType,FunctionType 

"""
info_mode := list, 4 x (0|1), used in RNBot. 
            [0] -> delegation nodes known? 
            [1] -> feedback on resistance changes given? 
            [2] -> current node resistances known?
            [3] -> graph structure of <RStruct>s known? 

"""
class QStruct:

    def __init__(self,dim,answers:dict,energy=float(10**5),\
        info_mode=(0,0,0,0),query_cost_func=default_QStruct_query_cost,\
        f2fix_cost_func=default_QStruct_F2FixCost_function(),prg=None):

        assert len(dim) == 2
        assert type(dim[0]) == type(dim[1]) 
        assert min(dim) > 0 and type(dim[0]) == int 
        assert dim[1] == len(answers) 
        assert type(energy) == float and energy > 0 
        assert type(query_cost_func) in {MethodType,FunctionType}
        assert type(f2fix_cost_func) in {MethodType,FunctionType}

        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        self.dim = dim 
        self.answers = answers 
        self.answer_keys = sorted(self.answers.keys())
        self.energy = energy  
        self.info_mode = None 
        self.set_info_mode(info_mode)
        self.querycost_func = query_cost_func
        self.f2fix_cost_func = f2fix_cost_func 
        self.prg = prg 
        self.init_mat() 

        # start up a move log, and load the first move 
        self.qsm_log = QSMoveLog() 
        self.load_first_move() 

    def __str__(self): 
        S = "ANSWERS" 
        S += str(self.answers) + "\n" 
        S += "\n" + "DELEGATION" + "\n" 
        S += str(self.drate)
        S += "\n" + "CONTRADICTION" + "\n" 
        S += str(self.crate)
        S += "\n" + "Q-FREQUENCY" + "\n" 
        S += str(self.frate)
        S += "\n" + "AVERAGE ANSWERS" + "\n" 
        S += str(self.arate)
        return S 

    def set_info_mode(self,info_mode): 
        assert is_valid_rnb_info_mode(info_mode)
        self.info_mode = info_mode 

    def answer_(self,q): 
        assert q in self.answer_keys 
        x = self.answers[q] 

        if type(x) != type(None): return x 

        index = self.answer_keys.index(q) 
        rs = self.arate[:,index]
        return np.mean(rs) 
    
    def init_mat(self): 
        # delegation rate
        self.drate = np.zeros(self.dim) 
        # contradiction rate 
        self.crate = np.zeros(self.dim) 
        # question frequency rate 
        self.frate = np.zeros(self.dim) 
        # average answers 
        self.arate = np.zeros(self.dim)  
        # resistance changes 
        self.rcrate = np.zeros(self.dim)

        # initial node resistances 
        self.in_resistances = None 
        # current node resistances 
        self.cn_resistances = None 
        # graph config for RStruct instances 
        self.graph_config = None 
        # set of terminated nodes 
        self.terminated_nodes = set() 
        # set of F2-fixed nodes 
        self.f2fixed_nodes = set()

        # extended delegation info 
        # node -> question idn -> delegate nodes 
        self.extended_delinfo = defaultdict(defaultdict) 
        return

    def update(self,node_idn,q_idn,answer,delegation_bool):
        q_index = self.answer_keys.index(q_idn) 

        # update energy from query 
        self.energy = self.energy + self.querycost_func(node_idn,q_idn) 

        del_stat = 0 
        if type(delegation_info) == bool: 
            del_stat = int(delegation_info) 
        else: 
            assert type(delegation_info) == type(None)

        self.frate[node_idn,q_index] += 1 
        f = self.frate[node_idn,q_index] 

        self.arate[node_idn,q_index] = \
            update_mean(self.arate[node_idn,q_index],answer,f)
        
        ans = self.answer_(q_idn) 
        diff = abs(answer - ans) 
        self.crate[node_idn,q_index] = \
            update_mean(self.crate[node_idn,q_index],diff,f) 

        self.drate[node_idn,q_index] = \
            update_mean(self.drate[node_idn,q_index],del_stat,f)  
        return diff  

    """
    D := dict,node idn -> resistance::(non-negative integer)
    """
    def load_initial_info(self,D,G): 
        assert len(D) == self.dim[0] 
        #assert set(D.keys()) == set(self.answer_keys), "{}\n{}".format(set(D.keys()),set(self.answer_keys))
        self.in_resistances = D 
        self.cn_resistances = deepcopy(D) 

        if type(G) != type(None): 
            assert self.info_mode[3]
            assert type(G) == defaultdict 
            self.graph_config = G 

    def accept_info(self,node_idn,q_idn,x0,x1,x2): 
        q_index = self.answer_keys.index(q_idn)

        if not self.info_mode[0]: 
            assert type(x0) == type(None) 
        else: 
            assert type(x0) == set 
            self.extended_delinfo[node_idn][q_index] = x0 
        
        if not self.info_mode[1]: 
            assert type(x1) == type(None) 
        else: 
            assert type(x1) == float 
            f = self.frate[node_idn,q_index] 
            self.rcrate[node_idn,q_index] = \
                update_mean(self.rcrate[node_idn,q_index],x1,f)   

        if not self.info_mode[2]: 
            assert type(x2) == type(None) 
        else: 
            assert type(x2) == dict 
            assert set(x2.keys()) == set(self.answer_keys) 
            self.cn_resistances = x2 
        return

    #------------------------ methods for sending out info on next move to RNBot 

    def next_move(self): 
        cat,info = self.qsm_log.run_active_move()

        if type(cat) == type(None): 
            self.follow_up_on_prev_move() 

    def load_first_move(self):
        category = "initial scan"
        additional_info = tuple(self.dim)
        self.qsm_log.load_QSMove(category,additional_info)
        return

    def follow_up_on_prev_move(self):
        return -1 

    def f1_or_f2_decision(self): 

        return -1 

    #------------------------ methods for analysis of nodes based on querying (F1-fix)  
    #------------------------ and F2-fix costs. 

    def f1_fix_review(self): 
        # collect into matrix 
        f1_mat = np.zeros((0,4)) 
        for n in range(self.dim[0]): 
            # case: inactive node 
            if n in self.terminated_nodes: 
                continue 

            q,query_cost,num_attempts = \
                self.expected_node_querybreak_cost(n)

            f1_mat = np.vstack((n,q,query_cost,num_attempts)) 

        # tie-breaker for best node 
        v = f1_mat[:,2] 
        v_max = np.max(v) 
        indices = np.where(v_max == v)[0]
        i = int(self.prg()) % len(indices)
        i = indices[i] 

        cheapest_f1_fix = f1_mat[i]
        return cheapest_f1_fix 

    def expected_node_querybreak_cost(self,n): 

        # subcases: current node resistances known|unknown   
        expected_node_resistance = self.cn_resistances[n] if self.open_info[2] else self.in_resistances[n]

        # resistance delta known 
        # case: get the question that yields the greatest change in resistance 
        if self.open_info[1]: 
            # get the min (max abs) of rc_row 
            rc_row = self.rcrate[n,:] 

                # choose the minimum index of min 
            m = np.min(rc_row) 
            indices = np.where(m == np.min(rc_row))[0]
            q_index = int(self.prg()) % len(indices) 
            q_index = indices[q_index] 
            q = self.answer_keys[q_index] 

            num_attempts,query_cost = info_on_query(expected_node_resistance,abs(m),self.querycost_func) 
            return q,query_cost,num_attempts 

        # resistance delta unknown 
        # case: choose random question since magnitude of contradiction of answer 
        #       is not entirely proportional to change of resistance 
        q_index = int(self.prg()) % len(self.answer_keys) 
        q = self.answer_keys[q_index] 

            # get the contradiction of (node,q_index) 
        contra = self.crate[n,q_index] 

        num_attempts,query_cost = info_on_query(expected_node_resistance,contra,self.querycost_func) 
        return q,query_cost,num_attempts 

    def f2_fix_review(self):
        f2_mat = np.zeros((0,2))
        for n in range(self.dim[0]): 
            if n in self.f2fixed_nodes:
                continue 
            cost = self.f2_fix_cost(n)
            f2_mat = np.vstack((n,cost)) 
        return f2_mat 

    def f2_fix_cost(self,n):  
        return self.f2fix_cost_func(self,n)

    @staticmethod 
    def generate_instance_from_RStructMap(rs_map,answer_type:str,prg=None,energy=float(10**5)):
        assert len(rs_map) > 0 
        assert answer_type in {"most frequent","random","none"}  

        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        # get the number of questions 
        l0 = set() 
        answer_keys = set() 
        answer_range = None 
        for v in rs_map.values(): 
            l0 |= {len(v.answers)}

            r0 = sorted(v.answers.keys())
            answer_keys |= {vector_to_string(r0)}
            answer_range = v.answers_range 

        assert len(l0) == 1 
        l0 = l0.pop() 
        answer_keys = answer_keys.pop() 
        answer_keys = string_to_vector(answer_keys)

        dim = (len(rs_map),l0)
        answers = dict()
        if answer_type == "random": 
            for k in answer_keys: 
                arange = answer_range[k] 
                x = int(prg())
                answers[k] = modulo_in_range(int(prg()),arange) 
        elif answer_type == "none": 
            for k in answer_keys: 
                answers[k] = None  
        else:

            vf = lambda x: x[1] 

            # key := question 
            # value := list<(answer,frequency)>
            d = defaultdict(Counter)
            for rs in rs_map.values(): 
                c2 = rs.answer_map() 
                for k,v in c2.items(): 
                    d[k][v] += 1 

            for k in answer_keys: 
                q = d[k] 
                q = [(k2,v2) for k2,v2 in q.items()] 
                q2 = prg_seqsort_ties(q,prg,vf)
                
                ans = q2[-1] 
                answers[k] = ans[0]

        return QStruct(dim,answers,prg=prg,energy=energy)
     