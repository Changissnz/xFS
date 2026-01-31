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

class GraphNavigator:

    def __init__(self,loc): 
        self.loc = loc 
        self.context = None 
        return 

    def add_tag_target(self): 
        return 

    def receive_context(self,sg:defaultdict): 
        assert type(sg) == defaultdict 
        assert self.loc in sg 
        self.context = sg 
        return

    