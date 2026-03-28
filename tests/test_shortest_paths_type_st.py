from graph_models.graph_gen import * 
from graph_models.modular_graph import * 
from graph_models.shortest_paths_type_st import * 
import time 
import unittest

def ShortestPathsApproximatorTypeST__base_graph_sample_ST(): 
    prg = prg__LCG(243.31,-66625.52,6226.3,9766.4)
    g = GraphGen(False,prg,True,2000,0.005) 

    g.full_run() 
    graph_to_one_component(g.d,prg) 
    return g.d 



### lone file test 
"""
py -m tests.test_shortest_paths_type_st
"""
class ShortestPathsApproximatorTypeSTClass(unittest.TestCase):

    def test__ShortestPathsApproximatorTypeST__one_reduction_case_1(self): 
        G = ShortestPathsApproximatorTypeST__base_graph_sample_ST() 
        prg = prg__LCG(15243.31,-2625.52,16226.3,5000.4)
        spa = ShortestPathsApproximatorTypeST(G,DEFAULT_EDGE_COST_FUNCTION_2,prg,verbose=False)

        q = [i for i in range(1,2000,49)] 
        q2 =[i for i in range(2,2000,21)] 
        q3 = q + q2 
        q4 = [(q_,q2_) for (q_,q2_) in zip(q,q2)] 
        q4_ = [] 
        for r in q4: 
            q4_.extend(r) 
        q4 = q3 + q4_ 

        print("time test for {} arbitrary source-target path calculations.".format(len(q4))) 
        t = time.time()
        for i in range(len(q4) -1): 
            u,v = q4[i],q4[i+1] 
            p = spa.shortest_path__approx(u,v) 
            if type(p) == type(None): 
                print("no path for ({},{})".format(u,v))
                continue 
            print("approximate shortest path for ({},{}): {}".format(u,v,p.cost()))  
        print("-- time: {}".format(time.time() - t)) 

if __name__ == '__main__':
    unittest.main()