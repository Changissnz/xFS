from .bfs import * 
from types import MethodType,FunctionType
import random 
from morebs2.numerical_generator import prg__single_to_decimal

"""
NOTE: in `prg` mode, algorithm not guaranteed to produce one component 
      during tree search. 

NOTE: code is somewhat redundant to the <XFSCache> classes. 
"""
class SpanningTree: 

    def __init__(self,G,edge_cost_function=lambda u,v:1 if u != v else 0,\
        prg=None):
        assert type(G) == defaultdict 
        assert type(edge_cost_function) in {MethodType,FunctionType,type(None)} 
        assert type(prg) in {MethodType,FunctionType,type(None)} 

        self.G = G 
        self.edge_cost_function = edge_cost_function 
        self.prg = prg
        self.prg_dec = None 
        self.mst_mode = type(self.prg) == type(None) 

        self.head = None 
        self.queue = []
        # target node -> (predecessor node,edge distance from head,PRNG decimal | None)
        self.T = dict() 
        self.fin_stat = False 
        return

    """
    pre-main method 
    """
    def init_head(self,head=None):
        if type(head) == type(None):  
            K = sorted(self.G.keys())
            if not self.mst_mode: 
                i = int(self.prg()) % len(K)
            else: 
                i = random.randrange(0,len(K))

            self.head = K[i]
        else: 
            self.head = head 

        self.queue = [self.head]  
        self.T = dict() 
        
        x = None
        if not self.mst_mode: 
            self.prg_dec = prg__single_to_decimal(self.prg)
            x = 1.0 
        
        self.T[self.head] = [None,0.,x]  

        self.fin_stat = False 
        return

    """
    main method 
    """
    def make(self):
        while not self.fin_stat: next(self) 

    def __next__(self): 

        if self.fin_stat: 
            return 

        if len(self.queue) == 0: 
            self.fin_stat = True 
            return

        q = self.queue.pop(0) 
        neighbors = sorted(self.G[q]) 
        for n in neighbors: 
            stat = self.assign_connection(q,n)
            if stat: 
                self.queue.append(n)
        return

    def assign_connection(self,predecessor_node,current_node): 
        if self.mst_mode: 
            return self.assign_connection__mst(predecessor_node,current_node)
        else: 
            return self.assign_connection__prng(predecessor_node,current_node)

    def assign_connection__mst(self,predecessor_node,current_node): 
        assert self.mst_mode 

        if current_node not in self.T: 
            s1 =  float('inf') 
        else: 
            s1 = self.T[current_node][1] 

        s2 = self.T[predecessor_node][1] 
        s2 = s2 + self.edge_cost_function(predecessor_node,current_node)

        if s2 < s1: 
            self.T[current_node] = [predecessor_node,s2,None] 
            return True 
        return False 

    def assign_connection__prng(self,predecessor_node,current_node): 
        assert not self.mst_mode 

        if current_node not in self.T: 
            s1 = -0.05 
        else: 
            s1 = self.T[current_node][2]   
            
        s2 = round(self.prg_dec(),5)

        if s2 > s1: 
            q = self.T[predecessor_node][1] + \
                self.edge_cost_function(predecessor_node,current_node)
            self.T[current_node] = [predecessor_node,q,s2]
            return True 
        return False 

    """
    post-main method 
    """
    def tree_to_paths(self,key_is_st_pair:bool=False): 

        F = lambda u,v,c: self.edge_cost_function(u,v) 
        bfsc = BFSCache(self.head,self.tree(),\
            edge_cost_function=F,nextnode_priority_function=None,\
            no_duplicate_touch_nodes=False)
        bfsc.exec() 
        bfsc.store_minpaths()

        D = dict() 
        for k,v in bfsc.min_paths.items(): 
            k_ = (self.head,k) if key_is_st_pair else k 
            D[k_] = v[0] 
        return D

    def tree(self): 
        D = defaultdict(set) 
        for k,v in self.T.items(): 
            if type(v[0]) == type(None): continue 
            D[v[0]] |= {k} 
        return D 