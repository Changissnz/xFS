from collections import defaultdict 
from copy import deepcopy

DEFAULT_EDGE_COST_FUNCTION = lambda u,v,c: 1
CUMULATIVE_EDGE_COST_FUNCTION = lambda u,v,c: 1 + c  
CUMULATIVE_PATH_COST_FUNC = lambda x: len(x) 


class NodePath:

    def __init__(self,start_node):
        self.p = [start_node]
        self.pweights = []

    @staticmethod
    def preload(p,pw):
        assert len(p) == len(pw) + 1
        npath = NodePath("void")
        npath.p = p
        npath.pweights = pw 
        return npath 

    def __len__(self):
        return len(self.p)

    def __str__(self):
        s1 = str(self.p) + "\n" + str(self.pweights)
        return s1 

    def __add__(self,nw):
        assert len(nw) == 2 and type(nw) == tuple 
        q = deepcopy(self)
        q.append(nw[0],nw[1])
        return q 

    def __eq__(self,npath):
        assert type(npath) == NodePath
        stat1 = self.p == npath.p
        stat2 = self.pweights == npath.pweights
        return stat1 and stat2 

    def tail(self):
        return self.p[-1]

    def append(self,node,weight):
        self.p.append(node)
        self.pweights.append(weight)

    def invert(self):
        npath = NodePath("void")
        npath.p = self.p[::-1]
        npath.pweights = self.pweights[::-1]
        return npath 

    def cost(self,cost_func=sum):
        return cost_func(self.pweights) 

"""
parent class for DFSCache and BFSCache 
"""
class XFSCache: 

    def __init__(self,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,
        nextnode_priority_function=None):
        assert type(d) == defaultdict 
        self.start_node = start_node
        self.d = d
        self.ecf = edge_cost_function
        self.nnpf = nextnode_priority_function
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
        self.costfrom_table[self.reference][self.reference] = 0 
        return

    def exec(self):
        while self.move_one(): 
            continue 
        return 

    def move_one(self):
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

    def fetch_edge_cost(self,ref,q):
        pcs = list(self.costs_to_node(ref).values())
        prev_cost = min(pcs) if len(pcs) > 0 else 0
        return self.ecf(ref,q,prev_cost)

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
