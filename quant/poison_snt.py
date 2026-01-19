from .square_nt import * 

class PoisonModelSNT(SquareMatrixNegativeTransform): 

    def __init__(self,M,prg,min_max=[-1.,1.]):
        super().__init__(M,prg,min_max) 
        return 

    def __next__(self): 
        if self.fin_stat: 
            return None 

        return super().__next__()

