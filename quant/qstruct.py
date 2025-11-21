'''
the four variables are
 then:
 1. The rate that node i is a delegate to question j , W.
 2. The rate of contradiction, X.
 3. The duplicates of a question j asked to node i, Y .
 4. The mean of the answers of a node i to a question j, Z.
'''

class QStruct:

    def __init__(self,dim):
        assert len(dim) == 2
        assert type(dim[0]) == type(dim[1]) 
        assert min(dim) > 0 and type(dim[0]) == int 
        self.dim = dim 
        self.init_mat() 
    
    def init_mat(self): 
        # delegation rate
        self.drate = np.zeros(self.dim) 
        # contradiction rate 
        self.crate = np.zeros(self.dim) 
        # question frequency rate 
        self.frate = np.zeros(self.dim) 
        # average answer rate 
        self.arate = np.zeros(self.dim)  
        return

    def update(self,node_idn,q_idn,answer):
        f = self.frate[node_idn,q_idn]
        self.frate[node_idn,q_idn] += 1 
