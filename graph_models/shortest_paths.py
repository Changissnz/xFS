from .node_path import * 
from morebs2.numerical_generator import default_std_Python_prng,prg_seqsort
from types import MethodType,FunctionType

"""
designed for use with bigger graphs (> 50 nodes).
"""
class BDFSCache(XFSCache):

    def __init__(self,start_node,d:defaultdict,is_bfs:bool=True,prg=None,\
        edge_cost_function=lambda u,v:1,num_paths_per_node=10): 

        super().__init__(start_node,d,edge_cost_function,None)

        assert type(is_bfs) == bool 
        self.is_bfs = is_bfs 

        if type(prg) == type(None): 
            prg = default_std_Python_prng()

        assert type(prg) in {MethodType,FunctionType} 
        self.prg = prg 

        self.min_paths[self.reference] = [NodePath(self.reference)] 
        self.num_paths_per_node = num_paths_per_node 

    def move_one(self): 
        def prg_(): return int(self.prg())

        self.previous_edges.clear() 

        if type(self.reference) == type(None): 
            return False 

        # get untravelled nodes 
        untravelled = self.d[self.reference] - self.ref_neighbors_travelled[self.reference] 
        untravelled = sorted(untravelled) 

        if len(untravelled) == 0: 
            self.reference = None 
            if len(self.reference_varcache) == 0: 
                return False 

            self.reference = self.reference_varcache.pop(0)
            return True 

        if self.is_bfs: 
            for n in untravelled: 
                new_paths = self.add_node_to_prev_min_paths(self.reference,n)
                self.insert_new_paths(n,new_paths)
            untravelled = set(untravelled)
        else: 
            # choose a node 
            ni = int(self.prg()) % len(untravelled)
            node = untravelled.pop(ni)

            new_paths = self.add_node_to_prev_min_paths(self.reference,node) 
            self.insert_new_paths(node,new_paths) 

            untravelled = set([node]) 
            
        self.ref_neighbors_travelled[self.reference] |= untravelled
        untravelled = prg_seqsort(sorted(untravelled),prg_)

        self.previous_edges = [(self.reference,n) for n in untravelled] 

        self.reference_varcache.extend(untravelled) 

        if self.is_bfs: 
            self.reference = self.reference_varcache.pop(0)

        return True 

    """
    return:
    - each path of previous node `prev` extended with `node`. 
    """
    def add_node_to_prev_min_paths(self,prev,node): 
        prev_paths = self.min_paths[prev]
        cost = self.ecf(prev,node)

        paths = [] 
        for p in prev_paths: 
            new_path = p + (node,cost) 
            paths.append(new_path)
        return paths 

    def insert_new_paths(self,node,new_paths): 

        def insert_one(path): 
            cost = path.cost() 

            # iterate through paths of node to sort it 
            node_paths = self.min_paths[node] 
            for j,p in enumerate(node_paths): 
                cost2 = p.cost() 
                if cost <= cost2: 
                    node_paths.insert(j,path)  
                    return 
            
            node_paths.insert(len(node_paths),path) 
            return 

        for p in new_paths:
            insert_one(p) 
    
        node_paths = self.min_paths[node] 
        while len(node_paths) > self.num_paths_per_node: 
            node_paths.pop(-1)
        return 