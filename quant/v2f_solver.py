import numpy as np 
from copy import deepcopy 
from morebs2.matrix_methods import is_vector
from morebs2.numerical_generator import prg__single_to_int,prg__LCG,prg_choose_n,prg_decimal,modulo_in_range 
from types import FunctionType,MethodType 

DEFAULT_FIT_TYPE_1_COEFFICIENT_SCALE = [-2/1.2,2/1.2] 
DEFAULT_FIT_TYPE_1_MAX_ADJUSTMENT_STEPS = [1,1000] 

"""
Given a vector V, calculate a vector V2 of length |V| s.t. 
    V * V2 = f. 
"""
class Vector2FloatSolverTypeS1:  

    def __init__(self,V,f,prg):
        assert is_vector(V)
        assert type(prg) in {FunctionType,MethodType}

        self.V = V 
        self.f = float(f)
        self.prg = prg 
        self.W = np.zeros((len(self.V),)) 
        
        self.adjustment_indices = None 
        self.running_sum = 0

        self.c = 0
        self.fin_stat = False  

        self.update_log = [] 
        self.initial_weights() 

    def solve(self): 
        while not self.fin_stat: 
            next(self) 


    def __next__(self): 
        if self.fin_stat: 
            return None 

        self.c += 1 
        fit_exact = False 
        if self.c == self.adjustment_steps: 
             fit_exact = True 
             self.fin_stat = True 
        self.fit_next(fit_exact) 

    def output(self): 
        return sum(self.V * self.W) 


    def initial_weights(self): 
        self.W = self.W + 1 
        S = [i for i in range(len(self.V))]
        self.adjustment_indices = self.choose_non_zero_sum_subset(S) 
        self.number_of_adjustment_steps() 
        self.running_sum = sum(self.V * self.W) 

    def subset_coefficient_sum(self,ai): 
        return sum([self.V[i] for i in ai]) 

    def choose_non_zero_sum_subset(self,S,num_attempts=50): 
        if num_attempts < 0: assert False 

        prg_ = prg__single_to_int(self.prg)
        n = modulo_in_range(prg_(),[1,len(S)]) 
        q = prg_choose_n(deepcopy(S),n,\
            prg_,is_unique_picker=True)
        stat = round(self.subset_coefficient_sum(q),5) == 0 
        if stat: 
            return self.choose_non_zero_sum_subset(S,num_attempts-1)
        return q 

    def number_of_adjustment_steps(self):
        prg_ = prg__single_to_int(self.prg) 
        self.adjustment_steps = modulo_in_range(prg_(),DEFAULT_FIT_TYPE_1_MAX_ADJUSTMENT_STEPS)
        return

    def fit_next(self,fit_exact:bool): 
        s = 1.0 
        if not fit_exact: 
            s = modulo_in_range(self.prg(),DEFAULT_FIT_TYPE_1_COEFFICIENT_SCALE)

        diff = self.f - self.output()
        diff = diff * s 

        stat = False 
        while not stat: 
            stat = self.choose_non_zero_sum_subset(self.adjustment_indices)

        q = self.choose_non_zero_sum_subset(self.adjustment_indices)
        cs = self.subset_coefficient_sum(q)

        q2 = diff / cs 

        self.update_vec(q2,q) 
        self.update_log.append((q2,q)) 
        return q2, q 

    def update_vec(self,f,indices): 
        for i in indices: 
            self.W[i] += f  
        return
