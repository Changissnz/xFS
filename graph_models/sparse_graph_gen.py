from .tree_gen import * 
from morebs2.numerical_generator import prg_choose_n,prg__single_to_int

class SparseConnectedGraphGen(TreeGen): 

    def __init__(self,num_nodes,leaf_backtrack_conn_ratio_range,backtrack_conn_range,\
        is_dsg:bool=False,prg=None,branching_range=DEFAULT_TREE_BRANCHING_RANGE,\
        growth_type="distributed"):
        assert is_valid_range(leaf_backtrack_conn_ratio_range,False,True) 
        assert is_valid_range(backtrack_conn_range,True,False)  

        super().__init__(starting_nodeset={0},is_dsg=is_dsg,prg=prg,branching_range=branching_range,\
            growth_type=growth_type) 
        self.num_nodes = num_nodes 
        self.lbc_range = leaf_backtrack_conn_ratio_range
        self.bc_range = backtrack_conn_range
        return 

    def make(self): 
        self.form_tree()
        self.phase_two_edges() 
        return

    def phase_two_edges(self): 
        num_leaves = len(self.leaves) 
        r = modulo_in_range(int(self.prg()),self.lbc_range)
        n = ceil(num_leaves * r) 

        X = prg_choose_n(deepcopy(self.leaves),n,prg__single_to_int(self.prg),True)

        for x in X: 
            pl = modulo_in_range(int(self.prg()),self.bc_range)
            self.connect_path_from_leaf(x,pl) 

    def form_tree(self): 

        while self.node_count < self.num_nodes:  
            next(self) 

        diff = self.node_count - self.num_nodes 
        if diff != 0: 
            self.delete_n_nodes(diff)  
        return

    def connect_path_from_leaf(self,l,path_length): 

        already = {l} | self.d[l]
        at = l 
        while path_length > 0: 
            candidates = set(self.d.keys()) - already 
            if len(candidates) == 0: 
                break 

            candidates = sorted(candidates) 
            i = int(self.prg()) % len(candidates) 
            c = candidates[i]

            self.d[at] |= {c} 

            if not self.is_dsg: 
                self.d[c] |= {at} 

            already = {c} | self.d[c] 
            at = c 
            path_length -= 1 
        return