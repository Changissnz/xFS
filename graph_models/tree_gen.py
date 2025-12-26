from .micrograph import * 
from morebs2.matrix_methods import is_valid_range 
from morebs2.numerical_generator import modulo_in_range
from morebs2.graph_basics import is_undirected_graph
from math import ceil 
from types import MethodType,FunctionType

DEFAULT_TREE_BRANCHING_RANGE = [1,8] 

# simple counter class for new node identifiers
class SimpleCounter: 

    def __init__(self,x): 
        self.x = x 
    
    def __next__(self):
        x2 = self.x 
        self.x += 1 
        return x2 

# TODO: test this. 
class TreeGen:

    def __init__(self,starting_nodeset = {0},is_dsg:bool=False,prg=None,branching_range=DEFAULT_TREE_BRANCHING_RANGE): 
        assert len(starting_nodeset) > 0 
        for x in starting_nodeset: assert type(x) == int 
        self.starting_nodeset = sorted(starting_nodeset)
        self.is_dsg = is_dsg 
        if type(prg) == type(None): 
            prg = default_std_Python_prng()
        assert type(prg) in {MethodType,FunctionType} 
        self.prg = prg 
        assert is_valid_range(branching_range,True,True)
        self.branching_range = branching_range
        self.ctr_function = SimpleCounter(max(self.starting_nodeset) + 1).__next__ 
        self.leaves = deepcopy(self.starting_nodeset)

        self.node_count = 0
        self.d = defaultdict(set)  
        self.preproc() 

    def preproc(self): 
        for x in self.starting_nodeset: 
            self.d[x] = set() 
            self.node_count += 1 
        return 

    def __next__(self): 
        assert len(self.leaves) > 0 

        q = int(self.prg()) % len(self.leaves) 
        leaf_node = self.leaves.pop(q) 

        num_new_leaves = modulo_in_range(int(self.prg()),self.branching_range) 
        
        leaves = {self.ctr_function() for _ in range(num_new_leaves)} 
        self.d[leaf_node] |= leaves 

        if not self.is_dsg: 
            for l in leaves: self.d[l] |= {leaf_node} 
        self.node_count += num_new_leaves
        self.leaves.extend(leaves) 
        return 
    

        