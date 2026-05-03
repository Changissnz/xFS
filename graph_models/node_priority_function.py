# file containing fundamental sorting functions for neighbor sets, used to 
# graph traversal via BFS and DFS algorithms. 
from collections import defaultdict
from types import MethodType,FunctionType
from morebs2.numerical_generator import prg_seqsort_ties
from morebs2.matrix_methods import is_number 

"""
output_type := single|set, 
    single -> <DFSCache>,
    set -> <BFSCache>,
"""
def prng_node_priority_function_(prg,output_type):
    assert type(prg) in {MethodType,FunctionType} 
    assert output_type in {"single","sequence"}

    def f(ref_node,neighbor_set):   
        if len(neighbor_set) == 0: return set() 
        return prg_seqsort(sorted(neighbor_set),prg) 

    return f 

"""
Priority function for graph traversal, breadth-first search or depth-first search.

Can order nodes according to one of the following: 
- frequency (of traversing the node)
- weight (assigned at initialization) 

If `priority_type` is `weight` but no weight exists in `node_weights` for some 
node n_i, assigns n_i a weight equal to the frequency of its been travelled. 

Node traversal frequency is collected regardless of the `priority_type`. 
"""
class NodePriorityFunctionStruct: 

    def __init__(self,priority_type,output_type,node_weights = dict(),\
        is_ascending:bool=True,prg=None):   
        assert priority_type in {"frequency","weight"}
        assert output_type in {"single","sequence"}
        assert type(node_weights) == dict 
        for v in node_weights.values(): assert is_number(v) and v > 0 
        assert type(is_ascending) == bool 
        assert type(prg) in {type(None),MethodType,FunctionType} 

        self.priority_type = priority_type
        self.output_type = output_type 
        self.node_weights = node_weights 
        self.is_ascending = is_ascending
        self.prg = prg 

        self.node_frequency = defaultdict(int)
        return 

    def next_node(self,ref_node,neighbor_set): 
        self.node_frequency[ref_node] += 1 
        
        if len(neighbor_set) == 0: 
            if self.output_type == "sequence": return set() 
            return None 
        
        q = [(n,self.node_to_value(n)) for n in neighbor_set]
        if type(self.prg) == type(None): 
            q = sorted(q,key=lambda x:x[1]) 
        else: 
            q = prg_seqsort_ties(q,self.prg,vf=lambda x: x[1]) 

        if not self.is_ascending: q = q[::-1] 
        
        if self.output_type == "single": 
            return q[0][0]
        return [q_[0] for q_ in q]
    
    def node_to_value(self,n): 
        if self.priority_type == "frequency": 
            return self.node_frequency[n] 

        if n not in self.node_weights: 
            return self.node_frequency[n] 

        return self.node_weights[n] 

    @staticmethod 
    def generate_instance():
        return -1 