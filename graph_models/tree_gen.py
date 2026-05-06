from .micrograph import * 
from morebs2.matrix_methods import is_valid_range 
from morebs2.numerical_generator import modulo_in_range
from morebs2.graph_basics import is_undirected_graph
from math import ceil 
from types import MethodType,FunctionType

DEFAULT_TREE_BRANCHING_RANGE = [1,8] 

# NOTE: does not check if G is actually a tree or not. 
class SimpleTreeContainer: 

    def __init__(self,G:defaultdict,root_nodeset,leave_nodeset):  
        assert type(G) == defaultdict 
        assert type(root_nodeset) == set == type(leave_nodeset) 

        self.G = G 
        self.root_nodeset = root_nodeset
        self.leave_nodeset = leave_nodeset
        return

# TODO: test this. 
class TreeGen:

    def __init__(self,starting_nodeset = {0},is_dsg:bool=False,prg=None,branching_range=DEFAULT_TREE_BRANCHING_RANGE,\
        growth_type="distributed"):  
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

        assert growth_type in {"distributed","ordered"} 
        self.growth_type = growth_type
        self.ctr_function = SimpleCounter(max(self.starting_nodeset) + 1).__next__ 
        self.leaves = deepcopy(self.starting_nodeset)
        self.leaves_partitioned = [deepcopy(self.starting_nodeset)]  

        self.node_count = 0
        self.d = defaultdict(set)  
        self.preproc()
        self.num_new_leaves = None  

    def to_tree_container(self): 
        return SimpleTreeContainer(self.d,self.starting_nodeset,self.leaves) 

    def preproc(self): 
        for x in self.starting_nodeset: 
            self.d[x] = set() 
            self.node_count += 1 
        return 

    def set_number_of_new_leaves(self,num_leaves): 
        assert type(num_leaves) == int and num_leaves > 0 
        self.num_new_leaves = num_leaves  

    def __next__(self): 
        assert len(self.leaves) > 0 

        leaf_node = self.choose_leaf_node() 

        if type(self.num_new_leaves) == type(None): 
            num_new_leaves = modulo_in_range(int(self.prg()),self.branching_range) 
        else: 
            num_new_leaves = self.num_new_leaves 
        leaves = {self.ctr_function() for _ in range(num_new_leaves)} 
        self.d[leaf_node] |= leaves 
        if not self.is_dsg: 
            for l in leaves: self.d[l] |= {leaf_node} 
        self.node_count += num_new_leaves
        self.leaves.extend(leaves) 
        self.leaves_partitioned.append(leaves)
        return 

    def choose_leaf_node(self): 
        leaf = None 
        if self.growth_type == "ordered": 
            #i = int(self.prg()) % len(self.leaves_partitioned) 
            lset = sorted(self.leaves_partitioned[0]) 
            j = int(self.prg()) % len(lset)
            leaf = lset.pop(j)  

            # pop the leaf from the leaves partition 
            if len(lset) == 0: 
                self.leaves_partitioned.pop(0) 
            else: 
                self.leaves_partitioned[0] = set(lset)
            
            # pop the leaf from the leaves set 
            k = self.leaves.index(leaf)
            self.leaves.pop(k) 
        
        else: 
            q = int(self.prg()) % len(self.leaves) 
            leaf = self.leaves.pop(q) 
        return leaf 

    """
    deletes nodes starting with leaves
    """
    def delete_n_nodes(self,n): 
        for _ in range(n): 
            stat = self.delete_one_leaf() 
            if not stat: break 
        return

    def delete_one_leaf(self): 
        if len(self.leaves) == 0: 
            return False 

        # choose a l
        q = int(self.prg()) % len(self.leaves) 
        leaf = self.leaves.pop(q) 
        del self.d[leaf] 
        
        p = self.parent_of(leaf)
        self.d[p] -= {leaf} 

        if len(self.d[p]) == 0: 
            self.leaves.append(p) 
        self.node_count -= 1 
        return True 

    def parent_of(self,n): 
        for k,v in self.d.items(): 
            if n in v: 
                return k 
        return None 

    
    @staticmethod
    def generate_tree__mroot_n_leaves(starting_nodeset,num_leaves,prg,is_dsg:bool=False,growth_type="ordered",\
        branching_range=DEFAULT_TREE_BRANCHING_RANGE): 
        assert type(num_leaves) == int and num_leaves > 0 

        T = TreeGen(starting_nodeset,is_dsg,prg,branching_range,growth_type=growth_type) 

        while len(T.leaves) < num_leaves: 
            diff_leaves = num_leaves - len(T.leaves)
            r = min([diff_leaves,T.branching_range[1]]) 
            new_leaves = modulo_in_range(int(prg()),[1,r+2]) 
            T.set_number_of_new_leaves(new_leaves) 
            next(T) 
        return T