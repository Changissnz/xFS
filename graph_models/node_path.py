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