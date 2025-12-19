from .qstruct_aux import * 
from morebs2.matrix_methods import vector_to_string,string_to_vector
from morebs2.numerical_generator import modulo_in_range,prg__LCG,default_std_Python_prng,prg_seqsort_ties,prg_seqsort 
from copy import deepcopy 
from collections import Counter,defaultdict 
from types import MethodType,FunctionType 

"""
For use with Respondent Network Bot (see file<graph_problems.rnb>)

QStruct makes its decisions using one of three processes: 
- NFA#1 
- NFA#2 
- NFA#3
- repeating a prior <QSMoveLog> move (see method<load_prior_QSMoveLog>) 

In <QStruct>'s independent state (no prior <QSMoveLog> reference), its 
decision-making uses `NFA#1` or `NFA#2`. NFA#1 is not guaranteed to 
produce the cheapest solution. The procedure de-emphasizes the use of 
F2-fix moves due to the arbitrarily greater cost of an F2-fix in comparison 
to an F1-fix. NFA#2 is more stochastic and will lean towards F2-fixing 
nodes, depending on the PRNG it is given for going for that preference. 
NFA#3 prioritizes F2-fixes, and is more expensive on average than #1,#2. 
For cost-effectiveness of <QStruct>, NFA#3 should rarely be used. 

info_mode := list, 4 x (0|1), used in RNBot. 
            [0] -> delegation nodes known? 
            [1] -> feedback on resistance changes given? 
            [2] -> current node resistances known?
            [3] -> graph structure of <RStruct>s known? 

"""
class QStruct:

    def __init__(self,dim,answers:dict,energy=float(10**5),\
        info_mode=(0,0,0,0),query_cost_func=default_QStruct_query_cost,\
        f2fix_cost_func=default_QStruct_F2FixCost_function(),prg=None,\
        nfa_type=1,verbose=False):

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
        assert nfa_type in {1,2,3}

        self.dim = dim 
        self.answers = answers 
        self.answer_keys = sorted(self.answers.keys())
        self.energy = energy  
        self.info_mode = None 
        self.set_info_mode(info_mode)
        self.querycost_func = query_cost_func
        self.f2fix_cost_func = f2fix_cost_func 
        self.prg = prg 
        self.nfa_type = nfa_type
        self.verbose = verbose 
        self.init_mat() 

        # start up a move log, and load the first move 
        self.qsm_log = QSMoveLog() 
        self.load_first_move() 

        self.repeat_qsm_mode = False 

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
        # delegation rate, cumulative 
        self.drate = np.zeros(self.dim) 
        # contradiction rate, average
        self.crate = np.zeros(self.dim) 
        # question frequency rate, cumulative
        self.frate = np.zeros(self.dim) 
        # average answers, average
        self.arate = np.zeros(self.dim)  
        # resistance changes, most recent 
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

    '''
    NOTE: method does not check for `qsm_log` to be applicable to the same 
          initial <RNBot> configuration. 
    BUG: possible. 
    '''
    def load_prior_QSMoveLog(self,qsm_log:QSMoveLog):
        assert type(qsm_log) == QSMoveLog
        self.qsm_log_prior = qsm_log 
        self.repeat_qsm_mode = True 
        self.qsm_log.active_move = None 
        if len(self.qsm_log_prior.cache) > 0: 
            qsmove = self.qsm_log_prior.cache.pop(0)
            qsmove.reset() 
            self.qsm_log.active_move = qsmove 

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

        # calculate answers according to type 
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
    
    #----------------------------------------------------------------------------------------------

    def update(self,node_idn,q_idn,answer,delegation_bool):
        q_index = self.answer_keys.index(q_idn) 

        # update energy from query 
        X = self.energy 
        self.energy = self.energy - self.querycost_func(node_idn,q_idn) 
        
        if self.verbose: 
            print("* Q energy,  t_0={}  t_1={}".format(X,self.energy))

        del_stat = 0 
        if type(delegation_bool) == bool: 
            del_stat = int(delegation_bool) 
        else: 
            assert type(delegation_bool) == type(None)

        self.frate[node_idn,q_index] += 1 
        f = self.frate[node_idn,q_index] 

        self.arate[node_idn,q_index] = \
            update_mean(self.arate[node_idn,q_index],answer,f)
        
        ans = self.answer_(q_idn) 
        diff = abs(answer - ans) 
        self.crate[node_idn,q_index] = \
            update_mean(self.crate[node_idn,q_index],diff,f) 

        self.drate[node_idn,q_index] += del_stat 
        return diff  

    """
    D := dict,node idn -> resistance::(non-negative integer)
    """
    def load_initial_info(self,D,G): 
        assert len(D) == self.dim[0] 
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
            f = self.frate[node_idn,q_index]  
            self.rcrate[node_idn,q_index] = x1 

        if not self.info_mode[2]: 
            assert type(x2) == type(None) 
        else: 
            assert type(x2) == dict 
            assert set(x2.keys()) == set([i for i in range(self.dim[0])])
            self.cn_resistances = x2 
        return

    #------------------------ methods for sending out info on next move to RNBot 

    def next_move(self):
        if self.energy <= 0.:
            return None,None  
        return self.next_move_()

    def next_move_(self): 
        cat,info = self.qsm_log.run_active_move()

        if self.verbose: 
            print("~ " * 20)

        if type(cat) == type(None): 
            if self.verbose: print("Q following up on previous move")
            
            self.load_next_move() 
            cat,info = self.qsm_log.run_active_move() 

        if self.verbose: 
            print("\tQ active move info")
            print("\t\tshort")
            print("* ", cat)
            print("* ", info) 
            print("\t---------------")
            print("\t\tfull")
            print(self.qsm_log.active_move_str()) 

        if self.verbose: 
            print("~ " * 20)

        return cat,info 

    """
    loads next move into <QSMoveLog> 
    """
    def load_next_move(self): 
        if self.repeat_qsm_mode: 
            if len(self.qsm_log_prior.cache) > 0: 
                qsmove = self.qsm_log_prior.cache.pop(0) 
                qsmove.reset() 
                self.qsm_log.active_move = qsmove 
            else: 
                self.repeat_qsm_mode = False 

        if not self.repeat_qsm_mode: 
            if self.nfa_type == 1: 
                self.follow_up_on_prev_move() 
            elif self.nfa_type == 2: 
                self.follow_up_on_prev_move__type2() 
            else: 
                self.follow_up_on_prev_move__type3() 

    #------------------------------------------- methods for making decisions, loading moves 

    def load_first_move(self):
        category = "initial scan"
        additional_info = tuple(self.dim)
        self.qsm_log.load_QSMove(category,additional_info)
        return

    def load_partial_scan(self): 
        qx = sorted(set([i for i in range(self.dim[0])]) - self.terminated_nodes)
        if len(qx) == 0: return 

        category = "partial scan" 
        additional_info = (qx,self.dim[1]) 
        self.qsm_log.load_QSMove(category,additional_info)

    def f1_or_f2_decision(self): 
        f1_node_info = self.f1_fix_review()
        if type(f1_node_info) == type(None): return None 

        n,q = f1_node_info[0],f1_node_info[1]
        first_degree_delegates,f2_delegate_cost = \
            self.f2_nodeset_fix_for_target_node(n,q) 

        if type(first_degree_delegates) == type(None): 
            f1_node_info_ = (f1_node_info[0],f1_node_info[1],f1_node_info[3])
            self.qsm_log.load_QSMove("f1-fix node",f1_node_info_)
            return self.qsm_log.active_move 

        # case: make F1-fix move         
        if f1_node_info[2] <= f2_delegate_cost: 
            # (node index,question index,num attempts)
            f1_node_info_ = (f1_node_info[0],f1_node_info[1],f1_node_info[3])
            self.qsm_log.load_QSMove("f1-fix node",f1_node_info_)
        # case: make F2-fix move
        else: 
            self.qsm_log.load_QSMove("f2-fix nodeset",\
                [prg_seqsort(sorted(first_degree_delegates),self.prg),(n,q,f1_node_info[3])])
        return self.qsm_log.active_move 

    def f2_nodeset_fix_for_target_node(self,n,q): 

        m = self.f2_fix_review()

        if type(m) == type(None): 
            return None,None

        # determine the cost of F2-fixing delegate nodes of n. 
        first_degree_delegates = set() 

        # case: delegate nodes known. 
        if self.info_mode[0]: 
            del_nodes = self.extended_delinfo[n][q]
        #       subcase: graph structure known. F2-fix only the 
        #                1st degree neighboring delegate nodes
            if self.info_mode[3]: 
                # 1st degree neighbors 
                neighbors = self.graph_config[n]
                first_degree_delegates = neighbors.intersection(del_nodes) 
                if len(first_degree_delegates) == 0: 
                    return None,None
        #       subcase: graph structure unknown. 
        #                Absolute approach: attempt to F2-fix all 
        #                nodes. 
            else: 
                first_degree_delegates = set(m[:,0])
        
        # case: delegate nodes unknown. 
        else: 
        #       subcase: graph structure known.
        #                choose all neighbors of graph 
            if self.info_mode[3]: 
                first_degree_delegates = set(self.graph_config[n]) 
        #       subcase: graph structure unknown. 
        #       choose an arbitrary node to F2-fix
            else: 
                candidates = set([i for i in range(self.dim[0])]) - self.f2fixed_nodes 
                index = int(self.prg()) % len(candidates)
                del_node = sorted(candidates)[index]
                first_degree_delegates = set([del_node])

        f2_delegate_cost = 0 
        for m_ in m: 
            if m_[0] in first_degree_delegates:
                f2_delegate_cost += m_[1] 

        return first_degree_delegates,f2_delegate_cost 

    #--------------------------------------------- NFA#1 

    """
    NFA#1 for decision-making. 
    - virtually a DFA, except for some decisions made using a PRG. 

    NFA#1 is not guaranteed to make decisions that result in the cheapest solution 
    for <QStruct> instance to make an <RStruct> network align with it. 
    """
    def follow_up_on_prev_move(self):
        assert len(self.qsm_log.cache) > 0 

        prev_move = self.qsm_log.cache[-1] 

        if prev_move.category == "initial scan": 
            self.f1_or_f2_decision() 
            return 
        elif prev_move.category == "f1-fix node": 
            target_node = prev_move.additional_info[0]
            # check if target node has been broken 
            stat = target_node in self.terminated_nodes

            # scan active nodes to update feedback values
            if stat: 
                self.load_partial_scan() 
            # scan the target node to update feedback values 
            else: 
                num_questions = int(self.dim[1])
                self.qsm_log.load_QSMove("scan node",(target_node,num_questions))
            return
        elif prev_move.category == "scan node":
            self.f1_or_f2_decision() 
        elif prev_move.category == "partial scan": 
            self.f1_or_f2_decision() 
        else: 
            node = int(prev_move.additional_info[1][0])
            num_questions = self.dim[1] 
            self.qsm_log.load_QSMove("scan node",(node,num_questions))
            return
        return

    #--------------------------------------------- NFA#2

    def follow_up_on_prev_move__type2(self): 
        assert len(self.qsm_log.cache) > 0 
        prev_move = self.qsm_log.cache[-1] 

        i1,i2 = self.prg(),self.prg() 
        if prev_move.category == "f2-fix nodeset": 

            # case: f1-fix 
            if i1 < i2: 
                f1_node_info = self.f1_fix_review()
                f1_node_info_ = (f1_node_info[0],f1_node_info[1],f1_node_info[3])
                self.qsm_log.load_QSMove("f1-fix node",f1_node_info_)
            # case: f1|f2-fix 
            else: 
                self.f1_or_f2_decision() 
        elif prev_move.category == "f1-fix node": 
            self.load_partial_scan()
        else: 
            # case: f2-fix 
            if i1 < i2: 
                self.target_delegate_node_objective() 
            # case: f1|f2-fix 
            else: 
                self.f1_or_f2_decision() 
        return

    #------------------------------------------------- NFA #3 

    def follow_up_on_prev_move__type3(self): 
        assert len(self.qsm_log.cache) > 0 
        prev_move = self.qsm_log.cache[-1] 

        # choose F2-fix if available  
        if prev_move.category in {"initial scan","partial scan"}: 
            self.target_delegate_node_objective() 
        elif prev_move.category == "scan node": 
            n = prev_move.additional_info[0] 
            q,_,num_attempts = \
                self.expected_node_querybreak_cost(n)
            info = (n,q,num_attempts) 
            self.qsm_log.load_QSMove("f1-fix node",info)
        elif prev_move.category == "f2-fix nodeset":  
            self.target_delegate_node_objective() 
        else: 
            self.choose_random_node_for_scan()
            #self.f1_or_f2_decision()

    def choose_random_node_for_scan(self): 
        # choose a random node for "scan node" 
        candidates = sorted(set([i for i in range(self.dim[0])]) - self.terminated_nodes)
        if len(candidates) == 0: return 
        i = int(self.prg()) % len(candidates)
        target_node = candidates[i] 
        self.qsm_log.load_QSMove("scan node",(target_node,self.dim[1]))

    #------------------------ methods for analysis of nodes based on querying (F1-fix)  
    #------------------------ and F2-fix costs. 

    """
    return:
    - [0] cheapest node to F1-fix
      [1] question identifier 
      [2] expected cost of query until node broken
      [3] expected number of queries until node broken 
    """
    def f1_fix_review(self): 
        # collect into matrix 
        f1_mat = np.zeros((0,4)) 
        for n in range(self.dim[0]): 
            # case: inactive node 
            if n in self.terminated_nodes: 
                continue 

            q,query_cost,num_attempts = \
                self.expected_node_querybreak_cost(n)

            f1_mat = np.vstack((f1_mat,(n,q,query_cost,num_attempts)))
        if f1_mat.shape[0] == 0: 
            return None 
        

        # tie-breaker for best node 
        v = f1_mat[:,2] 
        v_min = np.min(v) 
        indices = np.where(v_min == v)[0]
        i = int(self.prg()) % len(indices)
        i = indices[i] 

        cheapest_f1_fix = f1_mat[i]
        return cheapest_f1_fix 

    def expected_node_querybreak_cost(self,n): 

        # subcases: current node resistances known|unknown   
        expected_node_resistance = self.cn_resistances[n] if self.info_mode[2] else self.in_resistances[n]

        # resistance delta known 
        # case: get the question that yields the greatest change in resistance 
        if self.info_mode[1]: 
            # get the min (max abs) of rc_row 
            rc_row = self.rcrate[n,:] 

                # choose a random index of min 
            m = np.min(rc_row) 
            indices = np.where(m == rc_row)[0]
            q_index = int(self.prg()) % len(indices) 
            q_index = indices[q_index] 
            q = self.answer_keys[q_index] 

            num_attempts,query_cost = info_on_query(n,q,expected_node_resistance,abs(m),self.querycost_func) 
            return q,query_cost,num_attempts 

        # resistance delta unknown 
        # case: choose random question since magnitude of contradiction of answer 
        #       is not entirely proportional to change of resistance 
        q_index = int(self.prg()) % len(self.answer_keys) 
        q = self.answer_keys[q_index] 

            # get the contradiction of (node,q_index) 
        contra = self.crate[n,q_index] 

        num_attempts,query_cost = info_on_query(n,q,expected_node_resistance,contra,self.querycost_func) 
        return q,query_cost,num_attempts 

    """
    return: np.array, k x 2, 
        column [0] -> node identifier 
        column [1] -> cost 
    """
    def f2_fix_review(self):
        f2_mat = np.zeros((0,2))
        for n in range(self.dim[0]): 
            if n in self.f2fixed_nodes:
                continue 
            if n in self.terminated_nodes:
                continue 

            cost = self.f2_fix_cost(n)
            f2_mat = np.vstack((f2_mat,(n,cost))) 
        
        if f2_mat.shape[0] == 0: 
            return None 
        return f2_mat 

        #------------------------------ used for NFA#2+3
    def most_frequent_delegate_active_node(self): 
        nodeset = set() 
        for n in range(self.dim[0]): 
            if n in self.f2fixed_nodes:
                continue 
            if n in self.terminated_nodes:
                continue 
            nodeset |= {int(n)} 
        
        if len(nodeset) == 0: return None 
        dfreq = self.delegation_frequency_for_nodeset(nodeset) 
        dfreq = [(k,v) for k,v in dfreq.items()] 
        vf = lambda x: x[1] 
        dfreq = prg_seqsort_ties(dfreq,self.prg,vf) 

        q = dfreq.pop(-1) 
        return q[0] 
    
    def delegation_frequency_for_nodeset(self,nodeset): 
        D = defaultdict(int)
        for n in nodeset: D[n] = 0 
        for n,Q in self.extended_delinfo.items(): 
            for q_,ns in Q.items(): 
                I = ns.intersection(nodeset) 
                for n2 in I: 
                    D[n2] += 1 
        return D 

    def target_delegate_node_objective(self): 
        n = self.most_frequent_delegate_active_node()
        if type(n) == type(None): 
            f1_node_info = self.f1_fix_review()
            if type(f1_node_info) == type(None): 
                return 
            f1_node_info_ = (f1_node_info[0],f1_node_info[1],f1_node_info[3])
            self.qsm_log.load_QSMove("f1-fix node",f1_node_info_)
        else: 
            self.qsm_log.load_QSMove("f2-fix nodeset",\
            ([n],(n,0,1))) 

    def f2_fix_cost(self,n):  
        return self.f2fix_cost_func(self,n)

    #--------------------------------- update methods for terminated nodes, F2-fixed nodes 

    def add_terminated_nodes(self,nodeset): 
        self.terminated_nodes |= nodeset 

    def add_f2_fixed_nodes(self,nodeset): 
        self.f2fixed_nodes |= nodeset  