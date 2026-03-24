from graph_models.graph_gen import * 
from graph_models.modular_graph import * 
import unittest

### lone file test 
"""
py -m tests.test_modular_graph
"""
class ModularGraphClass(unittest.TestCase):

    def test__ModularGraph__one_reduction_case_1(self): 

        prg = prg__LCG(24.31,625.52,6226.3,91766.4)
        g = GraphGen(False,prg,True,1000,0.005) 
        g.full_run() 
        graph_to_one_component(g.d,prg) 

        # case 1: no multi-reduction 
        x = ModularGraph(g.d,1,prg,allow_multireduction=False)

        L = [] 
        while not x.fin_stat: 
            x.one_reduction()
            L.append(len(x.base_graph_))

        ans_l = [366, 166, 97, 79, 34, 33, \
            32, 31, 30, 29, 28, 27, 26, 25, \
            24, 23, 22, 21, 20, 19, 18, 17, \
            16, 15, 14, 13, 12, 11, 10, 1]
        assert L == ans_l 

        # case 2: multi-reduction 
        x2 = ModularGraph(g.d,1,prg,allow_multireduction=True)

        L2 = [] 
        while not x2.fin_stat: 
            x2.one_reduction()
            L2.append(len(x2.base_graph_))
        assert L2 == [10,2,1]


if __name__ == '__main__':
    unittest.main()