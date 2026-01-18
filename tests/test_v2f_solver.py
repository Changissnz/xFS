from quant.v2f_solver import * 
from morebs2.numerical_generator import prg__single_to_nvec
import unittest

### lone file test 
"""
py -m tests.test_v2f_solver 
"""
###
class Vector2FloatSolverTypeS1Class(unittest.TestCase):

    def test__Vector2FloatSolverTypeS1__solve__case_1(self):

        V = np.array([5,0,6,7,-5,-13]) 
        prg = prg__LCG(45,-677,899,1900.05)

        f = 1200 
        f2 = -2456 

        # subcase 1 
        vs = Vector2FloatSolverTypeS1(V,f,prg)
        vs.solve() 
        assert round(abs(vs.output() - f),4) == 0 
        print("solved {} --> \n\t{} *\n\t{}".format(f,V,np.round(vs.W,5))) 

        # subcase 2 
        vs2 = Vector2FloatSolverTypeS1(V,f2,prg)
        vs2.solve() 
        assert round(abs(vs2.output() - f2),4) == 0 
        print("solved {} --> \n\t{} *\n\t{}".format(f2,V,np.round(vs2.W,5))) 

        # subcases 3-6
        q = [5,4,10,8] 
        for q_ in q: 
            V2 = prg__single_to_nvec(prg,q_)()
            f_ = (prg() - prg()) * (prg() - prg())
            vs3 = Vector2FloatSolverTypeS1(V2,f_,prg)
            vs3.solve() 
            assert round(abs(vs3.output() - f_),4) == 0 
            print("solved {} --> \n\t{} *\n\t{}".format(f_,V2,np.round(vs3.W,5)))  

    def test__Vector2FloatSolverTypeS1__solve__case_2(self):

        V = np.array([5,0,0,7,0,0])  
        prg = prg__LCG(45,-677,899,1900.05)

        f = 44567 
        f2 = -845611 

        vs = Vector2FloatSolverTypeS1(V,f,prg)
        vs.solve() 
        assert round(abs(vs.output() - f),4) == 0 

        vs2 = Vector2FloatSolverTypeS1(V,f2,prg)
        vs2.solve() 
        assert round(abs(vs2.output() - f2),4) == 0 

        q = [5,4,10,8] 
        for q_ in q: 
            V2 = prg__single_to_nvec(prg,q_)()
            f_ = (prg() - prg()) * (prg() - prg())
            vs3 = Vector2FloatSolverTypeS1(V2,f_,prg)
            vs3.solve() 
            assert round(abs(vs3.output() - f_),4) == 0 


if __name__ == '__main__':
    unittest.main()