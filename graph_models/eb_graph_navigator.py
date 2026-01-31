from .base_node import * 

class NavigatorSyncTag:

    def __init__(self,tag_target:int):  
        self.tag_target = tag_target 
        self.location = None 
        self.next_location = None 
        self.next_path = None 
        return

    def update(self,loc,next_loc,next_path): 
        assert type(next_path) == NodePath 
        self.loc = self.location 
        self.next_location = next_loc 
        self.next_path = next_path 

"""
Graph navigator operates on finite energy. Once energy 
reaches non-positive real number, navigator terminates. 

Max speed is the upper threshold for navigator to travel 
some edges, with edge weights. 
"""
class EnergyBasedGraphNavigator: 

    def __init__(self,loc,energy,max_speed):  
        assert energy > 0 and max_speed > 0 

        # int -> node 
        #       OR 
        # ((int,int),float) -> halfway between two nodes, on edge  
        self.loc = None 
        self.update_loc(loc)  
        self.energy = energy 
        self.max_speed = max_speed 
        self.context = None 
        self.min_paths = None 
        self.current_path = None 
        self.sync_tags = {} 
        return 

    def add_tag_target(self,nst:NavigatorSyncTag):
        assert type(nst) == NavigatorSyncTag 
        self.sync_tags[nst.tag_target] = nst 
        return 

    def receive_context(self,sg:defaultdict,min_paths): 
        assert type(sg) == defaultdict 
        assert self.location() in sg  
        assert set(sg.keys()) == set(min_paths.keys()) 

        for v in min_paths.values(): 
            assert type(v) == NodePath 
        self.context = sg  
        self.min_paths = min_paths 
        return

    def process_context(self): 
        return -1 

    def update_loc(self,loc): 
        assert type(loc) in {int,tuple} 
        if type(loc) == tuple: 
            assert type(loc[0]) == tuple 
            assert type(loc[1]) == float 
        self.loc = loc 
        return

    def location(self): 
        if type(self.loc) == int: 
            return self.loc 
        return self.loc[0][0] 