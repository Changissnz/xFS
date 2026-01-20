from .v2f_solver import * 
from morebs2.search_space_iterator import * 

"""
transforms a square matrix M of dim (n x n) into its negative 
-M. 

There are (n * n) steps in this transformation, every step transforming 
index (i,j) into its negative. Iteration of indices starts at (0,0) and 
increments with index 0 first (column-wise). 

At every index (i,j), the transformation matrix S is constructed by this procedure: 
- set S to an identity matrix. 
- find a vector R of length n s.t. for matrix M' (the matrix of M after some k transformations), 
  row M'[i] * R = -M'[i,j]. 
- replace column S[:,j] with R. 

At the end of these (n * n) steps, a final transformation matrix E for addition instead of dot product, 
this the error term, is calculated as 
E = -M - M' --> 
-M = -M' + E. 

NOTE: 
A quirky procedure that exemplifies geometric noise involved. 
"""
class SquareMatrixNegativeTransform: 

    def __init__(self,M,prg,min_max=[-1.,1.]):
        assert M.shape[0] == M.shape[1]
        assert len(M.shape) == 2 
        assert is_valid_range(min_max,False,False) or is_valid_range(min_max,True,False) 
        assert min_max[0] <= np.min(M) <= np.max(M) <= min_max[1]
        self.M = M 
        self.M_ = deepcopy(M)
        self.prg = prg 

        bounds = np.array([[0,M.shape[0]],\
                    [0,M.shape[1]]]) 
        start_point = bounds[:,0]
        column_order = [0,1] 
        ssi_hop = np.array(M.shape)  
        self.ssi = SearchSpaceIterator(bounds,start_point,column_order,\
            ssi_hop,cycleOn = False,cycleIs = 0)

        self.transform_log = [] 

        self.error_term = None 
        self.fin_stat = False 
        return

    def solve(self): 
        while not self.fin_stat: 
            next(self) 

    def transform_n_steps(self,n):
        assert self.fin_stat, "not solved yet." 
        
        M_ = deepcopy(self.M)
        for _ in range(n): 
            q = _ % len(self.transform_log)
            M2 = self.transform_log[q]  
            M_ = np.dot(M_,M2)     
            if _ == len(self.transform_log) - 1: 
                M_ += self.error_term 
        return M_ 

    def __next__(self):

        if self.fin_stat: 
            return 

        if self.ssi.finished(): 
            S = self.last_transform() 
            self.fin_stat = True 
            return S  

        i0,i1 = next(self.ssi) 
        i0,i1 = int(i0),int(i1)
        S = np.identity(self.M_.shape[0])
        r0 = deepcopy(self.M_[i0])
        f = -self.M_[i0,i1]

        vs = Vector2FloatSolverTypeS1(r0,f,self.prg,[-1.,1.],1)
        vs.solve() 
        S[:,i1] = vs.W 
        self.transform_log.append(S) 
        self.M_ = np.dot(self.M_,S) 
        return deepcopy(self.M_) 

    def last_transform(self): 
        q = self.M * -1 
        q_ = q - self.M_ 
        self.error_term = q_ 
        return q_ 