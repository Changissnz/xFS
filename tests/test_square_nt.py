from quant.square_nt import * 
from morebs2.numerical_generator import prg__single_to_nvec
import unittest

def sample_LCG_pair(R = [-0.25,0.25]): 

    prg = prg__LCG(45,-677,899,1900.05)

    def prg_(): 
        d0 = prg() - prg() + prg() - prg() - prg() 
        d1 = prg() - 2 * prg() 
        return modulo_in_range(d0 * d1,R)
    return prg,prg_ 

### lone file test 
"""
py -m tests.test_square_nt 
"""
###
class SquareMatrixNegativeTransformClass(unittest.TestCase):

    def test__SquareMatrixNegativeTransform__solve__case1(self): 

        prg,prg_ = sample_LCG_pair() 

        # subcase 1: 10 x 10 matrix 
        L = 10
        prg2 = prg__single_to_nvec(prg_,L)
        M = np.zeros((L,L))
        for i in range(L): 
            M[i] = prg2()

        smnt = SquareMatrixNegativeTransform(M,prg)
        smnt.solve() 

        X = np.round(smnt.transform_n_steps(L * L) + smnt.M,5)
        rounding_error = round(np.sum(X),5) 
        assert rounding_error == -0.41726 

        # subcase 2: 5 x 5 matrix 
        L2 = 5
        prg3 = prg__single_to_nvec(prg_,L2)
        M2 = np.zeros((L2,L2))
        for i in range(L2): 
            M2[i] = prg3() 
        smnt2 = SquareMatrixNegativeTransform(M2,prg)
        smnt2.solve() 

        X2 = np.round(smnt2.transform_n_steps(L2 * L2) + smnt2.M,5)
        rounding_error2 = round(np.sum(X2),5) 
        assert rounding_error2 == 0. 

    def test__SquareMatrixNegativeTransform__solve__case2(self): 
        R = [-2,2]

        # subcase 1: 5 x 5 matrix 
        L = 5
        prg,prg2 = sample_LCG_pair(R) 
        prg3 = prg__single_to_nvec(prg2,L)
        M2 = np.zeros((L,L))
        for i in range(L): 
            M2[i] = prg3() 
        smnt = SquareMatrixNegativeTransform(M2,prg,R)
        smnt.solve() 

        X = np.round(smnt.transform_n_steps(L * L) + smnt.M,5)
        rounding_error = round(np.sum(X),5) 
        assert rounding_error == 0. 

        Q = smnt.transform_n_steps(L * 12)
        assert round(np.sum(Q),5) == 88337731.00063
        assert round(np.sum(np.abs(Q)),5) == 431440326.03366

        # subcase 2: 10 x 10 matrix 
        L2 = 10 
        prg,prg2 = sample_LCG_pair(R) 
        prg3 = prg__single_to_nvec(prg2,L2)
        M2 = np.zeros((L2,L2))
        for i in range(L2): 
            M2[i] = prg3() 
        smnt2 = SquareMatrixNegativeTransform(M2,prg,R)
        smnt2.solve() 

        X2 = np.round(smnt2.transform_n_steps(L2 * L2) + smnt2.M,5)
        rounding_error2 = round(np.sum(X2),5) 
        assert rounding_error2 == -4.12055,"got {}".format(rounding_error2) 

if __name__ == '__main__':
    unittest.main()    