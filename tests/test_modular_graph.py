from graph_models.graph_gen import * 
from graph_models.modular_graph import * 
import unittest

def ModularGraph_base_graph_sample_MR(): 
    prg = prg__LCG(24.31,625.52,6226.3,91766.4)
    g = GraphGen(False,prg,True,1000,0.005) 
    g.full_run() 
    graph_to_one_component(g.d,prg) 
    return g.d,prg 


### lone file test 
"""
py -m tests.test_modular_graph
"""
class ModularGraphClass(unittest.TestCase):

    def test__ModularGraph__one_reduction_case_1(self): 

        G,prg = ModularGraph_base_graph_sample_MR() 

        # case 1: no multi-reduction 
        x = ModularGraph(G,1,prg,allow_multireduction=False)

        L = [] 
        while not x.fin_stat: 
            x.one_reduction()
            L.append(len(x.base_graph_))

        assert L == [366, 184, 93, 41, 13, 3, 2, 1], "got {}".format(L)

        # case 2: multi-reduction 
        x2 = ModularGraph(G,1,prg,allow_multireduction=True)

        L2 = [] 
        while not x2.fin_stat: 
            x2.one_reduction()
            L2.append(len(x2.base_graph_))
        assert L2 == [11,1], "got {}".format(L2)

    """
    demonstrates variation between approximated shortest paths between 2 nodes in 
    a 1000-node graph. 
    """
    def test__ModularGraph__shortest_path__approx_case_1(self): 

        G,prg = ModularGraph_base_graph_sample_MR() 

        # case 1
        x = ModularGraph(G,15,prg,allow_multireduction=False)

        L = [] 
        while not x.fin_stat: 
            x.one_reduction()
            L.append(len(x.base_graph_))

        x.shortest_paths__init()        
        px = [] 

        for _ in range(10): 
            q = x.shortest_path__approx(5,988)
            px.append(q.cost()) 

        assert px == [5, 5, 7, 7, 5, 7, 7, 11, 6, 7]

if __name__ == '__main__':
    unittest.main()