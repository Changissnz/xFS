from .node_path import * 

"""
designed for use with smaller graphs (< 50 nodes). Offers comprehensive backtracking 
for obtaining paths. 
"""
class BFSCache(XFSCache):

    def __init__(self,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None,no_duplicate_touch_nodes:bool=False): 

        super().__init__(start_node,d,edge_cost_function,\
            nextnode_priority_function)
        self.no_duplicate_touch_nodes = no_duplicate_touch_nodes
        self.touched_nodes = set([self.reference]) 

    def move_one(self):
        self.previous_edges.clear() 

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
            self.previous_edges.append((self.reference,q_))
            self.ref_neighbors_travelled[q_] |= {self.reference} 
            new_cost = self.fetch_edge_cost(self.reference,q_)

            ### ??? 
            """
            if self.reference in self.costfrom_table: 
                if q_ in self.costfrom_table[self.reference]: 
                    new_cost = min([q_,new_cost]) 
            """ 
            self.costfrom_table[self.reference][q_] = new_cost 

        self.ref_neighbors_travelled[self.reference] -= set(q)

        q = self.filter_no_duplicate_touch_nodes(q) 
        self.reference_varcache.extend(q) 
        
        if self.no_duplicate_touch_nodes: 
            self.touched_nodes |= set(q) 
        
        if len(self.reference_varcache) == 0: 
            return False 
        self.reference = self.reference_varcache.pop(0)
        return True 

    def filter_no_duplicate_touch_nodes(self,q): 
        if not self.no_duplicate_touch_nodes: 
            return q 
        return [q_ for q_ in q if q_ not in self.touched_nodes] 