from .dir_imp_path import * 
from .hypergraph import * 

PATH_TYPE_DI_NODE_ACTIVATION_TYPES = {"linexp","csum"} 

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

    @staticmethod 
    def generate_instance(node_idn,prior_dependencies,node_value_range_map,activation_type,\
        max_path:NodePath,add_activation_node:bool,prg):
        
        i = max_path.p.index(node_idn) 
        subpath = set(max_path.p[:i]) 
        assert prior_dependencies.issubset(subpath) 

        # case: choose an activation node (node farther down `max_path` than `node_idn`)
        activation_node_idn = node_idn 
        if add_activation_node: 
            subpath = sorted(max_path.p[i+1:]) 
            if len(subpath) > 0: 
                j = int(prg()) % len(subpath)
                activation_node_idn = subpath[j] 

        prior_dependencies = sorted(prior_dependencies) 
        prior_dependencies.append(node_idn) 

        # assign weights 
        n2mt_map = dict()
        min_c,max_c = 0,0 
        for p in prior_dependencies: 
            r = node_value_range_map[p]
            q = modulo_in_range(prg(),r) 
            n2mt_map[p] = q 

            if activation_type == "linexp": 
                min_c += (q * r[0]) 
                max_c += (q * r[1]) 
        
        lin_exp_value = None 
        if activation_type == "linexp": 
            lin_exp_value = modulo_in_range(prg(),[min_c,max_c]) 

        return NodeActivationFunctionTypeMT(node_idn,\
            activation_node_idn,n2mt_map,activation_type,lin_exp_value=lin_exp_value)

    # NOTE: applicable only for `csum`
    """
    max_path := NodePath 
    node_value_map := dict, node idn -> acceptable range of input 
    """
    def is_valid_activation(self,max_path,node_value_map): 
        if self.node_idn not in node_value_map: return False 

        # make sure all nodes of `node_value_map` reside in the 
        # max subpath leading up through `node_idn`. 
        X = max_path.p
        i = X.index(self.node_idn)
        sp = set(X[:i+1]) 
        stat = set(self.n2mt_map.keys()).issubset(sp) 
        if not stat: return False  

        if self.act_type == "linexp": 
            min_c = 0 
            max_c = 0  
            for k,v in self.n2mt_map.items():             
                R = node_value_map[k] 
                min_c += (v * R[0]) 
                max_c += (v * R[1]) 
            return min_c <= self.lin_exp_value <= max_c 
            
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
        return c - self.lin_exp_value, c >= self.lin_exp_value 

    def register__csum(self,d): 

        keys = sorted(self.n2mt_map.keys())  

        for k in keys: 
            v = self.n2mt_map[k] 
            if k not in d: 
                return k,False
            if d[k] < v: 
                return k,False 

        return d[self.node_idn] - self.n2mt_map[k],True 

    @staticmethod 
    def generate_n2f_map_for_DirectedImplicationPath(dip:DirectedImplicationPath,\
        node_value_range_map,ratio_indirect_activation:float,prior_dependency_ratio:float,\
        activation_type:str,prg): 

        # get number of nodes with indirect activation (post-contact activation)
        max_indirect_activation = len(dip.G) - 2 
        num_indirect_activation = ceil(max_indirect_activation * ratio_indirect_activation) 
        indirect_activated_nodes = [] 
        if num_indirect_activation > 0: 
            X = sorted(dip.spine().p[:-2]) 
            indirect_activated_nodes = prg_choose_n(X,num_indirect_activation,prg__single_to_int(prg),is_unique_picker=True)

        # get dependency sets for each node's `n2mt_map`
        if prior_dependency_ratio == 0.: 
            extra_edges = [] 
        else: 
            extra_edges = dip.possible_extra_edges(prior_dependency_ratio,prg)
        extra_edges = sorted(extra_edges,key=lambda x:x[1]) 

        def dependencies_of_parent_node(p_idn): 
            i = None 
            for (j,x) in enumerate(extra_edges):
                if x[1] == p_idn:
                    i = j 
                    break 
            assert type(i) != type(None) 
            dependencies = set() 
            while i < len(extra_edges): 
                x = extra_edges[i] 
                if x[1] == p_idn: 
                    x2 = extra_edges.pop(i) 
                    dependencies |= {x2[0]} 
                else: 
                    break 
            return dependencies 

        S = dip.spine()

        # generate function for node, in order 
        nodes = sorted(dip.G.keys()) 
        n2f_map = dict()
        for n in nodes: 
            prior_dependencies = dependencies_of_parent_node(n) 
            stat = n in indirect_activated_nodes
            nf = NodeActivationFunctionTypeMT.generate_instance(\
                n,prior_dependencies,node_value_range_map,activation_type,\
                S,add_activation_node=stat,prg=prg) 
            n2f_map[n] = nf 
        return n2f_map 

"""
Objective Path, Type (D)irected (I)mplication. 

G := defaultdict, base graph for <DirectedImplicationPath> 
node_value_range_map := dict, node idn -> acceptable range for input 
node_act_function_map := dict, node idn -> NodeActivationFunctionTypeMT 
"""
class PathTypeDI(DirectedImplicationPath):  

    def __init__(self,G,node_value_range_map,node_act_function_map): 
        super().__init__(G) 
        assert type(relation) in {MethodType,FunctionType} 
        assert set(node_value_range_map.keys()) == set(G.keys())
        for v in node_value_range_map.values(): 
            assert is_valid_range(v,True,False) or is_valid_range(v,True,True) 
        assert node_type in PATH_TYPE_DI_NODE_ACTIVATION_TYPES 
        assert set(G.keys()) == set(node_act_function_map.keys())

        one_type_only = set() 
        for v in node_act_function_map.values(): 
            assert type(v) == NodeActivationFunctionTypeMT
            one_type_only |= {v.act_type} 
            assert len(one_type_only) == 1 
        self.act_type = one_type_only.pop()

        for na in node_act_function_map.values(): 
            assert na.is_valid_activation(self.spine(),node_value_map)

        self.nv_map = node_value_range_map
        self.node_act_function_map = node_act_function_map 
        self.navigator_path_record = [] 

        def reset(self): 
            self.navigator_path_record.clear() 

        def path_record_to_dict(self): 
            return {x[0]:x[1] for x in self.navigator_path_record} 

    @staticmethod 
    def generate_instance(G,node_value_range_map,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,prg):  
        dip = DirectedImplicationPath(G)

        n2f_map = NodeActivationFunctionTypeMT.generate_n2f_map_for_DirectedImplicationPath(\
            dip,node_value_range_map,ratio_indirect_activation,prior_dependency_ratio,\
            activation_type,prg) 
        return PathTypeDI(G,node_value_range_map,n2f_map) 

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

    @staticmethod
    def generate_instance(G,node_value_range_map,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,prg):  

        ptdi = PathTypeDI.generate_instance(G,node_value_range_map,\
            ratio_indirect_activation,prior_dependency_ratio,\
            activation_type,prg)
        return ObjectivePathTypeDI(ptdi.G,ptdi.nv_map,ptdi.node_act_function_map)

class InadvertentPathTypeDI(PathTypeDI): 

    def __init__(self,G,node_value_map,node_act_function_map,prg): 
        assert type(prg) in {MethodType,FunctionType}
        super().__init__(G,node_value_map,node_act_function_map)
        self.prg = prg 
        return

    def auto_register(self,node_idn,value:float):  
        return -1 

    @staticmethod
    def generate_instance(G,node_value_range_map,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,prg):  

        ptdi = PathTypeDI.generate_instance(G,node_value_range_map,\
            ratio_indirect_activation,prior_dependency_ratio,\
            activation_type,prg)
        return InadvertentPathTypeDI(ptdi.G,ptdi.nv_map,ptdi.node_act_function_map)