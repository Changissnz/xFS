from .base_node import * 
from .node_path import * 
from graph_models.shortest_paths_approx import * 

DEFAULT_BULLKILLER_AGENT_MODES = {\
    "bull": {"idle","flee"}, \
    "chaser": {"search","capture"}}

"""
Graph navigator operates on finite energy. Once energy 
reaches non-positive real number, navigator terminates. 

If navigator lands on an edge (u,v) instead of node u or v, 
algorithm rounds navigator location down to node u. 

There are two possible roles this navigator can be: 
- Bull: attempts to maximize distance to Chasers.  
- Chaser: attempts to be at the same node as Bull (capture).  

Used for Bull Killer Simulation. 
"""
class EnergyBasedGraphNavigator(NodeObjectiveNavigator): 

    def __init__(self,idn,loc,energy,prg,is_bull:bool,verbose:bool=False):  
        assert energy > 0

        super().__init__(loc,avoid_nodeset=set(),take_nodeset=set(),\
            objective_nodeset=set(),prg=prg,path_log_length=100,\
            absolute_avoid=False,risk_possible_avoid=False)
        assert type(is_bull) == bool
        assert type(verbose) == bool 

        # int -> node 
        #       OR 
        # ((int,int),float) -> halfway between two nodes, on edge  
        self.idn = idn 
        self.update_loc(loc)  
        self.energy = energy 
        self.is_bull = is_bull 

        self.context = None 
        self.min_paths = None 
        self.current_path = None 

        if is_bull: 
            self.mode = "idle" 
        else: 
            self.mode = "search" 

        # bull perspective 
        self.chaser_locs = None 

        # chaser perspective 
            # int 
        self.bull_loc = None 
            # chaser idn -> (location,nodeset of chaser's visual subgraph)
        self.other_chasers = dict()  

        # frequency of "flee" (if Bull) or "capture" (if Chaser)
        self.active_mode_count = 0 
        self.fin_stat = False 
        self.verbose = verbose 
        return 

    #------------------------------ traversal 

    """
    main method 
    """
    def __next__(self): 
        if self.fin_stat: 
            return 
        
        if self.verbose: print("agent: {}  status: {}  location: {}".format(self.idn,self.mode,self.location())) 

        if self.mode in {"flee","capture"}: 
            self.active_mode_count += 1 

        if self.is_bull: 
            _,c = self.next__bull()
        else: 
            _,c = self.next__chaser() 

        if type(c) != type(None): 
            self.energy -= c 
        
        if self.energy <= 0: 
            self.fin_stat = True 
        return

    def next__bull(self): 
        if type(self.current_path) == type(None): 
            return None,None 
        return self.next_by_current_path() 


    def next__chaser(self): 
        if type(self.current_path) == type(None):
            start = self.location() 
            q = self.make_choice()
            self.update_loc(q)             
            px = self.min_paths[(start,q)]
            if self.verbose: 
                print("agent {} moves from node={} to node={},weight={}".format(\
                self.idn,start,q,px.cost()))
            return q,px.cost() 
        else: 
            self.clear_mainvars()
            return self.next_by_current_path()

    def next_by_current_path(self):
        start = self.location() 
        q = self.current_path[-1] 
        c = self.current_path.cost()
        self.update_loc(q) 
        if self.verbose: 
            print("agent {} moves from node={} to node={},weight={}".format(\
                self.idn,start,q,c))
        self.current_path = None 
        return q,c 

    def stat(self): 
        if self.energy < 0: 
            energy = 0 
        else: 
            energy = self.energy 
        return (energy,self.active_mode_count) 

    #---------------------------------------- methods for receiving contextual graph information 
    #                                         with respect to location.

    def receive_context(self,sg:defaultdict,min_paths,bull_loc,chaser_locs):  
        assert type(sg) == defaultdict 
        assert self.location() in sg  

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

    """
    other_chasers := dict, chaser idn -> (location, nodeset) 
    """
    def add_other_chasers_info(self,other_chasers,min_paths): 
        assert type(other_chasers) == dict 
        for v in other_chasers.values(): 
            assert type(v[0]) == int and \
                type(v[1]) == set and len(v) == 2 
        self.other_chasers = other_chasers  
        self.min_paths.update(min_paths) 

    #--------------------------------------- planning out the next path for agent to take 

    # NOTE: only node with paths to all other nodes is the one that agent is currently located 
    #       on. Uses triangulation to select next path. 
    """
    adversary_path := NodePath | None 
    co_op_info := list<(path,status)>
    """
    def agent_predicts_best_path__chaser(self,adversary_path,co_op_info):  
        assert not self.is_bull 

        self.current_path = None 

        # review co-op info 
        ci = dict() 
        for v,v2 in co_op_info: 
            k2 = (v.head(),v.tail())
            ci[k2] = v2  

        # case: adversary is not sighted 
        #       choose a co-op agent to follow 
        if type(self.bull_loc) == type(None) and type(adversary_path) == type(None): 
            candidates = set()  
            for k,v in ci.items(): 
                if v == "capture":  
                    candidates |= {k[0]}
            candidates = sorted(candidates) 

            if len(candidates) == 0: 
                return self.current_path  

            i = int(self.prg()) % len(candidates)
            c = candidates[i]
            p = (self.location(), c)
            self.current_path = self.min_paths[p]
            return self.current_path 

        # iterate through co_op_info for 
        next_candidates = self.next_possible_nodes() 
        exclude = set([k[1] for k in ci.keys()]) 

        # case: go to expected next location of bull 
        if type(adversary_path) != type(None): 
            t = adversary_path.tail() 
            if t not in exclude: 
                self.current_path = self.min_paths[(self.location(),t)]
                return self.current_path

        next_candidates_ = next_candidates - exclude #(exclude | {self.location()}) 

        # case: all possible next nodes will be occupied by at least 1 co-agent 
        if len(next_candidates_) == 0: 
            next_candidates_ = next_candidates 
        if len(next_candidates_) == 0: 
            return self.current_path 

        # target node is either adversary_path[-1] or bull_loc 
        if type(adversary_path) != type(None): 
            t = adversary_path.tail() 
        else: 
            t = self.bull_loc 


        # sort by closest to farthest, via a triangulation calculation 
        tc = self.min_paths[(self.location(),t)].cost() 
        next_candidates_ = [(nc,abs(tc - self.min_paths[(self.location(),nc)].cost())) \
            for nc in next_candidates_] 
        q = prg_seqsort_ties(next_candidates_,prg__single_to_int(self.prg),lambda x:x[1]) 

            ####
        """
        print("CANDIDATES")
        print([x[0] for x in q])
        print("XX")
        print(q[0][1])
        """
            #### 

        t = q[0][0] 
        self.current_path = self.min_paths[(self.location(),t)]
        return self.current_path 

    # NOTE: only node with paths to all other nodes is the one that agent is currently located 
    #       on. Uses triangulation to select next path. 
    # NOTE: function has a flaw to it, in the case where `adversary_paths` are not known. Bull 
    #       could stay at the same node if that node is the farthest from the Chaser/s in vicinity. 
    #       Staying at the same node guarantees the Bull is captured. 
    def agent_predicts_best_path__bull(self,adversary_paths): 
        if type(self.chaser_locs) == type(None):  
            self.current_path = None 
            return self.current_path 

        # case: agent does not know any adversary paths 
        #       rely on adversary locations
        loc = self.location() 
        avoid_nodes = set(self.chaser_locs) 
        if type(adversary_paths) != type(None):
            avoid_nodes = set([p.tail() for p in adversary_paths])

        ad = average_edge_distance_to_nodeset(self.location(),avoid_nodes,self.min_paths,is_weighted=False)
        d = []  
        possible_next = self.next_possible_nodes()
        possible_next_ = possible_next - avoid_nodes 
        if len(possible_next_) == 0: possible_next_ = possible_next

        for p in possible_next_: 
            a = (p, abs(ad - len(self.min_paths[(self.location(),p)]) - 1))  
            ##average_edge_distance_to_nodeset(p,avoid_nodes,self.min_paths,is_weighted=False)) 
            d.append(a)

        vf = lambda x: x[1] 
        d = prg_seqsort_ties(d,prg__single_to_int(self.prg),vf)[::-1] 

        x = d.pop(0)  
        xs = [x] 
        while len(d) > 0: 
            x2 = d.pop(0) 
            if x2[1] == x[1]: 
                xs.append(x2) 
            else: 
                break 

        i = int(self.prg()) % len(xs) 
        x = xs[i][0] 

        self.current_path = self.min_paths[(loc,x)] 
        return self.current_path

    #---------------------------------------------- auxiliary methods 

    def next_possible_nodes(self): 
        l = self.location()
        nodes = set() 
        for k in self.min_paths.keys(): 
            if k[0] == l: 
                nodes |= {k[1]} 
        return nodes 

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