import numpy as np 

class QAGMat:

    def __init__(self,X:np.ndarray):
        assert type(X) == np.ndarray 
        self.X = X 
        return 