from graph_models.node_path import *
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

if __name__ == '__main__':
    unittest.main()