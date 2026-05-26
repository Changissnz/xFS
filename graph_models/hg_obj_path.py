from .dir_imp_path import * 
from .hypergraph import * 

PATH_TYPE_DI_NODE_ACTIVATION_TYPES = {"linexp","single"} 

"""
Node Activation Function, Type (M)inimum (T)hreshold. 

Associated with a node in <DirectedImplicationPath>. 

Two activation types: 
- single: node values are individually processed by function  
- linexp: linear expression 

To register an input vector V_d, represented as a dictionary D: 
    
- linexp: 
    V_d * `n2mt_map` >= `lin_exp_value`. 
- single: 
    for every minimum node value v of node n in `n2mt_map`, 
    D[n] >= v. 

"""
class NodeActivationFunctionTypeMT:  

    def __init__(self,node_idn,activation_node_idn,n2mt_map,activation_type,lin_exp_value=None):  
        assert type(n2mt_map) in {dict,defaultdict} 
        for v in n2mt_map.values(): assert type(v) == float 
        assert node_idn in n2mt_map
        assert activation_type in PATH_TYPE_DI_NODE_ACTIVATION_TYPES 
        if activation_type == "linexp": assert type(lin_exp_value) == float
        else: assert type(lin_exp_value) == type(None)
        self.node_idn = node_idn 
        self.activation_node_idn = activation_node_idn 
        # node -> min threshold (float) 
        self.n2mt_map = n2mt_map 
        self.act_type = activation_type 
        self.lin_exp_value = lin_exp_value 
        return

    def __str__(self): 
        x = "node idn: {}  type: {}  act. node idn: {}\n".format(self.node_idn,\
            self.act_type,self.activation_node_idn)

        x += "\n"
        q = sorted(self.n2mt_map.keys())
        for q_ in q: 
            x += "* {} : {}\n".format(q_,self.n2mt_map[q_])
        x += "\n"

        if self.act_type == "linexp": 
            x += "linear sum: {}\n".format(self.lin_exp_value)
        return x 

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
        ##print("NODE IDN {} ACTIVATION {}".format(self.node_idn,self.activation_node_idn))
        if self.act_type == "linexp": 
            return self.register__linexp(d) 
        return self.register__single(d) 

    def register__linexp(self,d): 

        c = 0 
        for k,v in self.n2mt_map.items(): 
            c = c + (v * d[k]) 
        #print("keys: {} / {}".format(sorted(d.keys()),sorted(self.n2mt_map.keys())))
        #print("S: {} / {}".format(c,self.lin_exp_value))
        return c - self.lin_exp_value, c >= self.lin_exp_value 

    def register__single(self,d): 

        keys = sorted(self.n2mt_map.keys())  

        for k in keys: 
            v = self.n2mt_map[k] 
            if k not in d: 
                return k,False
            if d[k] < v: 
                return k,False 

        return d[self.node_idn] - self.n2mt_map[k],True 

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

    @staticmethod 
    def generate_n2f_map_for_DirectedImplicationPath(dip:DirectedImplicationPath,\
        node_value_range_map,ratio_indirect_activation:float,prior_dependency_ratio:float,\
        activation_type:str,prg): 

        # get number of nodes with indirect activation (post-contact activation)
        max_indirect_activation = len(dip.G) - 2 
        num_indirect_activation = ceil(max_indirect_activation * ratio_indirect_activation) 
        print("INDIRECT ACTIVATION {} / {}".format(num_indirect_activation,len(dip.G))) 
        indirect_activated_nodes = [] 
        if num_indirect_activation > 0: 
            X = sorted(dip.spine().p[:-2]) 
            indirect_activated_nodes = prg_choose_n(X,num_indirect_activation,prg__single_to_int(prg),is_unique_picker=True)

        def dependencies_of_parent_node(p_idn): 
            i = None 
            for (j,x) in enumerate(extra_edges):
                if x[1] == p_idn:
                    i = j 
                    break 

            dependencies = set() 
            if type(i) == type(None): return dependencies

            while i < len(extra_edges): 
                x = extra_edges[i] 
                if x[1] == p_idn: 
                    x2 = extra_edges.pop(i) 
                    dependencies |= {x2[0]} 
                else: 
                    break 
            return dependencies 
    
        # get dependency sets for each node's `n2mt_map`
        S = dip.spine()
        extra_edges = [] 
        for (i,p) in enumerate(S.p): 
            for j in range(i): 
                extra_edges.append((S.p[j],p)) 
        q = ceil(prior_dependency_ratio * len(extra_edges)) 
        extra_edges = prg_choose_n(extra_edges,q,prg__single_to_int(prg),is_unique_picker=True)
        extra_edges = sorted(extra_edges,key = lambda x: x[1]) 

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
Path Type (D)irected (I)mplication. 

G := defaultdict, base graph for <DirectedImplicationPath> 
node_value_range_map := dict, node idn -> acceptable range for input 
node_act_function_map := dict, node idn -> NodeActivationFunctionTypeMT 
"""
class PathTypeDI(DirectedImplicationPath):  

    def __init__(self,G,node_value_range_map,node_act_function_map): 
        super().__init__(G) 
        assert set(node_value_range_map.keys()) == set(G.keys())
        for v in node_value_range_map.values(): 
            assert is_valid_range(v,True,False) or is_valid_range(v,False,False) 
            assert v[0] > 0 
        assert set(G.keys()) == set(node_act_function_map.keys())

        one_type_only = set() 
        for v in node_act_function_map.values(): 
            assert type(v) == NodeActivationFunctionTypeMT
            one_type_only |= {v.act_type} 
            assert len(one_type_only) == 1 
        self.act_type = one_type_only.pop()

        for na in node_act_function_map.values(): 
            assert na.is_valid_activation(self.spine(),node_value_range_map)

        self.nv_map = node_value_range_map
        self.node_act_function_map = node_act_function_map 
        self.navigator_path_record = [] 

        # [0] node -> [1] list::(previous travelled nodes of failure)
        # pending failures from [1] that activate when navigator reaches [0] 
        self.failure_record_map = defaultdict(list) 

    def display_node_functions(self):
        q = sorted(self.node_act_function_map.keys())
        for q_ in q: 
            print(self.node_act_function_map[q_]) 
            print("-------------------------------")

    def reset(self): 
        self.navigator_path_record.clear() 

    def path_record_to_dict(self): 
        return {x[0]:x[1] for x in self.navigator_path_record} 

    def info_for_node(self,n):
        assert n in self.node_act_function_map 
        q = self.node_act_function_map[n]  
        x = q.n2mt_map
        return x,q.lin_exp_value

    @staticmethod 
    def generate_instance(G,node_value_range_map,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,prg):  
        dip = DirectedImplicationPath(G)

        n2f_map = NodeActivationFunctionTypeMT.generate_n2f_map_for_DirectedImplicationPath(\
            dip,node_value_range_map,ratio_indirect_activation,prior_dependency_ratio,\
            activation_type,prg) 
        return PathTypeDI(G,node_value_range_map,n2f_map) 

"""
Subclass of <PathTypeDI>. 
"""
class ObjectivePathTypeDI(PathTypeDI):

    def __init__(self,G,node_value_map,node_act_function_map): 
        super().__init__(G,node_value_map,node_act_function_map)
        return

    """
    return: (0|1,?,?,?)

    - CASE 0: have to backtrack due to pending failures activating 
        - set::(backtracked nodes)
        - current location [after backtracking]
        - True: immediate effect 
    - CASE 1: other
        - difference between score and min. threshold score 
        - bool: ?success status?
        - bool: ?immediate effect? 
    """
    def register_advance(self,node_idn,value:float,verbose=False):  
        if verbose: 
            print("** navigator path record **")
            print(self.navigator_path_record)
            print() 

        # case: start, has to be head 
        if len(self.navigator_path_record) == 0: 
            assert node_idn == self.h 
        # case: check that this node is out-vertex of last node 
        else: 
            t = self.navigator_path_record[-1][0] 
            assert node_idn in self.G[t], "ERROR IN={} OUT={} \nGRAPH\n{}".format(t,node_idn,self.G) 

        # check that value fits required range for node 
        r = self.nv_map[node_idn] 
        assert r[0] <= value <= r[1], "got {},   {}".format(value,r) 

        # case: pending failures activate 
        backtracked_nodes,new_loc = self.process_pending_failure(node_idn) 
        if type(new_loc) != type(None):  
            return 0,backtracked_nodes,new_loc,True 

        q = self.node_act_function_map[node_idn] 
        d = defaultdict(float,self.path_record_to_dict())
        d[node_idn] = value 
        v,stat = q.register(d) 

            # immediate action 
        stat2 = True 

        # case: pass

        # case: register failure 
        if not stat:
            ##print("[!] registering failure")
            stat2 = self.register_failure(node_idn)

        # log node and value if pass or pending failure 
        if stat or not stat2: 
            self.navigator_path_record.append((node_idn,value))
        
        # case: immediate failure, forced to backtrack 
        if not stat and not stat2: 
            self.register_backtrack() 

        return 1,v,stat,stat2 

    def register_backtrack(self): 
        assert len(self.navigator_path_record) > 0 
        q = self.navigator_path_record.pop(-1)
        return q  

    def register_failure(self,node_idn): 
        # check if pending failure 
        q = self.node_act_function_map[node_idn] 
        
        immediate_fail = q.activation_node_idn == node_idn
        # case: pending failure 
        if not immediate_fail: 
            self.failure_record_map[q.activation_node_idn].append(node_idn) 
            ##print("AFTER {}: {}".format(node_idn,self.failure_record_map)) 

        return immediate_fail

    def process_pending_failure(self,node_idn):         
        q = self.failure_record_map[node_idn] 
        if len(q) == 0: 
            return set(),None 
        del self.failure_record_map[node_idn] 

        S = self.spine() 
        indices = [] 
        for q_ in q: 
            index = S.p.index(q_) 
            indices.append(index) 

        min_index = min(indices) 
        min_node_of_failure = S.p[min_index] 

        # go through travel history, choose index where 
        # min. node of failure occurs. 
        nprecord = [x[0] for x in self.navigator_path_record] 
        if min_node_of_failure not in nprecord: 
            return set(),None 
        index2 = nprecord.index(min_node_of_failure) 
        index2_ = index2 + 1 
        
        backtracked_nodes = set() 
        while index2_ < len(self.navigator_path_record): 
            q = self.navigator_path_record.pop(index2_) 
            backtracked_nodes |= {q[0]}

        return backtracked_nodes,min_node_of_failure 

    @staticmethod
    def generate_instance(G,node_value_range_map,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,prg):  

        ptdi = PathTypeDI.generate_instance(G,node_value_range_map,\
            ratio_indirect_activation,prior_dependency_ratio,\
            activation_type,prg)
        return ObjectivePathTypeDI(ptdi.G,ptdi.nv_map,ptdi.node_act_function_map)
