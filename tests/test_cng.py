from quant.cng import * 
import unittest 

"""
py -m tests.test_cng 
"""
class CLCGClass(unittest.TestCase):

    def test__CLCG__next__case1(self):
        start = 14 
        m = 3
        a = 7 
        n0,n1 = -10,111 

        lx = prg__LCG(56,3,11,1111)
        cg = CLCG(start,m,a,n0,n1,55,3,0,lx)

        q = [] 
        for i in range(100): 
            q.append(next(cg)) 

        assert cg.c2 == 11 
        assert q[56:] == ([55,3,16] * int(45/3))[:-1]
        assert q[:56] == [14, 39, -7, 97, 4, 4, 9, 24, \
                        69, 0, 0, -3, 109, 82, 3, 3, 6, \
                        15, 42, 3, 3, 6, 15, 42, 0, 0, -3, \
                        109, 82, 3, 3, 6, 15, 42, 0, 0, -3, \
                        109, 82, 2, 2, 3, 6, 15, 0, 0, -3, \
                        109, 82, 4, 4, 9, 24, 69, 3, 55]

    def test__CLCG__next__case2(self):
        start = 14 
        m = -3
        a = -7 
        n0,n1 = -100,111 
        lx = prg__LCG(56,3,11,1111)
        cg = CLCG(start,m,a,n0,n1,55,7,1,lx)

        q = [] 
        for i in range(100): 
            q.append(next(cg)) 

        assert q[56:] == ([7651, 7, 28, 91, 280, 847, 2548] * 7)[:-5]


if __name__ == '__main__':
    unittest.main()