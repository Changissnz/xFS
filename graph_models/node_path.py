from collections import defaultdict 
from copy import deepcopy
import numpy as np 

DEFAULT_EDGE_COST_FUNCTION = lambda u,v,c: 1
DEFAULT_EDGE_COST_FUNCTION_2 = lambda u,v:1 if u != v else 0
CUMULATIVE_EDGE_COST_FUNCTION = lambda u,v,c: 1 + c  
CUMULATIVE_PATH_COST_FUNC = lambda x: len(x) 

class NodePath:

    def __init__(self,start_node):
        self.p = [start_node]
        self.pweights = []
        self.index = 0 

    def adjust_weights(self,fx): 
        pw = [] 
        for i in range(len(self.p) -1): 
            u,v = self.p[i],self.p[i+1] 
            pw.append(fx(u,v)) 
        return NodePath.preload(deepcopy(self.p),pw) 

    @staticmethod
    def preload(p,pw):
        if len(p) == 0: 
            assert len(pw) == 0 
            npath = NodePath('void')
            npath.p.clear()
            return npath 

        assert len(p) == len(pw) + 1
        npath = NodePath("void")
        npath.p = p
        npath.pweights = pw 
        return npath 

    @staticmethod 
    def nodepath_set_to_graph(nodepath_set,is_dsg:bool=False): 

        D = defaultdict(set) 

        for npath in nodepath_set:
            assert type(npath) == NodePath 
            X = npath.p

            for i in range(len(X) - 1): 
                x0,x1 = X[i],X[i+1]
                D[x0] |= {x1} 

                if not is_dsg: 
                    D[x1] |= {x0} 
        return D

    def __getitem__(self,i):
        if isinstance(i, slice): 
            return self.p.__getitem__(i)    

        if type(i) in {list,np.ndarray}:
            qx = []
            for i_ in i:
                qx.append(self.__getitem__(i_))
            return qx 

        assert i < len(self) 
        return self.p[i]  

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.p):
            x = self.p[self.index]
            self.index += 1
            return x
        return None 

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

    def add_path(self,p): 
        if len(p) == 0: 
            return 
            
        if len(self) == 0: 
            self.p = p.p 
            self.pweights = p.pweights
            return 

        assert self.tail() == p.head() 
        self.p.extend(p.p[1:]) 
        self.pweights.extend(p.pweights)  

    def head(self):
        return self.p[0] 

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

    def first_occurrence(self,node): 
        if node not in self.p: return None 
        return self.p.index(node) 

    def head_subpath(self,index,include_first:bool=True): 
        assert 0 <= index < len(self.p) 

        if include_first: 
            index += 1 
        
        p_ = self.p[:index]
        if index - 1 < 0: 
            pw_ = [] 
        else: 
            pw_ = self.pweights[:index -1]

        return NodePath.preload(p_,pw_) 

    def tail_subpath(self,index,include_first:bool=True):
        assert 0 <= index < len(self.p) 
        
        if not include_first: 
            index += 1 

        p_ = self.p[index:]

        if index - 1 < 0: 
            pw_ = [] 
        else: 
            pw_ = self.pweights[index:]

        return NodePath.preload(p_,pw_) 

# NOTE: there are some features not yet implemented, such as 
#           parameter<cost_func> for function<store_minpaths>. 
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

        # used to keep track of previous move
        self.previous_edges = [] 

        self.min_paths = defaultdict(list)
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
        
        cft_copy = self.invert_costtable() 
        results = [] 
        while len(paths) > 0 and len(results) < num_paths:
            p = paths.pop(0)
            t = p.tail()
            q = cft_copy[t]

            # check to see if path is result
            stat1 = p.tail() == self.start_node            
            if stat1:
                results.append(p)
                continue
    
            pq = list(set(q.keys()) - set(p.p))
            pq = sorted(pq,key=lambda x: q[x])#[::-1]
            for k in pq:
                v = q[k] 
                p2 = p + (k,v)
                paths.insert(0,p2)
        return results 

    # NOTE: `cost_func`not fully implemented yet. 
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

    def remove_nodeset_from_refvarcache(self,nodeset): 
        i = 0 
        while i < len(self.reference_varcache):
            if self.reference_varcache[i] in nodeset:
                self.reference_varcache.pop(i)
            else:
                i += 1 

        if self.reference in nodeset: 
            self.reference = None 

        if len(self.reference_varcache) > 0:
            self.reference = self.reference_varcache.pop(0)
