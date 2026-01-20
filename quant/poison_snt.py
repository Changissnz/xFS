from .square_nt import * 
from graph_models.node_path import * 

class PoisonModelSNT(SquareMatrixNegativeTransform): 

    def __init__(self,M,prg,min_max=[-1.,1.]):
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
        return

    def load_poison(self,p:PoisonModelSNT): 
        assert type(p) == PoisonModelSNT
        self.p = p 
        return

    def path_head(self): 
        return self.npath.head() 

    def __next__(self): 
        assert type(self.p) == PoisonModelSNT 
        if self.fin_stat: return 

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
        return next(self.p) 

class PoisonRelay: 

    def __init__(self,owner:int,recognition_accuracy:float,prg):  
        assert type(owner) == int 
        assert 0. <= recognition_accuracy <= 1. 
        assert type(prg) in {MethodType,FunctionType} 

        self.owner = owner 
        self.recognition_accuracy = recognition_accuracy 
        self.prg = prg 
        return 

    def register_poison(self,pp:PoisonPath,all_source_candidates:set):  
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