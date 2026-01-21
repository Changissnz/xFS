from .square_nt import * 
from graph_models.node_path import * 
from morebs2.matrix_methods import equal_iterables

DEFAULT_POISON_MODEL_SNT_MINMAX = [-1.,1.]

class PoisonModelSNT(SquareMatrixNegativeTransform): 

    def __init__(self,M,prg,min_max=DEFAULT_POISON_MODEL_SNT_MINMAX,idn=None):
        self.idn = idn 
        super().__init__(M,prg,min_max) 
        return 

    def __next__(self): 
        if self.fin_stat: 
            return None 

        return super().__next__()

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
        return

    def load_poison(self,p:PoisonModelSNT): 
        assert type(p) == PoisonModelSNT
        self.p = p 
        return

    def path_head(self): 
        return self.npath.head() 

    def __next__(self): 
        assert type(self.p) == PoisonModelSNT 
        if self.fin_stat: return None,None 

        if self.phase == "send": 
            q = self.send_next()
            if type(q) == type(None): 
                self.phase = "react" 
                return next(self) 
            return q,self.phase 
        else: 
            q = self.react_next() 
            if type(q) == type(None): 
                self.fin_stat = True
                return None,None  
            q_ = q if self.poison_type == "expressive" else None 
            return q_,self.phase

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
        return 

    def relay_poison(self,pp:PoisonPath,all_source_candidates:set):  
        assert type(pp) == PoisonPath 
        assert type(all_source_candidates) == set 

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

class PoisonBacktracker: 

    def __init__(self,p:PoisonPath):
        assert type(p) == PoisonPath 
        self.p = p  
        self.fin_stat = False 
        self.i = -1  
        self.l = -ceil(len(self.p.npath) / 2)
        return 

    def __next__(self): 
        if self.fin_stat: 
            return None 

        if self.i == self.l: 
            self.fin_stat = True 
    
        q = self.p.npath[self.i] 
        self.i -= 1 
        return q 

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

class PoisonTarget: 

    def __init__(self,node_idn,prg): 
        assert type(prg) in {MethodType,FunctionType}
        self.node_idn = node_idn
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

        self.guess_count = defaultdict(int) 
        return

    def reset(self):
        self.relay_suspects.clear() 
        self.relay_suspects_.clear() 
        self.start_guess = False 
        self.poison_guess_candidates.clear() 
        self.source_guess = None 
        self.previous_source_guesses.clear() 

    """
    rule: if expressive poison, choose (source,poison) that exactly fits 
          poison_reaction_log. 

          if inexpressive poison, will have to make blind guess. 
    """
    def predict_poison(self):

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