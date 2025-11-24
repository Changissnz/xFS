import numpy as np 

class QStruct:

    def __init__(self,dim,answers:dict): 
        assert len(dim) == 2
        assert type(dim[0]) == type(dim[1]) 
        assert min(dim) > 0 and type(dim[0]) == int 
        self.dim = dim 
        self.answers = answers 
        self.init_mat() 
    
    def init_mat(self): 
        # delegation rate
        self.drate = np.zeros(self.dim) 
        # contradiction rate 
        self.crate = np.zeros(self.dim) 
        # question frequency rate 
        self.frate = np.zeros(self.dim) 
        # average answers 
        self.arate = np.zeros(self.dim)  
        return

    def update(self,node_idn,q_idn,answer):
        f = self.frate[node_idn,q_idn]
        self.frate[node_idn,q_idn] += 1 

class RStruct: 

    def __init__(self,node_idn,answers:dict,answer_objective:dict):  
        self.node_idn = node_idn
        self.answers = answers 
        self.answer_objective = answer_objective
        return
    
class RNet:

    def __init__(self,d:dict,rstruct_map,q):

        return -1 