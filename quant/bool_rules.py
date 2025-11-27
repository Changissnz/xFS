from graph_models.expr_tree import * 
from morebs2.numerical_generator import modulo_in_range 
from math import ceil  

"""
outputs a boolean variable expression. Not guaranteed to be 
satisfiable. 
"""
class BoolExprCNFGenerator:

    def __init__(self,var_list,prg,chunk_ratio_range,num_chunks=5): 
        assert len(var_list) > 0 
        assert 0.0 <= chunk_ratio_range[0] <= chunk_ratio_range[1] <= 1.0 
        self.var_list = var_list
        self.prg = prg 
        self.chunk_ratio_range = chunk_ratio_range 
        self.chunk_size_range = [ceil(self.chunk_ratio_range[0] * len(self.var_list)),\
                                ceil(self.chunk_ratio_range[1] * len(self.var_list)) + 1]
        self.num_chunks = num_chunks

        self.S = "" 
        return 

    def make(self): 
        for _ in range(self.num_chunks):
            S = self.one_chunk_() 
            self.S += S + " & " 
        self.S = self.S[:-3]
        return

    def one_chunk_(self): 
        chunk_size = modulo_in_range(int(self.prg()),self.chunk_size_range)

        q = deepcopy(self.var_list)
        S = "(" 
        for _ in range(chunk_size):
            i = int(self.prg()) % len(q) 
            s = q.pop(i)

            if int(self.prg()) % 2: 
                s = "!" + s 
            S += s + " | " 
        S = S[:-3] + ")" 
        return S 


class BoolExprContra: 

    def __init__(self,S,T):  
        self.preproc() 