from quant.rstruct import * 
from quant.qstruct import * 
from morebs2.graph_basics import is_undirected_graph

"""
Respondent Network Bot. 

A querying framework by a <QStruct> onto a network of <RStruct> 
nodes. Objective is for <QStruct> to make all <RStruct> nodes 
"align" in answers to k questions. Alignment between <QStruct> 
and an <RStruct> is for them to have the same answers to the k 
questions. Conceptualization of this bot was written in a paper 
@ https://github.com/Changissnz/RNB/blob/main/info/t1.pdf . 

<QStruct> can execute one of two moves for every turn:
- F1-fix: question a node n on question k_i. Node's resistance 
          changes according to these two factors:
    = magnitude of contradiction between node answer and <QStruct>
      answer. 
    = the delegate nodes that n relies on for defense against the 
      force of <QStruct>'s questioning. 
- F2-fix: applied onto some node n_i. Node n_i cannot serve as a delegate 
  node for any other node afterwards. 
* default for F1-fix is for the resistance delta of n on question k_i
  to be
      |(answer of n on k_i) - (answer of <QStruct> on k_i)|
  if there are no delegate nodes for n on question k_i. 
* default requirement for a node n_j being a delegate for node n on 
  question k_i is 
      (answer of n_j on k_i) = (answer of n on k_i). 
* default delegation effect is if the delegate nodeset is at least size 1, 
  then the resistance delta is 0 (immunity for node n on question k_i). 
* a node n will attempt to delegate to other nodes by a breadth-first 
  search pattern. A weakness of this pattern is that if the neighbors of 
  edge distance 1 to node n cannot serve as delegates to n on k_i, then 
  any other node n_x also cannot serve as delegate, even though n_x and 
  n may share the same answer on k_i. 
* if node's resistance falls to 0 or below, <QStruct> aligns node by 
  force-feeding it <QStruct>'s wanted answers. Node also cannot serve as 
  a delegate to other nodes. 

------------------------------------------------------------------------

qstruct_open_info_mode := list, 4 x (0|1). 
            [0] -> delegation nodes known? 
            [1] -> feedback on resistance changes given? 
            [2] -> current node resistances known?
            [3] -> graph structure of <RStruct>s known? 
"""
class RNBot:

    def __init__(self,d:defaultdict,rstruct_map,q,delegation_rule,\
        delegation_effect_rule=default_delegation_effect,\
        qstruct_open_info_mode=(0,0,0,0),verbose:bool=True):

        assert is_undirected_graph(d) 
        for v in rstruct_map.values(): assert type(v) == RStruct 
        assert type(q) == QStruct
        assert type(delegation_rule) == DelegationRuleOperator
        assert type(delegation_effect_rule) in {MethodType,FunctionType}
        assert is_valid_rnb_info_mode(qstruct_open_info_mode)

        self.d = d 
        self.rstruct_map = rstruct_map
        self.qstruct = q 
        self.qstruct.verbose = verbose 
        self.delegation_rule = delegation_rule
        self.delegation_effect_rule = delegation_effect_rule 
        self.open_info = qstruct_open_info_mode 
        self.verbose = verbose 

        self.relay_basic_info_to_Q()

        self.fin_stat = False 

    @staticmethod 
    def generate_instance(num_nodes,resistance,num_questions,answer_objective,\
        answer_range,num_questions_to_vary,prg,start_node_idn,qstructgen_answer_type,\
        qstruct_open_info_mode=(0,0,0,0),verbose=True): 

        Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,\
            num_questions,answer_objective,answer_range,num_questions_to_vary,\
            prg,start_node_idn) 

        rs_map = Q[0] 
        qs0 = QStruct.generate_instance_from_RStructMap(rs_map,qstructgen_answer_type,prg) 
        qs0.set_info_mode(qstruct_open_info_mode)
        dro = DelegationRuleOperator(Q[1],d2=default_delegation)

        rnbot = RNBot(Q[1],rs_map,qs0,dro,qstruct_open_info_mode=qstruct_open_info_mode,\
            verbose=verbose) 
        return rnbot

    #------------------------------- preprocessing 

    def relay_basic_info_to_Q(self):
        D = self.rstruct_node_resistances()
        if self.verbose: 
            S = "-/" * 20 
            print("* loading starting node resistances\n\t{}\n{}".format(D,S))

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
        del_nodeset -= {n} 

        di = None 
        if self.open_info[0]: 
            di = len(del_nodeset) > 1

        self.qstruct.update(n,q,ans,di)
        self.relay_info_to_Q(n,q,ans,del_nodeset)

    def relay_info_to_Q(self,n,q,node_ans,del_nodeset): 
        if self.verbose: print("* F1 (node,question): ({},{})".format(n,q))

        x0 = None if not self.open_info[0] else del_nodeset 

        ans2 = self.qstruct.answer_(q) 
        ans_diff = abs(ans2 - node_ans)
        res_change = self.delegation_effect_rule(ans_diff,del_nodeset)

        # apply resistance change to node 
        self.rstruct_map[n].update_resistance(res_change) 

        if self.verbose: 
            print("* node answer: {}".format(node_ans))
            print("* delegate nodeset:\n\t{}".format(del_nodeset)) 
            print("* Q answer: {}\tdiff: {}".format(ans2,ans_diff)) 
            print("* resistance change: {}".format(res_change))
            print("* node resistance: {}".format(self.rstruct_map[n].resistance))
        
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
        
        X = self.qstruct.energy 
        self.qstruct.energy -= f2cost 
        if self.verbose: 
            print("* F2   node {} cost {}".format(n,f2cost)) 
            print("* energy   t_0={}  t_1={}".format(X,self.qstruct.energy))

        self.delegation_rule.add_no_delegation({n})
        self.qstruct.add_f2_fixed_nodes({n}) 

    #------------------------------- move methods 

    def __next__(self): 
        self.exec_QStruct_move()

        if self.verbose: 
            S = "-/"
            print(S * 20)
        return

    def exec_QStruct_move(self):
        if self.fin_stat: return 

        cat,info = self.qstruct.next_move()
        if type(cat) == type(None): 
            self.fin_stat = True 
            return 

        if self.verbose: 
            print("\t\tMoving\n")

        if cat in {"initial scan", "f1-fix node","scan node","partial scan"}:
            n,q = int(info[0]),int(info[1])
            self.exec_question(n,q) 
        else: 
            n = info 
            self.f2_fix_node(n)
        return

    def sim_status(self): 
        qstat = self.qstruct.energy > 0. 
        D = self.rstruct_node_resistances() 
        L = [] 
        for k,v in D.items(): 
            if v > 0.: 
                L.append(k) 
        L = sorted(L) 

        S = "\tQ is active?\n" + str(qstat) + "\n\n" 
        S += "\tActive <RStruct> Nodes:\n" + vector_to_string(L) 
        return  S