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

Two activation types: 
- csum: cumulative sum 
- linexp: linear expression 

To register an input vector V_d, represented as a dictionary D: 
    
- linexp: 
    V_d * `n2mt_map` >= `lin_exp_value`. 
- csum: 
    for every minimum node value v of node n in `n2mt_map`, 
    D[n] >= v. 

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

    # NOTE: applicable only for `csum`
    def is_valid_activation(self,max_path,node_value_map): 
        if self.node_idn not in node_value_map: return False 

        # make sure all nodes of `node_value_map` reside in the 
        # max subpath leading up through `node_idn`. 
        X = max_path.p
        i = X.index(self.node_idn)
        sp = set(X[:i+1]) 
        stat = set(self.n2mt_map.keys()).issubset(sp) 
        if not stat: return False  

        if self.act_type == "linexp": return True 

        # ensure every min activation value in possible range for 
        # navigator 
        for k,v in self.n2mt_map.items(): 
            R = node_value_map[k] 
            if not R[0] <= v <= R[1]: 
                return False 

        return True 
                

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

G := defaultdict, base graph for <DirectedImplicationPath> 
node_value_map := dict, node idn -> range (csum) XOR float (linexp) 
node_act_function_map := dict, node idn -> NodeActivationFunctionTypeMT 
"""
class PathTypeDI(DirectedImplicationPath):  

    def __init__(self,G,node_value_map,node_act_function_map): 
        super().__init__(G) 
        assert type(relation) in {MethodType,FunctionType} 
        assert set(node_value_map.keys()) == set(G.keys())
        
        self.ptype = hg_objective_node_type(node_value_map) 
        assert type(self.ptype) != type(None) 
        assert set(G.keys()) == set(node_act_function_map.keys())

        one_type_only = set() 
        for v in node_act_function_map.values(): 
            assert type(v) == NodeActivationFunctionTypeMT
            one_type_only |= {v.act_type} 
            assert len(one_type_only) == 1 

        self.act_type = one_type_only.pop() 
        for na in node_act_function_map.values(): 
            assert na.is_valid_activation(self.min_paths[-1],node_value_map)

        self.nv_map = node_value_map
        self.node_act_function_map = node_act_function_map 
        self.navigator_path_record = [] 

        def reset(self): 
            self.navigator_path_record.clear() 

        def path_record_to_dict(self): 
            return {x[0]:x[1] for x in self.navigator_path_record} 

class ObjectivePathTypeDI(PathTypeDI):

    def __init__(self,G,node_value_map,node_act_function_map): 
        super().__init__(G,node_value_map,node_act_function_map)
        return

    def register(self,node_idn,value:float):  
        if len(self.navigator_path_record) == 0: 
            assert node_idn == self.h 

        if self.act_type == "csum": 
            r = self.nv_map[node_idn] 
            assert r[0] <= value <= r[1] 

        q = self.node_act_function_map[node_idn] 
        d = self.path_record_to_dict() 
        d[node_idn] = value 
        v,stat = q.register(d) 

        if stat: 
            self.navigator_path_record.append((node_idn,value)) 
        return v,stat 

class InadvertentPathTypeDI(PathTypeDI): 

    def __init__(self,G,node_value_map,node_act_function_map): 
        super().__init__(G,node_value_map,node_act_function_map)
        return -1 

    def auto_register(self,node_idn,value:float):  

        return -1 