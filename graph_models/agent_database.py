import numpy as np 
from copy import deepcopy 

class AgentInfo:

    def __init__(self,info_type): 
        assert info_type in {str,int,float,\
            list,set,np.ndarray}  
        self.info_type = info_type
        self.info = None 
        return

    def __add__(self,s): 
        assert type(s) == self.info_type, "got {}".format(type(s)) 
        q = deepcopy(self)
        if type(q.info) == type(None): 
            if q.info_type == np.ndarray: 
                q.info = np.array([s]) 
            else: 
                q.info = s 
        elif type(s) in {str,int,float}: 
            q.info += s 
        elif type(s) == list: 
            q.info.extend(s) 
        elif type(s) == set: 
            q.info |= s 
        else: 
            q.info = np.vstack((q.info,s)) 
        return q 
    
class SimpleAgentDB:

    def __init__(self,info_type): 
        self.info_type = info_type
        self.agent_idns = [] 
        self.agent_info = dict() 
        self.c = 0 

    def add_agent(self): 
        self.agent_idns.append(self.c) 
        self.c += 1 

    def add_agent_(self,idn): 
        assert idn not in self.agent_idns
        self.agent_idns.append(idn)
        self.agent_info[idn] = AgentInfo(self.info_type) 
        return 

    def update_agent(self,idn,info): 
        assert idn in self.agent_idns 
        self.agent_info[idn] = self.agent_info[idn] + info 
        return