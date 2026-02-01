from .base_node import * 

DEFAULT_BULLKILLER_AGENT_MODES = {\
    "bull": {"idle","flee"}, \
    "chaser": {"search","capture"}}

"""
"""
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
weighted edges. If navigator lands on an edge (u,v) instead 
of node u or v, algorithm rounds navigator location down to 
node u. 

Used for Bull Killer Simulation. 
"""
class EnergyBasedGraphNavigator(NodeObjectiveNavigator): 

    def __init__(self,idn,loc,energy,max_speed,prg,is_bull:bool):  
        assert energy > 0 and max_speed > 0 

        super().__init__(loc,avoid_nodeset=set(),take_nodeset=set(),\
            objective_nodeset=set(),prg=prg,path_log_length=100,\
            absolute_avoid=False,risk_possible_avoid=False)
        assert type(is_bull) == bool 

        # int -> node 
        #       OR 
        # ((int,int),float) -> halfway between two nodes, on edge  
        self.idn = idn 
        self.loc_ = self.location() 
        self.update_loc(loc)  
        self.energy = energy 
        self.max_speed = max_speed 
        self.is_bull = is_bull 

        self.context = None 
        self.min_paths = None 
        self.current_path = None 
        self.sync_tags = {} 

        if is_bull: 
            self.mode = "idle" 
        else: 
            self.mode = "search" 

        # bull perspective 
        self.chaser_locs = None 

        # chaser perspective 
            # int 
        self.bull_loc = None 
            # NavigatorSyncTag
        self.bull_tag = None 
            # chaser idn -> (location,nodeset of chaser's visual subgraph)
        self.other_chasers = None 
        return 

    def add_tag_target(self,nst:NavigatorSyncTag):
        assert type(nst) == NavigatorSyncTag
        assert not self.is_bull 
        self.bull_tag = nst  
        return 

    def receive_context(self,sg:defaultdict,min_paths,bull_loc,chaser_locs):  
        assert type(sg) == defaultdict 
        assert self.location() in sg  
        assert set(sg.keys()) == set(min_paths.keys()) 

        for v in min_paths.values(): 
            assert type(v) == NodePath 
        self.bull_loc = None 
        self.chaser_locs = None 

        self.context = sg  
        self.min_paths = min_paths
        self.bull_loc = bull_loc  
        self.chaser_locs = chaser_locs 

        self.update_mode() 

    def update_mode(self): 
        if not self.is_bull: 
            assert type(self.chaser_locs) == type(None) 
            if type(self.bull_loc) != type(None): 
                self.mode = "capture" 
            else: 
                self.mode = "search" 
            
        else: 
            assert type(self.bull_loc) == type(None) 
            if type(self.chaser_locs) != type(None): 
                assert type(self.chaser_locs) == set 
                self.mode = "flee"
            else: 
                self.mode = "idle" 
        return

    def add_other_chasers_info(self,other_chasers): 
        assert type(other_chasers) == dict 
        for v in other_chasers.values(): 
            assert type(v[0]) == int and \
                type(v[1]) == set and len(v) == 2 

        self.other_chasers = other_chasers  

    def process_context(self): 
        return -1 

    def update_loc(self,loc): 
        assert type(loc) in {int,tuple} 
        if type(loc) == tuple: 
            assert type(loc[0]) == tuple 
            assert type(loc[1]) == float 
        self.loc_ = loc
        self.loc = self.location()  
        return

    def location(self): 
        if type(self.loc_) == int: 
            return self.loc_  
        return self.loc_[0][0] 