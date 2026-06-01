
DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES = {"compatible characterization","third-party contra"} 

class AgentType2F3MMOContainer: 

    def __init__(self,agent_idn,mo_type,cat2label_map,compatibility_map,attribute_vec_info,agent_action_comp_map,prg):  
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
            assert 
            for k,v in agent_action_comp_map.items(): 
                q = set(v.keys()) 
                assert q == set(cat2label_map.keys())

                # category -> label -> compatibility 
                for k2,v2 in v2.items(): 
                    assert set(cat2label_map[k2].keys()) == set(cat2label_map[k2]) 
        else: 
            assert type(agent_action_comp_map) == type(None) 
            assert is_vector(attribute_vec_info[0]) 
            assert is_bounds_vector(attribute_vec_info[1])  
            self.attribute_vec = attribute_vec_info[0] 
            self.attribute_vec_bounds = attribute_vec_info[1] 

        assert type(prg) in {MethodType,FunctionType} 

        self.agent_idn = agent_idn 
        self.mo_type = mo_type 
        self.c2l_map = cat2label_map 
        self.comp_map = compatibility_map
        # agent idn -> category -> label -> r in [0.,1.]
        self.aa_comp_map == agent_action_comp_map
        self.prg = prg 

        # characterization of self 
        #   category -> label
        self.self_char = None 
        # characterization of other 
        #   other agent idn -> category -> label 
        self.other_char = dict() 

        # used for mo type "compatible characterization"
        # other agent idn -> list::(category,label,jstrength) 
        self.other_char_recv = defaultdict(list) 

        # used for mo type "third-party contra" 
        # other agent idn -> category -> label -> # of times where first relay results in successful execution
        self.success_exec_record_map = defaultdict()
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

    def characterize_agent(self,other_agent:AgentType2F3M): 
        d = self.char_map() 
        self.current_char[other_agent.idn] = d 
        return

    def char_map(self): 
        categories = sorted(self.c2l_map.keys()) 

        d = dict() 
        for c in categories: 
            c2 = self.independent_action(c) 
            d[c] = c2 
        return d 

    #------------------------------- for compatible characterization 

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
        D = [deepcopy(avec)]  
        L = [label] 
        
        other_labels = sorted(set(self.c2l_map[category]) - {label})  

        for ol in other_labels: 
            a = prg() 
            q = avec + a 
            v = vector_modulo_in_bounds(q,self.attribute_vec_bounds) 
            D.append(v) 
            L.append(ol) 

        D = np.array(D) 
        pscheme = int(prg_decimal(self.prg,[0.,1.]) >= 0.5 )
        rodc = RecursiveOneDimClassifier(D,L,prg=self.prg,pscheme=pscheme) 

        rodc.fit() 
        c = rodc.score_accuracy(D,L) 
        jstrength = c / len(D)

        other_agent.recv_justification(self,category,label,jstrength) 
        return 

    def recv_justification(self,other_agent:AgentType2F3M,category,label,jstrength): 
        self.other_char_recv[other_agent.idn].append((category,label,jstrength))

    #------------------------------- for third-party contra 

    """
    return: 
    - bool, ?permit `other_agent` to act by `label` of `category`?  
    """
    def approve_action(self,other_agent:AgentType2F3M,category): 
        assert category in self.c2l_map
        #assert label in self.c2l_map[category] 
        label = self.current_char[other_agent.idn][category] 

        prg = merge_two_prgs(self.prg,other_agent.prg,add) 
        d = prg_decimal(prg,[0.,1.]) 
        x = self.aa_comp_map[other_agent.idn][category][label] 
        return x <= d 

    """
    return: 
    - bool, ?trio-based decision to allow `actor_agent` to execute action `label` of `category? 
    """
    def recv_action_leak(self,actor_agent:AgentType2F3M,sender_agent:AgentType2F3M,category,sender_approval:bool): 
        
        approval = int(self.approve_action(actor_agent,category))
        if approval == 0: approval = -1 

        sender_approval = int(sender_approval) 
        if sender_approval == 0: sender_approval = -1 

        idn = actor_agent.idn 
        
        d0_weight = 2 * sender_approval * \
            sender_agent.mo_container.compatibility_with_agent(actor_agent) * \
            sender_agent.mo_container.aa_comp_map[idn][category][label] 

        d1_weight = approval * self.compatibility_with_agent(actor_agent) * self.aa_comp_map[idn][category][label]

        prg = merge_two_prgs(actor_agent.prg,sender_agent.prg) 
        prg = merge_two_prgs(prg,self.prg)

        d = prg_decimal(prg,[0.,1.]) 

        return d <= d0_weight + d1_weight

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
            self.success_exec_record_map[a_idn][category][label] = 1 
        else: 
            self.success_exec_record_map[a_idn][category][label] += 1 

        self.current_exec_map[a_idn].append((category,label,success_stat))

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
    def generate_three_instances(agent_idns):
        return -1 

"""
Agent Type 2 (F)aces 3 (M)otives. 

"""
class AgentType2F3M: 

    def __init__(self,idn,mo_container:AgentType2F3MMOContainer):    
        self.idn = idn 
        self.mo_container = mo_container

        # if "compatible characterization": 
        #   element := (category, executed label, agent 1 expected label, agent 2 expected label)
        # if "third-party contra": 
        #   element := (category, executed label, bool::success) 
        self.exec_record = [] 

    def support_for_agent_cl(self,a_idn,category,label): 
        return self.mo_container.aa_comp_map[a_idn][category][label]

    def attribute_vector(self): 
        return self.mo_container.attribute_vec 

    def mo_type(self): 
        return self.mo_container.mo_type 

    def cat_vec(self): 
        return sorted(self.mo_container.c2l_map.keys()) 

    def process_one(self,a1,a2):  

        self.characterize_self()
        self.characterize_agent(a1) 
        self.characterize_agent(a2) 
        mt = self.mo_type()

        if mt == "compatible characterization": 
            self.process_one__CC(a1,a2) 
        else: 
            self.process_one__3PC(a1,a2) 

    def process_one__CC(self,a1,a2): 
        self.other_char_recv.clear() 

        cats = self.cat_vec() 
        for c in cats: 
            self.mo_container.justify_char(a1,c) 
            self.mo_container.justify_char(a2,c) 
        return

    def process_one__3PC(self,a1,a2): 
        self.mo_container.current_exec_map.clear() 

        cats = self.cat_vec() 
        for c in cats: 
            self.process_one__3PC_(a1,a2,c)

    def process_one__3PC_(self,a1,a2,category):

        first_relay = self.mo_container.choose_first_relay__3PC(a1,a2,category)
        second_relay = a1 if r0 == a2 else a2 

        label = self.mo_container.self_char[category] 

        c = first_relay.mo_container.compatibility_with_agent(self.idn) 
        s = first_relay.support_for_agent_cl(self.idn,category,label) 
        s = s * c 

        prg = merge_two_prgs(self.prg,first_relay,add) 
        q = prg_decimal(prg,[0.,1.]) 

        sender_approval = q <= s 
        stat = first_relay.mo_container.recv_action_leak(self,second_relay,category,sender_approval)

        self.mo_container.update_success_count(first_relay.idn,category,label,stat)
        return

    def execute(self): 
        if self.mo_type() == "compatible characterization":
            self.mo_container.

        # used for mo type "compatible characterization"
        # other agent idn -> list::(category,label,jstrength) 
        self.other_char_recv = defaultdict(list) 

        # used for mo type "third-party contra" 
        # other agent idn -> category -> label -> # of times where first relay results in successful execution
        self.success_exec_record_map = defaultdict()
        # other agent idn -> list::(category,label,bool) 
        self.current_exec_map = defaultdict(list) 
        return  

class AgentType2F3MTrifecta: 

    def __init__(self,a0,a1,a2): 
        assert type(a0) == type(a1) == type(a2) == AgentType2F3M

        self.a0 = a0 
        self.a1 = a1 
        self.a2 = a2  
        return 

    def __next__(self): 

        return -1 