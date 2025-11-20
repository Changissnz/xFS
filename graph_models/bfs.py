from .node_path import * 

class BFSCache(XFSCache):

    def __init__(self,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None): 

        super().__init__(start_node,d,edge_cost_function,\
            nextnode_priority_function)

    def move_one(self):

        # get all neighbors, untravelled 
        q = self.d[self.reference] - self.ref_neighbors_travelled[self.reference]
        
        stat1 = len(q) == 0 
        stat2 = len(self.reference_varcache) == 0

        # case: no more neighbors, no more nodes
        if stat1 and stat2: 
            return False 

        # case: use nnpf to prioritize order of neighbors for next search
        if type(self.nnpf) != type(None): 
            q = self.nnpf(self.reference,q) 
        else: 
            q = sorted(q) 

        # update records 
        for q_ in q:
            self.ref_neighbors_travelled[q_] |= {self.reference} 
            self.costfrom_table[self.reference][q_] = self.fetch_edge_cost(self.reference,q_)

        self.ref_neighbors_travelled[self.reference] -= set(q)
        self.reference_varcache.extend(q) 

        if len(self.reference_varcache) == 0: 
            return False 
        self.reference = self.reference_varcache.pop(0)
        return True 