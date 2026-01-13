import numpy as np 
from copy import deepcopy 

class AgentInfo:

    def __init__(self,info_type): 
        assert info_type in {str,int,float,\
            list,set,np.ndarray}  
        self.info_type = info_type
        self.info = None 
        self.last_info = None 
        return

    def __str__(self): 
        return str(self.info) 

    def __add__(self,s): 
        assert type(s) == self.info_type, "got {}".format(type(s)) 
        q = deepcopy(self)
        q.last_info = s 
        if type(q.info) == type(None): 
            if q.info_type == np.ndarray: 
                q.info = np.array([s]) 
            else: 
                q.info = s 
        elif q.info_type in {str,int,float}: 
            q.info += s 
        elif q.info_type == list: 
            q.info.append(s) 
        elif q.info_type == set: 
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

    def __str__(self): 
        S = ""
        for k,v in self.agent_info.items(): 
            S += str(k) + "\n" + str(v) + "\n\n" 
        return S 

    def add_agent(self): 
        self.add_agent_(self.c)
        self.c += 1 

    def add_agent_(self,idn): 
        assert idn not in self.agent_idns
        self.agent_idns.append(idn)
        self.agent_info[idn] = AgentInfo(self.info_type) 
        return 

    def update_info(self,idn,info): 
        if idn not in self.agent_idns:
            self.add_agent_(idn) 
        self.agent_info[idn] = self.agent_info[idn] + info 
        return

    def last_info_for_agent(self,idn): 
        if idn not in self.agent_idns: return None 
        return self.agent_info[idn].last_info 