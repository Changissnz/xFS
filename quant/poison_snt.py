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

    def __init__(self,npath:NodePath): 
        assert type(npath) == NodePath 
        self.npath = npath 
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
            return q,self.phase

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

class PoisonTarget: 

    def __init__(self,node_idn): 
        self.node_idn = node_idn
        self.poison_db = PoisonDB() 
        self.poison_reaction_log = []  
        return

    def predict_poison(self):
        next_reaction,stat = None,None 
        for poison,source_info in self.poison_db.poison2source_map.items(): 
            for source in source_info.keys(): 
                r,stat = self.predict_poison_(poison,source)
                if not stat: 
                    continue 
                return r,stat 
        return None,False 

    def predict_poison_(self,poison_idn,source_idn): 
        if len(self.poison_reaction_log) == 0: 
            return None 
        
        M = self.poison_reaction_log[0]

        prg = self.poison_db.poison_source_info(\
            poison_idn,source_idn) 

        pms = PoisonModelSNT(M,prg,min_max=DEFAULT_POISON_MODEL_SNT_MINMAX,idn=None)

        for i in range(1,len(self.poison_reaction_log)): 
            q = next(pms) 
            if not equal_iterables(q,self.poison_reaction_log[i],5): 
                return None,False 
        return next(pms),True 

    def register_poison(self,poison,source,prng): 
        self.poison_db.add_poison_source_info(poison,source,prng)
        return 