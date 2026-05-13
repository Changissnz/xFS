from .dir_imp_path import * 
from .hypergraph import * 

PATH_TYPE_DI_NODE_ACTIVATION_TYPES = {"linexp","csum"} 

def hg_objective_node_type(node_value_map): 

    numbers = 0 
    ranges = 0 
    for v in node_value_map.values(): 
        if is_valid_range(v): 
            #assert v[0] > 0. 
            ranges += 1 
        else: 
            #assert is_number(v) 
            numbers += 1 
        #assert numbers == 0 or ranges == 0 

    if numbers == 0 and ranges == 0: 
        return None 

    if numbers != 0 and ranges == 0: 
        return "linexp" 

    if numbers == 0 and ranges != 0: 
        return "csum" 

    return None 

"""
Node Activation Function, Type (M)inimum (T)hreshold. 

Associated with a node in <DirectedImplicationPath>. 
"""
class NodeActivationFunctionTypeMT:  

    def __init__(self,node_idn,activation_node_idn,n2mt_map,activation_type,lin_exp_value=None):  
        assert type(n2mt_map) in {dict,defaultdict} 
        for v in n2mt_map.values(): assert type(v) == float 
        assert node_idn in n2mt_map
        assert activation_type in PATH_TYPE_DI_NODE_ACTIVATION_TYPES 
        if activation_type == "linexp": assert float(lin_exp_value) == float
        self.node_idn = node_idn 
        self.activation_node_idn = activation_node_idn 
        self.n2mt_map = n2mt_map 
        self.act_type = activation_type 
        self.lin_exp_value = lin_exp_value 
        return

    def register(self,d):
        assert type(d) == defaultdict 

        if self.act_type == "linexp": 
            return self.register__linexp(d) 
        return self.register__csum(d) 

    def register__linexp(self,d): 

        c = 0 
        for k,v in self.n2mt_map.items(): 
            c = c + (v * d[k]) 
        return c, c >= self.lin_exp_value 

    def register__csum(self,d): 

        keys = sorted(self.n2mt_map.keys())  

        for k in keys: 
            v = self.n2mt_map[k] 
            if k not in d: 
                return k,False
            if d[k] < v: 
                return k,False 

        return None,True 

"""
Objective Path, Type (D)irected (I)mplication. 
"""
class PathTypeDI(DirectedImplicationPath):  

    def __init__(self,G,node_value_map,objective_float,node_min_threshold_map:dict): 
        super().__init__(G) 
        assert type(objective_float) == float    
        assert type(relation) in {MethodType,FunctionType} 

        assert set(node_value_map.keys()) == set(G.keys())
        
        self.ptype = hg_objective_node_type(node_value_map) 
        assert type(self.ptype) != type(None) 
        
        self.nv_map = node_value_map
        self.obj_float = objective_float
        self.R = relation 

class ObjectivePathTypeDI(PathTypeDI):

    def __init__(self):
        return -1 

class InadvertentPathTypeDI(PathTypeDI): 

    def __init__(self,G): 
        return -1 
