"""
gain/loss table for use with class<ExprTree> 
"""
from morebs2.numerical_generator import modulo_in_range 
import numpy as np 

class GLExprTableGen: 

    def __init__(self,var_size,gain_range,loss_range,prg):
        assert var_size > 0 and type(var_size) == int  
        assert gain_range[1] >= gain_range[0] > 0.0
        assert 0.0 > loss_range[1] >= loss_range[0]
        self.var_size = var_size  
        self.gain_range = gain_range
        self.loss_range = loss_range 
        self.prg = prg 
        self.table = np.zeros((len(var_size),2))
        self.make_table() 
        return

    def make_table(self): 
        self.table[:,0] = [self.one_gl(True) for _ in range(self.var_size)] 
        self.table[:,1] = [self.one_gl(False) for _ in range(self.var_size)] 
    
    def one_gl(self,is_gain:bool):
        ratio = self.one_ratio() 
        R = self.gain_range if is_gain else self.loss_range 
        return R[0] + ratio * (R[1] - R[0])

    def one_ratio(self): 
        one,two = abs(self.prg()),abs(self.prg())
        ratio = [one,two] if one <= two else [two,one] 
        return ratio[0] / ratio[1] 
        