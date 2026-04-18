import numpy as np 
from collections import defaultdict
from morebs2.numerical_generator import prg_seqsort_ties

# TODO: test 
class BaseNode: 

    def __init__(self,node_identifier):  
        assert type(node_identifier) in {str,int,np.int32,np.int64}
        self.identifier = node_identifier
        self.nextseq = [] 
        self.i = 0 

    def __next__(self):
        if self.i >= len(self.nextseq): return None 
        q = self.nextseq[i] 
        self.i = (self.i + 1) % len(self.nextseq) 
        return q

    def add_nextseq(self,ns): 
        self.nextseq.extend(ns) 
        return

    def switch_to_next(self,value,is_index): 
        if is_index: 
            assert 0 <= value < len(self.nextseq) 
            self = self.nextseq[value] 
            return 
        index = self.index_of_next(value) 
        assert index != -1 
        self = self.nextseq[value] 
        return

    def index_of_next(self,identifier): 
        for i,x in enumerate(self.nextseq): 
            if x.identifier == identifier: return i 
        return -1 

DEFAULT_NAVIGATOR_NODE_COUNTER = lambda loc,value: value + 1

# TODO: test 
"""
a navigator for a graph, provided by parameter to method<receive_context>. 
Navigator prioritizes travelling on nodes of `take_nodeset`, deprioritizes 
travelling on nodes of `avoid_nodeset`, and attempts to converge to node 
location in `objective_nodeset`. 

A node-by-node navigator. Does not consider edge costs. 

`objective` > `take` > `possible_avoid` > `avoid`. 
"""
class NodeObjectiveNavigator:

    def __init__(self,loc,avoid_nodeset,take_nodeset,objective_nodeset,prg,path_log_length=float('inf'),\
        absolute_avoid:bool=False,risk_possible_avoid:bool=False,nav_ctr=DEFAULT_NAVIGATOR_NODE_COUNTER): 
        assert type(avoid_nodeset) == type(take_nodeset) == type(objective_nodeset) 
        assert len(avoid_nodeset.intersection(take_nodeset)) == 0 
        assert len(take_nodeset.intersection(objective_nodeset)) == 0 
        assert len(avoid_nodeset.intersection(objective_nodeset)) == 0 
        assert type(absolute_avoid) == bool == type(risk_possible_avoid)

        self.path_log_length = path_log_length
        self.encountered = defaultdict(int,{loc: 1}) 
        self.path_log = [loc]
        self.loc = loc 
        self.avoid = avoid_nodeset
        self.possible_avoid = set() 
        self.nav_ctr = nav_ctr 
        self.absolute_avoid = absolute_avoid
        self.risk_possible_avoid = risk_possible_avoid

        # preferred nodes to take in intermediary travel 
        self.take = take_nodeset
        self.objectives = objective_nodeset
        self.prg = prg 
        self.context = None 
        self.c = 0 
        return

    def set_risk_possible_avoid(self,stat:bool): 
        assert type(stat) == bool 
        self.risk_possible_avoid = stat 

    def receive_context(self,sg:defaultdict): 
        assert type(sg) == defaultdict 
        assert self.loc in sg 
        self.context = sg 
        return

    """
    moves one edge distance 
    """
    def make_choice(self):
        x = self.next_move()
        if type(x) == type(None): 
            return None 

        self.loc = x 
        self.update_travel_log()
        return x 

    def next_move(self):

        q = self.context[self.loc]         
        if len(q) == 0: 
            return 

        # case: go to objective node 
        o = self.objectives.intersection(q)
        if len(o) > 0: 
            o = sorted(o) 
            i = int(self.prg()) % len(o) 
            return o[i]

        q = q - set(self.encountered.keys()) - self.avoid
        
        # case: all nodes in vicinity have been traveled on. 
        #       take the least frequently travelled. 
        if len(q) == 0: 
            # rank neighbors from least to most traveled 
            neighbors = sorted(self.context[self.loc])

            # partition neighbors into non-avoid and avoid 
            non_avoid = [(n,self.encountered[n]) for n in neighbors if n not in self.avoid]
            possible_avoid = [(n,self.encountered[n]) for n in neighbors if n in self.possible_avoid]

            if self.absolute_avoid: 
                avoid = [] 
            else: 
                avoid = [(n,self.encountered[n]) for n in neighbors if n in self.avoid] 

            if len(non_avoid) > 0: 
                non_avoid = prg_seqsort_ties(non_avoid,self.prg,lambda x:x[1]) 
            if len(possible_avoid) > 0: 
                possible_avoid = prg_seqsort_ties(possible_avoid,self.prg,lambda x:x[1])
            if len(avoid) > 0: 
                avoid = prg_seqsort_ties(avoid,self.prg,lambda x:x[1]) 
            
            non_avoid.extend(possible_avoid)
            #
            if len(non_avoid) > 0 and self.risk_possible_avoid: 
                non_avoid = prg_seqsort_ties(non_avoid,self.prg,lambda x:x[1]) 

            non_avoid.extend(avoid)
            if len(non_avoid) == 0: return None 
            return non_avoid[0][0]  

        # case: take a preferred node 
        ix = self.take.intersection(q) 
        if len(ix) != 0: 
            ix = sorted(ix) 
            i = int(self.prg()) % len(ix) 
            return ix[i] 

        # case: take an arbitrary node
        q = sorted(q) 
        i = int(self.prg()) % len(q) 
        return q[i] 

    def update_travel_log(self):
        k,v = self.loc,self.encountered[self.loc] 
        self.encountered[self.loc] = self.nav_ctr(k,v) 
        self.path_log.append(self.loc) 

        lx = self.path_log_length - len(self.path_log) 

        while lx < 0: 
            self.path_log.pop(0)  
            lx += 1 

        self.c += 1 

    def add_possible_avoid(self,possible_avoid):
        assert type(possible_avoid) == set  
        self.possible_avoid |= possible_avoid

    def add_take(self,take_nodeset):
        assert type(take_nodeset) == set  
        self.take |= take_nodeset

    def clear_mainvars(self): 
        self.possible_avoid.clear() 
        self.take.clear() 
        self.encountered = defaultdict(int,{self.loc: 1}) 
        self.path_log.clear() 

    def reset_location(self,loc):
        self.loc = loc 
        self.path_log.append(self.loc) 