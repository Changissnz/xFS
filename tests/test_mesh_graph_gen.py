from graph_models.mesh_graph_gen import * 
import unittest

### lone file test 
"""
py -m tests.test_mesh_graph_gen
"""
###
class Mesh2DGraphGenClass(unittest.TestCase):

    def test__Mesh2DGraphGen__make__case_1(self):

        starting_idn = 5 
        num_rows = 3 
        num_cols = 4

        X = Mesh2DGraphGen(starting_idn,num_rows,num_cols)
        X.make() 

        assert X.G == defaultdict(set, \
            {5: {9, 6}, 6: {10, 5, 7}, \
            7: {8, 11, 6}, 8: {12, 7}, \
            9: {10, 13, 5}, 10: {9, 11, 6, 14}, \
            11: {10, 12, 15, 7}, 12: {8, 16, 11}, \
            13: {9, 14}, 14: {10, 13, 15}, \
            15: {16, 11, 14}, 16: {12, 15}})

        assert len(X.parallels) == num_rows 

        for q in X.parallels: 
            p = NodePath.from_graph(q,False) 
            assert len(p) == num_cols 
 
if __name__ == '__main__':
    unittest.main()