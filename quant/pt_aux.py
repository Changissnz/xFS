from .poison_snt import * 


"""
database utilized by a target in simulation Poison Trace Bot. Target stores information 
on (source identifiers, poison identifiers, PRNG reactor) it or its predecessors, located 
at the same node, encounter over the course of Poison Trace Bot simulation activity. 
"""
class PoisonDB: 

    def __init__(self): 
        self.poison2source_prngs = dict() 
        return

    def add_poison_source_info(self,poison_idn,source_idn,prng): 
        if poison_idn not in self.poison2source_prngs: 
            self.poison2source_prngs[poison_idn] = dict() 
        self.poison2source_prngs[poison_idn][source_idn] = prng 
        return 

    def poison_source_info(self,poison_idn,source_idn): 
        if poison_idn not in self.poison2source_prngs: 
            return None 
        if source_idn not in self.poison2source_prngs[poison_idn]: 
            return None 
        return deepcopy(self.poison2source_prngs[poison_idn][source_idn]) 

    def source_poisons(self,source_idn): 
        poisons = [] 
        for k,d2 in self.poison2source_prngs.items(): 
            if source_idn in d2.items(): 
                poisons.append(k)  
        return sorted(poisons) 

    def sources(self): 
        sources = [] 
        for d2 in self.poison2source_prngs.values(): 
            sources.extend(d2.keys())
        return sorted(sources) 

"""
Poison Target 
"""
class PoisonTarget: 

    def __init__(self,node_idn,target_idn,prg,max_relays,num_sources,relay_accuracy_range): 
        assert type(prg) in {MethodType,FunctionType}
        self.node_idn = node_idn
        self.target_idn = target_idn 
        self.rplacer = RelayPlacement(self.node_idn,num_sources,max_relays,prg,relay_accuracy_range)
        self.prg = prg 

        self.poison_db = PoisonDB() 
        self.poison_reaction_log = []  

        # element := set(source)
        self.relay_suspects = []
        # element := source 
        self.relay_suspects_ = []
        self.start_guess = False 
        # element := (source,poison idn) 
        self.poison_guess_candidates = [] 
        self.source_guess = None 
        self.previous_source_guesses = [] 

        self.backtracker = None 
        self.guess_count = defaultdict(int) 

        self.terminated = False 

        self.verbose = False 

        self.backtracked = False 
        return

    def reset(self):
        self.relay_suspects.clear() 
        self.relay_suspects_.clear() 
        self.start_guess = False 
        self.poison_guess_candidates.clear() 
        self.source_guess = None 
        self.previous_source_guesses.clear() 
        self.poison_reaction_log.clear() 
        self.backtracked = False 

    def reproduce(self): 
        self.reset() 
        q = deepcopy(self) 
        q.target_idn += 1 
        return q 

    def __next__(self):
        self.next_backtrack() 

        if type(self.backtracker) == type(None) and self.terminated: 
            return True 
        return False 

    def start_backtrack(self,poison_path,source_info): 
        if self.backtracked: 
            return 
        self.backtracker = PoisonBacktracker(poison_path,source_info) 
        return 

    def next_backtrack(self): 
        if type(self.backtracker) == type(None): 
            return 
        q = next(self.backtracker) 

        print("{} is backtracking to {}".format(self.node_idn,q))
        # case: finished, register into DB and RelayPlacement 
        if type(q) in {MethodType,FunctionType}: 
            nodeset = self.backtracker.cache
            poison_idn = self.backtracker.poison_idn 
            source_idn = self.backtracker.source_idn 
            self.poison_db.add_poison_source_info(poison_idn,source_idn,q) 
            self.backtracker = None
            self.backtracked = True  
        return 

    def register_termination(self): 
        self.terminated = True 
        return 

    def is_poisoned(self): 
        return len(self.poison_reaction_log) > 0 

    """
    rule: if expressive poison, choose (source,poison) that exactly fits 
          poison_reaction_log. 

          if inexpressive poison, will have to make blind guess. 
    """
    def predict_poison(self):
        if not self.start_guess: 
            self.init_guess() 

        # case: not enough reactions to start prediction 
        if len(self.poison_reaction_log) < 2: 
            return None 

        is_expressive = self.is_expressive_poison() 
        poison_idn,source_idn = self.next_guess()

        if type(poison_idn) == type(None): 
            return None 

        r,stat = self.predict_poison__stepwise(poison_idn,source_idn,expressive_restriction=is_expressive) 
        if not stat: 
            return None 
        return r 

    def is_expressive_poison(self): 
        if len(self.poison_reaction_log) < 2: 
            return False 
        if type(self.poison_reaction_log[1]) != type(None): 
            return True 
        return False

    def next_guess(self): 
        if type(self.source_guess) == type(None): 
            self.source_guess = self.guess_source() 
        
        if type(self.source_guess) == type(None): 
            return None,None 

        poison_candidates = self.poison_db.source_poisons(self.source_guess)
        poison_candidates = prg_seqsort(poison_candidates,prg__single_to_int(self.prg)) 
        for x in poison_candidates: 
            q = (self.source_guess,x) 
            if q not in self.poison_guess_candidates: 
                return (self.source_guess,q) 
        
        self.source_guess = None 
        return self.next_guess() 

    def init_guess(self): 
        self.start_guess = True 
        if len(self.relay_suspects) == 0: 
            self.relay_suspects_ = self.poison_db.sources()  
            return 
        
        self.relay_suspects_ = self.relay_suspects[0] 
        for i in range(1,len(self.relay_suspects)): 
            self.relay_suspects_ = self.relay_suspects_ | self.relay_suspects[i] 
        return 

    def guess_source(self): 

        if len(self.relay_suspects_) == 0: 
            return None 

        i = int(self.prg()) % len(self.relay_suspects_)
        q = self.relay_suspects_.pop(i) 
        return q 

    def predict_poison__stepwise(self,poison_idn,source_idn,expressive_restriction:bool=True): 
        if len(self.poison_reaction_log) == 0: 
            return None,False 
        
        M = self.poison_reaction_log[0]

        prg = self.poison_db.poison_source_info(\
            poison_idn,source_idn) 

        pms = PoisonModelSNT(M,prg,min_max=DEFAULT_POISON_MODEL_SNT_MINMAX,idn=None)

        for i in range(1,len(self.poison_reaction_log)): 
            q = next(pms) 
            q2 = self.poison_reaction_log[i] 
            
            if type(q2) == type(None): 
                if expressive_restriction:
                    return None,False 
                continue 

            if not equal_iterables(q,q2,5): 
                return None,False 
        return next(pms),True 

    def register_poison_reaction(self,r): 
        self.poison_reaction_log.append(r) 
        return 
        
    def add_poison_source_info(self,poison,source,prng): 
        self.poison_db.add_poison_source_info(poison,source,prng)
        return 

    def add_relay(self,rsuspects:set): 
        self.relay_suspects.append(rsuspects)  
        return

class PoisonSource: 

    def __init__(self,source_idn,target_path_map,poison_matrix_map,expressive_mode:bool,prg):  
        assert type(source_idn) == int 
        assert type(target_path_map) == dict 
        assert type(poison_matrix_map) == dict 
        for k,v in poison_matrix_map.items(): 
            assert type(k) == int 
            assert type(v) == np.ndarray and len(v.shape) == 2 
        assert type(expressive_mode) == bool 
        assert type(prg) in {MethodType,FunctionType}

        self.source_idn = source_idn 
        self.target_path_map = target_path_map 
        self.poison_matrix_map = poison_matrix_map 
        self.expressive_mode = expressive_mode
        self.prg = prg 
        self.prg2 = deepcopy(self.prg) 

        self.active_poison_action = None 
        return 

    def __str__(self):
        S = "* active poison action" + "\n" 
        S += str(self.active_poison_action) + "\n"
        S += "\n\n* available poisons\n"
        S += "---------------------------------\n"
        for k,v in self.poison_matrix_map.items(): 
            S += "idn: " + str(k) + "\n\n" 
            S += str(v) + "\n" 
            S += "--------------------------------------"
            S += "\n" 
        
        return S 

    def __next__(self): 
        if self.active_poison_action.fin_stat: 
            self.active_poison_action = None 
            return None,None 

        q,mode = next(self.active_poison_action) 
        return q,mode 

    def clear_poison_action(self): 
        self.active_poison_action = None 

    def form_poison(self,p_idn,t_idn): 
        M_ = self.poison_matrix_map[p_idn] 
        p = PoisonModelSNT(M_,deepcopy(self.prg),min_max=DEFAULT_POISON_MODEL_SNT_MINMAX,idn=p_idn)

        # form poison
        npath = self.target_path_map[t_idn]  
        poison_type = "expressive" if self.expressive_mode else "inexpressive"
        pp = PoisonPath(npath,poison_type) 
        pp.load_poison(p) 
        return pp 

    def send_poison(self,occupied_targets:set=set()): 
        # choose target 
        possible_targets = sorted(set(self.target_path_map.keys()) - occupied_targets) 
        i = int(self.prg2()) % len(possible_targets) 
        target_idn = possible_targets[i] 

        # choose poison 
        P_ = sorted(self.poison_matrix_map) 
        i = int(self.prg2()) % len(P_)
        poison_idn = P_[i] 

        self.active_poison_action = self.form_poison(poison_idn,target_idn)
        return self.active_poison_action