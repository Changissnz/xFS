from graph_models.node_path import *
from graph_models.graph_gen import * 
import time 
import unittest

### lone file test 
"""
py -m tests.test_node_path 
"""
class NodePathClass(unittest.TestCase):

    def test__NodePath__subpath_case_1(self): 

        PX = NodePath.preload([3, 7, 6, 7, 6],\
            [1, 1, 1, 1]) 

        PX11 = NodePath.preload([3, 7, 6],[1, 1]) 
        PX10 = NodePath.preload([3, 7],[1]) 
        PX01 = NodePath.preload([6, 7, 6],[1, 1]) 
        PX00 = NodePath.preload([7, 6],[1]) 

        assert PX11 == PX.head_subpath(2,True)
        assert PX10 == PX.head_subpath(2,False)
        assert PX01 == PX.tail_subpath(2,True)
        assert PX00 == PX.tail_subpath(2,False)
        return 

    def test__NodePath__subpath_case_2(self): 
        p = [100,67,78,45,1]
        pw = [6,7,9,9]
        N = NodePath.preload(p,pw) 

        T = N.tail_subpath(3,True)
        T2 = N.tail_subpath(3,False)

        A = NodePath.preload([45, 1],[9]) 
        A2 = NodePath.preload([1],[])

        assert T == A 
        assert T2 == A2 

    def test__NodePath__from_graph__case_1(self):
        num_vertices = 10 
        start_node = 5 
        is_dsg = True 
        G = generate_graph__path(num_vertices,start_node,is_dsg=is_dsg)

        N = NodePath.from_graph(G,is_dsg,head_node=None,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)

        assert N.p == [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        assert N.pweights == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test__NodePath__from_graph__case_2(self):
        num_vertices = 10 
        start_node = 5 
        is_dsg = True 
        G = generate_graph__path(num_vertices,start_node,is_dsg=is_dsg)

        try:
            NodePath.from_graph(G,is_dsg=False,head_node=None,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)
            assert False 
        except: 
            assert True 

    def test__NodePath__from_graph__case_3(self): 
        num_vertices = 10 
        start_node = 5 
        is_dsg = True 
        G = generate_graph__path(num_vertices,start_node,is_dsg=is_dsg)

        # subcase 1
        try:
            NodePath.from_graph(G,is_dsg=False,head_node=14,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)
            assert False 
        except: 
            assert True 

        # subcase 2 
        try:
            NodePath.from_graph(G,is_dsg=True,head_node=5,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)
            assert True 
        except: 
            assert False  
        
        # subcases 3 + 4 

        # check for 2 possible paths from undirected graph 
        is_dsg = False 
        G2 = generate_graph__path(num_vertices,start_node,is_dsg=is_dsg)

        ecfx = lambda u,v: DEFAULT_EDGE_COST_FUNCTION_2(u,v) if u != 8 else 4 

        P = NodePath.from_graph(G2,is_dsg=is_dsg,head_node=14,\
            edge_cost_function=ecfx)
        assert P.p == [14, 13, 12, 11, 10, 9, 8, 7, 6, 5]
        assert P.pweights == [1, 1, 1, 1, 1, 1, 4, 1, 1]

        P2 = NodePath.from_graph(G2,is_dsg=is_dsg,head_node=5,\
            edge_cost_function=ecfx)
        assert P2.p == [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        assert P2.pweights == [1, 1, 1, 4, 1, 1, 1, 1, 1]


if __name__ == '__main__':
    unittest.main()