
DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES = {"compatible characterization","third-party contra"} 

class AgentType2F3MMOContainer: 

    def __init__(self,agent_idn,mo_type,cat2label_map,compatibility_map,attribute_vec_info,agent_action_comp_map,prg):  
        assert mo_type in DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES
        assert len(cat2label_map) > 0 
        assert type(cat2label_map) in {dict,defaultdict} 
        for v in cat2label_map.values(): 
            assert type(v) == list 
            assert len(v) == len(set(v)) > 0 

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

        self.self_char = None 
        self.other_char = dict() 
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
            q = self.c2l_map[c] 
            i = int(self.prg()) % len(q) 
            c2 = q[i] 
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
    - Use a <RecursiveOneDimClassifier> to add noise to it. s
    """
    def justify_char(self,other_agent:AgentType2F3M, category): 
        '''
        RecursiveOneDimClassifier
            def __init__(self,D,L,prg=None,pscheme=0,verbose:bool=False): 
        ''' 
        print("?ass shit?")

        return -1 

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
        
        d0_weight = 2 * sender_approval * sender_agent.compatibility_with_agent(actor_agent) * sender_agent.aa_comp_map[idn][category][label] 
        d1_weight = approval * self.compatibility_with_agent(actor_agent) * self.aa_comp_map[idn][category][label]

        prg = merge_two_prgs(actor_agent.prg,sender_agent.prg) 
        prg = merge_two_prgs(prg,self.prg)

        d = prg_decimal(prg,[0.,1.]) 

        return d <= d0_weight + d1_weight

"""
Agent Type 2 (F)aces 3 (M)otives. 

"""
class AgentType2F3M: 

    def __init__(self,idn,mo_container:AgentType2F3MMOContainer):    
        self.idn = idn 
        self.mo_container = mo_container

    def attribute_vector(self): 
        return self.mo_container.attribute_vec 

class AgentType2F3MTrifecta: 

    def __init__(self): 

        return -1 