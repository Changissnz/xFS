from .square_nt import * 
from graph_models.node_path import * 
from morebs2.matrix_methods import equal_iterables
from math import ceil 

DEFAULT_POISON_MODEL_SNT_MINMAX = [-1.,1.]

"""
representative of poison in simulation Poison Trace Bot. 
"""
class PoisonModelSNT(SquareMatrixNegativeTransform): 

    def __init__(self,M,prg,min_max=DEFAULT_POISON_MODEL_SNT_MINMAX,idn=None):
        self.idn = idn 
        super().__init__(M,prg,min_max) 
        return 

    def __next__(self): 
        if self.fin_stat: 
            return None 

        return super().__next__()

"""
representative of poisoning action taken by source against target, in simulation Poison Trace Bot. 
Poisoning action consists of two phases: 
- send phase: poison travels through network from source to target. 
- reaction phsae: after registering hit with target, poison activates in target. 
"""
class PoisonPath: 

    def __init__(self,npath:NodePath,poison_type="expressive"): 
        assert type(npath) == NodePath 
        assert poison_type in {"expressive","inexpressive"} 
        self.npath = npath 
        self.poison_type = poison_type 
        self.p = None 
        self.phase = "send" 
        self.fin_stat = False 
        self.first_reaction = True 

        self.loc = None 
        return

    def __str__(self): 
        S = "* Poison Path Status: " + self.phase + "\n"
        S += "* finished: " + str(self.fin_stat) + "\n" 
        S += "\ttype: " + self.poison_type + "\n" 
        S += str(self.npath) 
        return S 

    def load_poison(self,p:PoisonModelSNT): 
        assert type(p) == PoisonModelSNT
        self.p = p 
        return

    def path_head(self): 
        return self.npath.head() 

    def path_target(self): 
        return self.npath.tail() 

    def poison_idn(self):
        if type(self.p) == type(None): 
            return None  
        return self.p.idn 

    def __next__(self): 
        assert type(self.p) == PoisonModelSNT 
        if self.fin_stat: return None,None 

        if self.phase == "send": 
            q = self.send_next()
            if type(q) == type(None): 
                self.phase = "react" 
                return next(self) 
            self.loc = q 
            return q,self.phase 
        else: 
            q = self.react_next()
            if type(q) == type(None): 
                self.fin_stat = True
                return None,None  
            q_ = q if self.poison_type == "expressive" else None 
            return q_,self.phase

    def location(self): 
        return self.loc 

    def send_next(self): 
        assert self.phase == "send"
        return next(self.npath)

    def react_next(self): 
        assert self.phase == "react"  
        if self.first_reaction: 
            self.first_reaction = not self.first_reaction
            return deepcopy(self.p.M) 
        return next(self.p) 

class PoisonRelay: 

    def __init__(self,owner:int,location:int,recognition_accuracy:float,prg):  
        assert type(owner) == int == type(location)
        assert 0. <= recognition_accuracy <= 1. 
        assert type(prg) in {MethodType,FunctionType} 

        self.owner = owner 
        self.location = location 
        self.recognition_accuracy = recognition_accuracy 
        self.prg = prg 
        self.hit_counter = 0 
        return 

    def relay_poison(self,pp:PoisonPath,all_source_candidates:set):  
        assert type(pp) == PoisonPath 
        assert type(all_source_candidates) == set 
        
        self.hit_counter += 1
        path_head = pp.path_head() 
        all_source_candidates = sorted(all_source_candidates - {path_head}) 

        suspects = {path_head} 
        num_additional = ceil((1 - self.recognition_accuracy) * len(all_source_candidates)) 
        if num_additional == 0: 
            return suspects 

        prg_ = prg__single_to_int(self.prg)
        q = prg_choose_n(all_source_candidates,num_additional,prg_,is_unique_picker=True)
        suspects = suspects | set(q) 
        return suspects 

    def change_location(self,new_loc): 
        self.location = new_loc 
        self.hit_counter = 0

class RelayPlacement: 

    def __init__(self,source_idn,num_sources,max_relays,prg,relay_accuracy_range,verbose:bool=False):   

        self.source_idn = source_idn 
        self.num_sources = num_sources 
        self.max_relays = max_relays 
        self.prg = prg 
        self.relay_accuracy_range = relay_accuracy_range
        # path idn -> set of relays 
        self.active_relays = defaultdict(list)  
        # path idn -> partial nodeset of path 
        self.paths_info = defaultdict(set)
        return 

    def attempt_relay_PoisonPath(self,poison_path,possible_candidates): 
        x = poison_path.location() 
        relays = self.relays_at_location(x) 

        q = [] 
        for relay in relays: 
            possible = relay.relay_poison(poison_path,possible_candidates)
            q.append(possible)
        return q 
        
    def relays_at_location(self,location): 
        relays = set() 
        for relay_set in self.active_relays.values():  
            for r in relay_set: 
                if r.location != location: continue 
                relays |= {r} 
        return relays 

    def set_placement_scheme(self,scheme): 
        assert scheme in {0,1} 
        self.placement_scheme = scheme 

    def relay_count(self): 
        s = 0 
        for x in self.active_relays.values(): 
            s += len(x) 
        return s 

    def add_path_info(self,source_idn,nodeset): 
        self.paths_info[source_idn] = nodeset 
        return 

    def add_one_relay(self):
        if self.relay_count() == self.max_relays: 
            return False 

        q = ceil(self.max_relays / self.num_sources)
        x = sorted(self.paths_info.keys())
        if len(x) == 0: return False 

        i = int(self.prg()) % len(x) 
        p_idn = x[i]

        nodes = sorted(self.paths_info[p_idn]) 
        j = int(self.prg()) % len(nodes) 
        loc = nodes[j] 

        accuracy = modulo_in_range(self.prg(),self.relay_accuracy_range)
        r = PoisonRelay(self.source_idn,loc,accuracy,self.prg)
        self.active_relays[p_idn].append(r) 
        return True 

    def move_one_relay(self): 
        x = sorted(self.active_relays.keys())
        if len(x) == 0: return False 

        i = int(self.prg()) % len(x) 
        p_idn = x[i]

        relays = self.active_relays[p_idn] 
        j = int(self.prg()) % len(relays) 
        old_relay = relays[j] 

        q = sorted(set(self.paths_info.keys()) - {p_idn})
        if len(q) == 0: 
            return False 

        k = int(self.prg()) % len(q) 

        new_loc = q[k] 
        old_relay.change_location(new_loc) 

        self.active_relays[p_idn].pop(j) 
        if len(self.active_relays[p_idn]) == 0: 
            del self.active_relays[p_idn] 
        self.active_relays[new_loc].append(old_relay) 
        return True 

    def __next__(self): 

        if not self.add_one_relay(): 
            self.move_one_relay() 
        return

    def path_relay_hit_counter_map(self): 
        path_hits = dict() 
        for k,v in self.active_relays.items(): 
            f = sum([v_.hit_counter for v_ in v]) 
            path_hits[k] = f 
        return path_hits 


"""
action structure that can be utilized by a target after it has been struck with poison. 
Target uses <PoisonBacktracker> to determine source information behind the poison. 
"""
class PoisonBacktracker: 

    def __init__(self,p:PoisonPath,source_info): 
        assert type(p) == PoisonPath 
        assert type(source_info) in {MethodType,FunctionType} 

        self.p = p  
        self.source_idn = self.p.path_head()
        self.poison_idn = self.p.poison_idn() 
        self.source_info = source_info 
        self.fin_stat = False 
        self.i = -1  
        self.l = -ceil(len(self.p.npath) / 2)
        self.cache = set() 
        return 

    def __next__(self): 
        if self.fin_stat: 
            return self.source_info 

        if self.i == self.l: 
            self.fin_stat = True 
    
        q = self.p.npath[self.i] 
        self.i -= 1 
        self.cache |= {q} 
        return q 
