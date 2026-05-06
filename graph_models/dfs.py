from .node_path import * 

"""
designed for use with smaller graphs (< 50 nodes). Offers comprehensive backtracking 
for obtaining paths. 

search_head_type := 1 for thorough, 2 for filtered;
    1 produces all possible paths, 2 produces less paths 
        in which none may be the shortest path. 
        
"""
class DFSCache(XFSCache):

    def __init__(self,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        search_head_type=1,nextnode_priority_function=None,no_duplicate_touch_nodes:bool=False):
        assert search_head_type in {1,2}
        self.search_head_type = search_head_type
        super().__init__(start_node,d,edge_cost_function,\
            nextnode_priority_function,no_duplicate_touch_nodes)

    def move_one(self):
        self.previous_edges.clear() 
        ##print("moving {}".format(len(self.reference_varcache))) 
        
        # move to a random available node from the reference
        stat = self.check_for_expired_reference()
        if stat: 
            return False 

        q = self.ref_neighbors_travelled[self.reference]
        available = set(self.d[self.reference]) - self.ref_neighbors_travelled[self.reference]

        stat1 = len(available) == 0
        stat2 = len(self.reference_varcache) == 0

        # case: end search 
        if stat1 and stat2: 
            self.fin_stat = True 
            return False

        # case: move to the next reference
        if stat1: 
            self.reference = self.reference_varcache.popleft() 
            return True 

        # case: move to random available node
        if type(self.nnpf) != type(None): 
            q = self.nnpf(self.reference,available) 
        else: 
            q = available.pop()
        cost = self.fetch_edge_cost(self.reference,q)
        
        self.costfrom_table[self.reference][q] = cost 

            # update reference
        self.ref_neighbors_travelled[self.reference] = self.ref_neighbors_travelled[\
            self.reference] | {q}

        if self.search_head_type == 2:
            self.ref_neighbors_travelled[q] = self.ref_neighbors_travelled[q]\
                | {self.reference}

        # case: node has already been touched 
        if self.no_duplicate_touch_nodes: 
            if q in self.touched_nodes: 
                return True 

        self.previous_edges.append((self.reference,q))

        if self.no_duplicate_touch_nodes: 
            self.touched_nodes |= {q} 

        self.reference_varcache.insert(0,deepcopy(self.reference))
        self.reference = q
        return True 
    

