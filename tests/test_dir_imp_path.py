from graph_models.dir_imp_path import * 
from morebs2.numerical_generator import * 
import unittest

def directed_implication_graph__sample_RE(): 
    num_nodes = 10 
    extra_edge_ratio = 0.2 
    prg = prg__LCG(-45.55,134.55,-76.44,9019.55) 
    return generate_directed_implication_path(num_nodes,extra_edge_ratio,prg,start_node_idn=0) 

"""
py -m tests.test_dir_imp_path
"""
class DirImpPathFunctions(unittest.TestCase):

    def test__generate_directed_implication_path__case_1(self):

        num_nodes = 10 
        extra_edge_ratio = 0.2 
        q = directed_implication_graph__sample_RE() 

        max_edges = sum([i for i in range(1,(num_nodes - 2) + 1)]) 

        q_base = generate_graph__path(num_nodes,0,True) 
        graph_childkey_fillin(q_base) 

        x = MicroGraph(q).sub_ve_score(MicroGraph(q_base)) 

        assert x[0] == 0 
        assert x[1] == ceil(max_edges * extra_edge_ratio)

    def test__generate_directed_implication_path__case_2(self): 

        q = directed_implication_graph__sample_RE() 
        M = verify_directed_implication_path(q)

        assert M[0] == 0 
        assert M[1] == 9 
        assert M[3] == True 

        # not directed from start to finish
        Q1 = generate_graph__path(9,0,False) 
        M1 = verify_directed_implication_path(Q1) 
        assert not M1[3] 

        # edges from source to target cannot go backwards. 
        Q2 = generate_graph__path(7,0,True) 
        Q2[3] |= {1} 
        Q2[4] |= {6} 
        M2 = verify_directed_implication_path(Q2)  
        assert not M2[3] 

if __name__ == '__main__':
    unittest.main()