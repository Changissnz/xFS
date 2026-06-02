from collections import defaultdict
from morebs2.numerical_generator import * 
from morebs2.onedimprt_classifier import *
from morebs2.pr2label import * 
from types import MethodType,FunctionType
from copy import deepcopy 

DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES = {"compatible characterization","third-party contra"} 
DEFAULT_AGENT_TYPE_2F3M_CC_JUSTIFICATION_LABEL2SAMPLE_SIZE = 17  

class AgentType2F3MMOContainer: 

    def __init__(self,agent_idn,mo_type,cat2label_map,compatibility_map,attribute_vec_info,agent_action_comp_map,prg,verbose=False):  
        assert mo_type in DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES
        assert len(cat2label_map) > 0 
        assert type(cat2label_map) in {dict,defaultdict} 
        for v in cat2label_map.values(): 
            assert type(v) == list 
            assert len(v) == len(set(v)) > 1  

        assert len(compatibility_map) > 0 
        for v in compatibility_map.values(): assert is_number(v) 

        self.attribute_vec = None 
        self.attribute_vec_bounds = None 

        if mo_type == "third-party contra": 
            assert type(attribute_vec_info) == type(None) 
            assert type(agent_action_comp_map) == dict 

            for k,v in agent_action_comp_map.items(): 
                q = set(v.keys()) 
                assert q == set(cat2label_map.keys())

                # category -> label -> compatibility 
                for k2,v2 in v.items(): 
                    assert set(cat2label_map[k2]) == set(v2.keys()) 
        else: 
            assert type(agent_action_comp_map) == type(None) 
            assert is_vector(attribute_vec_info[0]) 
            assert is_bounds_vector(attribute_vec_info[1]) 
            assert type(attribute_vec_info[2]) == int and attribute_vec_info[2] > 1  
            self.attribute_vec = attribute_vec_info[0] 
            self.attribute_vec_bounds = attribute_vec_info[1] 
            self.cc_justification_l2s_size = attribute_vec_info[2] 

        assert type(prg) in {MethodType,FunctionType} 
        assert type(verbose) == bool 

        self.agent_idn = agent_idn 
        self.mo_type = mo_type 
        self.c2l_map = cat2label_map 
        self.comp_map = compatibility_map
        # agent idn -> category -> label -> r in [0.,1.]
        self.aa_comp_map = agent_action_comp_map
        self.prg = prg 
        self.verbose = verbose 

        # characterization of self 
        #   category -> label
        self.self_char = None 
        # characterization of other 
        #   other agent idn -> category -> label 
        self.other_char = dict() 

        # used for mo type "compatible characterization"
        # other agent idn -> category -> (label,jstrength) 
        self.other_char_recv = dict()  

        # used for mo type "third-party contra" 
        # other agent idn -> category -> label -> # of times where first relay results in successful execution
        self.success_exec_record_map = defaultdict(None)
        # other agent idn -> list::(category,label,bool) 
        self.current_exec_map = defaultdict(list) 
        return 

    def compatibility_with_agent(self,other_agent:AgentType2F3M): 
        idn = other_agent.idn 
        assert idn in self.comp_map
        return self.comp_map[idn] 

    def independent_action(self,category):
        q = self.c2l_map[category] 
        i = int(self.prg()) % len(q) 
        return q[i] 

    def characterize_self(self): 
        self.self_char = self.char_map()

        if self.verbose: 
            C = self.cat_vec() 
            print("agent {} self-char:\n  {}".format(self.agent_idn,[(c,self.self_char[c]) for c in C]))

    def characterize_agent(self,other_agent:AgentType2F3M): 
        d = self.char_map() 
        self.other_char[other_agent.idn] = d 

        if self.verbose: 
            C = self.cat_vec() 
            print("agent {} characterizes {}:\n  {}".format(self.agent_idn,other_agent.idn,[(c,d[c]) for c in C]))

        return

    def char_map(self): 
        categories = self.cat_vec() 

        d = dict() 
        for c in categories: 
            c2 = self.independent_action(c) 
            d[c] = c2 
        return d 

    def cat_vec(self): 
        return sorted(self.c2l_map.keys()) 

    def selfchar_seq(self): 
        categories = self.cat_vec() 
        return [(c,self.self_char[c]) for c in categories] 

    def other_char_recv_category_info(self,category): 
        q = dict() 
        for k,v in self.other_char_recv.items(): 
            if category not in v: continue 
            q[k] = v[category] 
        return q 

    #------------------------------- for compatible characterization 

    def set_cc_dataset_justification_size(self,l): 
        assert type(l) == int and l > 1 
        self.cc_justification_l2s_size = l 

    @staticmethod
    def generate_justification_dataset(ref_vec,bounds_vec,ref_label,all_labels,samples_per_label,prg): 
        assert is_vector(ref_vec)
        assert is_bounds_vector(bounds_vec) 

        D = [deepcopy(ref_vec)]   
        L = [ref_label]  
        prg_ = prg__single_to_nvec(prg,len(ref_vec)) 

        def samples_for_label(label): 
            for _ in range(samples_per_label): 
                a = prg_() 
                q = ref_vec + a 
                v = vector_modulo_in_bounds(q,bounds_vec)  
                D.append(v) 
                L.append(label) 
          
        for x in all_labels: 
            samples_for_label(x) 

        D,L = np.array(D),np.array(L)
        return D,L 

    """
    A `justification` scheme using class<RecursiveOneDimClassifier> from project<morebs2>. 

    Justification process goes as follows: 
    - given the `other_agent`'s attribute vector V_t, justify characterization l of 
      `category` for `other_agent` by generating a sequence D of |category| - 1 additional 
      vectors. Each of these vectors of D is formed by using a `prg` to add noise to V_t, and 
      then assigned a unique label. 
    - Use a <RecursiveOneDimClassifier> to classify D. 
    - Accuracy of classifier is justification strength. 
    """
    def justify_char(self,other_agent:AgentType2F3M, category): 

        assert self.mo_type == "compatible characterization" 
        label = self.other_char[other_agent.idn][category]  
        prg = prg__single_to_nvec(self.prg,len(self.attribute_vec)) 

        avec = other_agent.attribute_vector() 

        all_labels = sorted(set(self.c2l_map[category]))
        D,L = AgentType2F3MMOContainer.generate_justification_dataset(avec,self.attribute_vec_bounds,\
            label,all_labels,self.cc_justification_l2s_size,self.prg)

        pscheme = int(prg_decimal(self.prg,[0.,1.]) >= 0.5 )
        rodc = RecursiveOneDimClassifier(D,L,prg=self.prg,pscheme=pscheme) 

        rodc.fit() 
        c = rodc.score_accuracy(D,L)
        jstrength = c / len(D)
        other_agent.mo_container.recv_justification(self,category,label,jstrength) 
        return 

    def recv_justification(self,other_agent_mo:AgentType2F3MMOContainer,category,label,jstrength): 
        if other_agent_mo.agent_idn not in self.other_char_recv: 
            self.other_char_recv[other_agent_mo.agent_idn] = dict() 
        self.other_char_recv[other_agent_mo.agent_idn][category] = (label,jstrength)

    def choose_char__CC(self,category):
        label = self.self_char[category]

        other_agents = sorted(self.other_char_recv.keys())
        assert len(other_agents) == 2 

        non_compat = ((1 - self.comp_map[other_agents[0]]) + (1 - self.comp_map[other_agents[1]])) / 2.0 
        V = [non_compat] 

        p0 = self.other_char_recv[other_agents[0]][category][1] 
        p1 = self.other_char_recv[other_agents[1]][category][1] 
        V.extend([p0,p1]) 

        V = [zero_div(v,non_compat+p0+p1,1/3) for v in V]
        A = [label,self.other_char_recv[other_agents[0]][category][0],self.other_char_recv[other_agents[1]][category][0]] 
        pr_vec = [(v,a) for (v,a) in zip(V,A)] 

        pr = prg_decimal(self.prg,[0.,1.])
        l = probability_to_label(pr_vec,pr)
        return l 

    def choose_char_seq__CC(self): 
        categories = self.cat_vec() 
        catseq = [] 

        for c in categories: 
            q = self.choose_char__CC(c)
            catseq.append((c,q)) 
        return catseq 

    #------------------------------- for third-party contra 

    """
    return: 
    - bool, ?permit `other_agent` to act by `label` of `category`?  
    """
    def approve_action(self,other_agent:AgentType2F3M,category): 
        assert category in self.c2l_map
        label = other_agent.mo_container.self_char[category] 

        prg = merge_two_prgs(self.prg,other_agent.prg(),add) 
        d = prg_decimal(prg,[0.,1.]) 
        x = self.aa_comp_map[other_agent.idn][category][label] 
        stat = x <= d 
        if self.verbose: 
            print("agent {} approves agent {} action {}? {}".format(self.agent_idn,other_agent.idn,(category,label),stat))  
        return stat 

    """
    For use by the first relay. 

    return: 
    - bool, ?trio-based decision to allow `actor_agent` to execute action `label` of `category? 
    """
    def recv_action_leak(self,actor_agent:AgentType2F3M,recv_agent:AgentType2F3M,category,sender_approval:bool): 
        
        approval = int(self.approve_action(actor_agent,category))
        if approval == 0: approval = -1 

        sender_approval = int(sender_approval) 
        if sender_approval == 0: sender_approval = -1 

        idn = actor_agent.idn 
        label = actor_agent.mo_container.self_char[category]

        d0_weight = 2 * sender_approval * \
            recv_agent.mo_container.compatibility_with_agent(actor_agent) * \
            recv_agent.mo_container.aa_comp_map[idn][category][label] 

        d1_weight = approval * self.compatibility_with_agent(actor_agent) * self.aa_comp_map[idn][category][label]

        prg = merge_two_prgs(actor_agent.prg(),recv_agent.prg(),add) 
        prg = merge_two_prgs(prg,self.prg,add) 

        d = prg_decimal(prg,[0.,1.]) 

        stat = d <= d0_weight + d1_weight
        if self.verbose: 
            print("\tacting agent {} executes? {}".format(actor_agent.idn,stat))
        return stat 

    def success_count(self,a_idn,category,label): 
        if a_idn not in self.success_exec_record_map: 
            return 0 
        
        if category not in self.success_exec_record_map[a_idn]: 
            return 0 
        
        if label not in self.success_exec_record_map[a_idn][category]: 
            return 0 

        return self.success_exec_record_map[a_idn][category][label] 

    def update_success_count(self,a_idn,category,label,success_stat:bool): 
        assert type(success_stat) == bool 

        s = int(success_stat)

        if a_idn not in self.success_exec_record_map: 
            self.success_exec_record_map[a_idn] = dict() 

        if category not in self.success_exec_record_map[a_idn]: 
            self.success_exec_record_map[a_idn][category] = dict() 
        
        if label not in self.success_exec_record_map[a_idn][category]: 
            self.success_exec_record_map[a_idn][category][label] = s  
        else: 
            self.success_exec_record_map[a_idn][category][label] += s  

        self.current_exec_map[category] = (a_idn,label,success_stat) 

    def choose_first_relay__3PC(self,a1,a2,category): 

        l = self.self_char[category] 

        s0 = self.success_count(a1.idn,category,l) 
        s1 = self.success_count(a2.idn,category,l) 

        d = zero_div(s0,s0+s1,0.5) 

        p = prg_decimal(self.prg,[0.,1.]) 

        if p <= d: 
            return a1 
        return a2

    @staticmethod
    def generate_c2l_map(num_categories,label_size_range,prg): 
        categories = [i for i in range(num_categories)] 
        cat2label_map = defaultdict(list)
        x = 0 
        for c in categories: 
            q = modulo_in_range(int(prg()),label_size_range)
            cat2label_map[c] = [i for i in range(x,x+q)] 
            x = x + q 
        return cat2label_map

    @staticmethod
    def generate_tri_relations_(ref_agent_idn,other_agent_idns,cat2label_map,prg): 
        assert len(other_agent_idns) == 2

        other_agent_idns = sorted(other_agent_idns)
        C = sorted(cat2label_map.keys()) 

        agent_action_comp_map = {} 

        for o in other_agent_idns: 
            agent_action_comp_map[o] = dict() 
            for c in C: 
                l = cat2label_map[c]
                agent_action_comp_map[o][c] = dict() 
                for l_ in l: 
                    agent_action_comp_map[o][c][l_] = prg_decimal(prg,[0.,1.])
        return agent_action_comp_map 

    @staticmethod 
    def generate_three_instances(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,prg): 

        if mo_type == "third-party contra": 
            assert type(attribute_bound_vec) == type(None) 
        else: 
            assert is_bounds_vector(attribute_bound_vec)

        # generate category-to-label map 
        c2l_map = AgentType2F3MMOContainer.generate_c2l_map(num_categories,label_size_range,prg)

        agent_idns = sorted(agent_idns) 

        container_seq = [] 
        for a in agent_idns: 
            prg0 = prg_to_prg__LCG_sequence(prg,1,modulo_in_range(prg(),[1.,5.]))[0] 
            other_agents = sorted(set(agent_idns) - {a})

            action_compatibility_map = None 
            attribute_vec_info = None 

            if mo_type == "third-party contra": 
                action_compatibility_map = AgentType2F3MMOContainer.generate_tri_relations_(a,other_agents,c2l_map,prg) 
            else: 
                vec = prg__single_to_nvec(prg,len(attribute_bound_vec))()
                vec = vector_modulo_in_bounds(vec,attribute_bound_vec)
                attribute_vec_info = (vec,attribute_bound_vec,DEFAULT_AGENT_TYPE_2F3M_CC_JUSTIFICATION_LABEL2SAMPLE_SIZE)

            compatibility_map = {} 
            for o in other_agents: 
                compatibility_map[o] = prg_decimal(prg,[0.,1.]) 

            atmc = AgentType2F3MMOContainer(a,mo_type,c2l_map,compatibility_map,attribute_vec_info,action_compatibility_map,prg0)
            container_seq.append(atmc) 
        return container_seq

"""
Agent Type 2 (F)aces 3 (M)otives. 

"""
class AgentType2F3M: 

    def __init__(self,idn,mo_container:AgentType2F3MMOContainer):    
        self.idn = idn 
        self.mo_container = mo_container

        # every element is a list. 
        # every element of that element is ... 
        # if "compatible characterization": 
        #   element1 := (category, expected label (of self), executed label (of self XOR from others))
        # if "third-party contra": 
        #   element1 := (category, expected label (of self), bool::success) 
        self.exec_record = [] 

    def set_verbosity(self,verbose): 
        self.mo_container.verbose = True

    def prg(self): 
        return self.mo_container.prg 

    def support_for_agent_cl(self,a_idn,category,label): 
        return self.mo_container.aa_comp_map[a_idn][category][label]

    def attribute_vector(self): 
        return self.mo_container.attribute_vec 

    def mo_type(self): 
        return self.mo_container.mo_type 

    def cat_vec(self): 
        return self.mo_container.cat_vec() 

    def preprocess_one(self,a1,a2): 
        self.mo_container.characterize_self()
        self.mo_container.characterize_agent(a1) 
        self.mo_container.characterize_agent(a2) 

    def process_one(self,a1,a2):  
        mt = self.mo_type()

        if mt == "compatible characterization": 
            self.process_one__CC(a1,a2) 
        else: 
            self.process_one__3PC(a1,a2) 

    def process_one__CC(self,a1,a2): 

        cats = self.cat_vec() 
        for c in cats: 
            self.mo_container.justify_char(a1,c) 
            self.mo_container.justify_char(a2,c) 
            if self.mo_container.verbose: 
                d = self.mo_container.other_char_recv_category_info(c)
                k = sorted(d.keys())
                d_ = [(k_,d[k_]) for k_ in k]
        return

    def process_one__3PC(self,a1,a2): 
        self.mo_container.current_exec_map.clear() 

        cats = self.cat_vec() 
        for c in cats: 
            self.process_one__3PC_(a1,a2,c)

    def process_one__3PC_(self,a1,a2,category):

        first_relay = self.mo_container.choose_first_relay__3PC(a1,a2,category)
        second_relay = a1 if first_relay == a2 else a2 

        label = self.mo_container.self_char[category] 

        c = first_relay.mo_container.compatibility_with_agent(self) 
        s = first_relay.support_for_agent_cl(self.idn,category,label) 
        s = s * c 

        prg = merge_two_prgs(self.prg(),first_relay.prg(),add) 
        q = prg_decimal(prg,[0.,1.]) 

        sender_approval = q <= s 
        stat = first_relay.mo_container.recv_action_leak(self,second_relay,category,sender_approval)

        self.mo_container.update_success_count(first_relay.idn,category,label,stat)
        return

    def execute(self): 
        x = self.mo_container.selfchar_seq()

        if self.mo_type() == "compatible characterization":
            y = self.mo_container.choose_char_seq__CC() 

            erecord = [] 
            for x_,y_ in zip(x,y): 
                c = x_[0]
                erecord.append((c,x_[1],y_[1]))
        else: 

            categories = self.cat_vec() 
            erecord = [] 
            for i,c in enumerate(categories): 
                # check current exec map 
                stat = self.mo_container.current_exec_map[c][2] 
                erecord.append(x[i] + (stat,)) 
        
        if self.mo_container.verbose: print("agent {} exec stat: {}".format(self.idn,erecord))

        self.exec_record.append(erecord)
        return  

class AgentType2F3MTrifecta: 

    # NOTE: does not perform parameter checks for any of the three agents
    def __init__(self,a0,a1,a2,verbose=False): 
        assert type(a0) == type(a1) == type(a2) == AgentType2F3M

        self.a0 = a0 
        self.a1 = a1 
        self.a2 = a2  
        self.set_verbosity(verbose) 
        return 

    def mo_type(self): 
        return self.a0.mo_container.mo_type 

    def set_verbosity(self,verbose:bool):
        assert type(verbose) == bool  
        self.verbose = verbose 
        for x in [self.a0,self.a1,self.a2]: 
            x.set_verbosity(self.verbose)

    def __next__(self): 
        q = [self.a0,self.a1,self.a2] 
        for q_ in q: q_.mo_container.other_char_recv.clear() 

        if self.verbose: print("--- \t\tAGENT PREPROCESS")
        for i in range(3): 
            self.agent_pproc(i,True) 
        
        if self.verbose: print("--- \t\tAGENT PROCESS")
        for i in range(3): 
            self.agent_pproc(i,False) 

        if self.verbose and self.mo_type() == "compatible characterization": 
            for q_ in q: 
                print("other characterizations for agent {}".format(q_.idn)) 
                cvec = q_.mo_container.cat_vec() 
                for c in cvec: 
                    x = q_.mo_container.other_char_recv_category_info(c)
                    print("category {} : {}".format(c,x))
                #print(q_.mo_container.other_char_recv) 
                print("\t* * * *\t") 

        if self.verbose: print("--- \t\tAGENT EXECUTION") 
        for q_ in q: q_.execute() 
        return 

    def agent_pproc(self,number,is_preproc:bool): 
        assert number in {0,1,2} 
        assert type(is_preproc) == bool 

        q = [self.a0,self.a1,self.a2] 
        x = q.pop(number) 

        if is_preproc: 
            x.preprocess_one(q[0],q[1]) 
        else: 
            x.process_one(q[0],q[1]) 

    @staticmethod 
    def generate_instance(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,prg): 
        mo_containers = AgentType2F3MMOContainer.generate_three_instances(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,prg)

        A = [] 
        for mo in mo_containers: 
            a = AgentType2F3M(mo.agent_idn,mo)
            A.append(a) 
        return AgentType2F3MTrifecta(A[0],A[1],A[2]) 