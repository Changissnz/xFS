from graph_models.graph_gen import * 
from graph_models.modular_graph import * 
import time 
import unittest

def ModularGraph_base_graph_sample_MR(num_nodes=1000): 
    prg = prg__LCG(24.31,625.52,6226.3,91766.4)
    g = GraphGen(False,prg,True,num_nodes,0.005) 
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

    """
    Uses preprocessed approximator. Checks for peridistances.
    """
    def test__ModularGraph__shortest_path__approx_case_2(self): 

        G,prg = ModularGraph_base_graph_sample_MR(num_nodes=2000)

        # case 1
        t = time.time() 
        x = ModularGraph.default_instance(G,prg,approx_type="std",\
            record_peridistance=True,ensure_even_density=True) 
        x.full_reduction() 

        print("reduced: ",time.time() - t) 

        x.shortest_paths__init()
        x.set_pa_mode(True) 

        t = time.time() 

        q = [i for i in range(1,1500,49)]
        for i in range(len(q) -1): 
            u,v = q[i],q[i+1] 
            p = x.shortest_path__approx(u,v) 
            print("shortest paths for: {},{}".format(u,v)) 
            print(p) 
            print() 
        print("-- time elapsed for {} shortest paths: {}".format(len(q),time.time() - t))

        # check for correct peridistances
        q = x.node_to_base_nodeset(2790) 
        expected_distances = {64 : 3,960 : 4,1857 : 2,1990 : 1,\
        1865 : 4,1034 : 4,1424 : 4,1489 : 3,\
        1683 : 0,147 : 4,1620 : 3,279 : 3,\
        794 : 4,603 : 2,1949 : 2,29 : 3,\
        221 : 4,1565 : 1,1261 : 2,375 : 2,\
        313 : 4,1786 : 2,767 : 4}

        for q_ in q: 
            assert x.peridistance[q_] == expected_distances[q_] 

if __name__ == '__main__':
    unittest.main()