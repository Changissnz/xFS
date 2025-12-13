import numpy as np 

# TODO: test 
class BaseNode: 

    def __init__(self,node_identifier):  
        assert type(node_identifier) in {str,int,np.int32,np.int64}
        self.identifier = node_identifier
        self.nextset = [] 
        self.i = 0 

    def __next__(self):
        if self.i >= len(self.nextset): return None 
        q = self.nextset[i] 
        self.i = (self.i + 1) % len(self.nextset) 
        return q

    def add_nextset(self,ns): 
        self.nextset.extend(ns) 
        return

    def switch_to_next(self,value,is_index): 
        if is_index: 
            assert 0 <= value < len(self.nextset) 
            self = self.nextset[value] 
            return 
        index = self.index_of_next(value) 
        assert index != -1 
        self = self.nextset[value] 
        return

    def index_of_next(self,identifier): 
        for i,x in enumerate(self.nextset): 
            if x.identifier == identifier: return i 
        return -1 