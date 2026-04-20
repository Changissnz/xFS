from morebs2.pa_derivative import * 

MOBILE_VECTOR_AGENT_ROLES = {"chaser","target"}

class MobileVectorAgent: 

    def __init__(self,v,role): 
        assert is_vector(v) 
        assert role in MOBILE_VECTOR_AGENT_ROLES
        return -1 