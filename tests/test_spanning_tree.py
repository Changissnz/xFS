from graph_models.spanning_tree import * 
from morebs2.numerical_generator import prg__LCG 
from graph_models.graph_gen import * 
import unittest

def SpanningTree__graph__sample_ST(): 
    prg = prg__LCG(45.1,-17,18.6,91.6)
    is_realtime_gen = True 
    vertex_degree = 15 
    edge_connectivity = 0.2   
    gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity,\
            verbose=False)
    gg.full_run() 
    G = graph_to_one_component(gg.d,prg)
    return G,prg 



### lone file test 
"""
py -m tests.test_spanning_tree
"""
###
class SpanningTreeClass(unittest.TestCase):
    
    def test__SpanningTree__make__case_1(self):
        G,prg = SpanningTree__graph__sample_ST() 

        st = SpanningTree(G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,prg=None) 

        st.init_head(0) 
        st.make() 

        assert st.T == {0: [None, 0.0, None], \
                1: [0, 1.0, None], 2: [0, 1.0, None], \
                3: [0, 1.0, None], 5: [0, 1.0, None], \
                8: [0, 1.0, None], 9: [0, 1.0, None], \
                4: [1, 2.0, None], 7: [1, 2.0, None], \
                11: [5, 2.0, None], 14: [5, 2.0, None], \
                10: [9, 2.0, None], 13: [9, 2.0, None], \
                6: [4, 3.0, None], 12: [11, 3.0, None]}

        st2 = SpanningTree(G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,prg=prg) 
        st2.init_head() 
        st2.make() 

        assert st2.T == \
            {13: [None, 0.0, 1.0], 9: [0, 3.0, 0.82093], \
            0: [5, 7.0, 0.95285], 7: [1, 6.0, 0.9269], \
            10: [9, 2.0, 0.768], 1: [5, 5.0, 0.98566], \
            2: [0, 3.0, 0.63935], 3: [8, 6.0, 0.84217], \
            5: [14, 8.0, 0.97588], 8: [3, 7.0, 0.9599], \
            12: [10, 3.0, 0.96251], 4: [14, 8.0, 0.94246], \
            11: [5, 9.0, 0.89712], 14: [5, 7.0, 0.95302], \
            6: [4, 9.0, 0.99791]}


if __name__ == '__main__':
    unittest.main()