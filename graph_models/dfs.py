from .node_path import * 

"""
search_head_type := 1 for thorough, 2 for filtered;
    1 produces all possible paths, 2 produces less paths 
        in which none may be the shortest path. 
        
"""
class DFSCache:

    def __init__(self,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        search_head_type=1):
        assert type(d) == defaultdict 
        self.start_node = start_node
        self.d = d
        self.ecf = edge_cost_function

        assert search_head_type in {1,2}
        self.search_head_type = search_head_type
        self.reference = None
        self.reference_varcache = []

        # record-keeping vars
        ## vertex -> nodes travelled
        self.ref_neighbors_travelled = defaultdict(set) 

        ## vertex -> previous vertex -> score 
        self.costfrom_table = defaultdict(defaultdict)

        self.min_paths = {} 
        self.init_cache() 

    def init_cache(self):
        self.reference = deepcopy(self.start_node)
        self.reference_varcache.append(deepcopy(self.start_node))
        self.costfrom_table[self.reference][self.reference] = 0 
        return

    def exec_DFS(self):
        while self.move_one(): 
            continue 

    def move_one(self):

        # move to a random available node from the reference
        q = self.ref_neighbors_travelled[self.reference]
        available = set(self.d[self.reference]) - self.ref_neighbors_travelled[self.reference]

        stat1 = len(available) == 0
        stat2 = len(self.reference_varcache) == 0

        # case: end search 
        if stat1 and stat2: 
            return False

        # case: move to the next reference
        if stat1: 
            self.reference = self.reference_varcache.pop(0)
            return self.move_one()

        # case: move to random available node
        q = available.pop()

        pcs = list(self.costs_to_node(self.reference).values())
        prev_cost = min(pcs) if len(pcs) > 0 else 0
        cost = self.ecf(self.reference,q,prev_cost)
        
        self.costfrom_table[self.reference][q] = cost 

            # update reference
        self.ref_neighbors_travelled[self.reference] = self.ref_neighbors_travelled[\
            self.reference] | {q}

        if self.search_head_type == 2:
            self.ref_neighbors_travelled[q] = self.ref_neighbors_travelled[q]\
                | {self.reference}
        self.reference_varcache.insert(0,deepcopy(self.reference))
        self.reference = q        
        return True 

    """
    backtracing uses BFS algorithm;
    no loops! 
    """
    def paths_to_head(self,node,num_paths=float('inf')):
        paths = [NodePath(node)]
        ## ??
        #cft_copy = deepcopy(self.costfrom_table)
        cft_copy = self.invert_costtable() 
        results = [] 
        ##print("HEAD", self.start_node ," NODE ",node)
        while len(paths) > 0 and len(results) < num_paths:
            p = paths.pop(0)
            t = p.tail()
            q = cft_copy[t]

            # check to see if path is result
            ##print('\t\ttail: ',t)
            stat1 = p.tail() == self.start_node            
            if stat1:
                results.append(p)
                continue
    
            pq = list(set(q.keys()) - set(p.p))
            pq = sorted(pq,key=lambda x: q[x])[::-1]
            for k in pq:
                v = q[k] 
                p2 = p + (k,v)
                paths.insert(0,p2)
        return results 

    def store_minpaths(self,ns=None,num_paths=1,cost_func=sum):
        if type(ns) == type(None):
            ns = set(self.ref_neighbors_travelled.keys())

        for k in ns:
            paths = self.paths_to_head(k,num_paths)
            sorted_paths = sorted(paths,key=lambda p: p.cost(cost_func))
            self.min_paths[k] = sorted_paths
        return

    def costs_to_node(self,node):
        d = defaultdict(int)

        for k,v in self.costfrom_table.items():
            if node in v:
                d[k] = v[node]
        return d

    def invert_costtable(self):
        q = defaultdict(defaultdict)

        for k,v in self.costfrom_table.items():
            for k2,v2 in v.items():
                q[k2][k] = v2
        return q

    """
    return:
    - set, nodes that have shortest path of `d` to `start_node`
    """
    def nodeset_of_distance_d(self,d,cost_func=sum):
        assert d > 0 and type(d) == int
        nsd = set() 
        for k,v in self.min_paths.items():
            c = v[0].cost(cost_func)
            if c == d: nsd = nsd | {k}
        return nsd

    

