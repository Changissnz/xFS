
DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES = {"compatible characterization","third-party contra"} 

class AgentType2F3MMOContainer: 

    def __init__(self,agent_idn,mo_type,cat2label_map,compatibility_map):
        assert mo_type in DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES
        assert len(cat2label_map) > 0 
        assert type(cat2label_map) in {dict,defaultdict} 
        for v in cat2label_map.values(): assert type(v) == list 

        assert len(compatibility_map) > 0 
        for v in compatibility_map.values(): assert is_number(v) 

        self.agent_idn = agent_idn 
        self.mo_type = mo_type 
        self.c2l_map = cat2label_map 
        self.comp_map = compatibility_map
        return 

    def characterize_(self,other_agent:AgentType2F3M,category): 
        assert type(other_agent) == AgentType2F3M
        assert other_agent != self 
        assert other_agent.idn in self.comp_map 


    def justify(self,other_agent:AgentType2F3M): 

        return -1 

"""
Agent Type 2 (F)aces 3 (M)otives. 


"""
class AgentType2F3M: 

    def __init__(self,idn,mo_container:AgentType2F3MMOContainer):    
        self.idn = idn 
        self.mo_container = mo_container