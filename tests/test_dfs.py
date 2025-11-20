from graph_models._mg_sample import * 
from graph_models.dfs import * 
import unittest

"""
python -m tests.test_dfs
"""
class DFSCacheClass(unittest.TestCase):

    def test__DFSCache_exec_DFS__search_head_type_1__case3(self):

        q = test_dfs_graph_3()
        x = DFSCache(1,q,search_head_type=1)
        x.exec_DFS() 
        x.store_minpaths(num_paths=1000)

        npath1 = NodePath.preload([3, 1],[1])
        npath2 = NodePath.preload([3, 0, 1],[1, 1])
        npath3 = NodePath.preload([3, 2, 1],[1, 1])
        npath4 = NodePath.preload([3, 0, 2, 1],\
                [1, 1, 1])
        npath5 = NodePath.preload([3, 2, 0, 1],\
                [1, 1, 1])
        npaths = [npath1,npath2,npath3,npath4,npath5]

        assert len(x.min_paths[3]) == len(npaths)
        for pt in npaths: 
                assert pt in x.min_paths[3]

    def test__DFSCache_exec_DFS__search_head_type_1AND2__case2(self):
        g = test_dfs_graph_2()
        x = DFSCache(1,g,search_head_type=1)

        x.exec_DFS()

        q = x.paths_to_head(7)
        q = sorted(q,key=lambda x: x.cost())
        assert len(q) == 10
        assert q[0].cost() == 2

        x = DFSCache(1,g,search_head_type=2)
        x.exec_DFS()
        q2 = x.paths_to_head(7)
        assert len(q) > len(q2) 
        return

    def test__DFSCache_exec_DFS__search_head_type_1AND2__case4(self):
        q = test_dfs_graph_4()
        x = DFSCache(1,q,search_head_type=1)
        x.exec_DFS() 
        x.store_minpaths(num_paths=1000)

        x2 = DFSCache(1,q,search_head_type=2)
        x2.exec_DFS()
        x2.store_minpaths(num_paths=1000)

        distances = {0:1,1:0,2:1,3:2,4:3}
        for k,v in x.min_paths.items():
                assert len(v) == 1
                assert distances[k] == v[0].cost()
                assert len(v) == len(x2.min_paths[k])

    def test__DFSCache_exec_DFS__search_head_type_1__case1(self):

        q = test_dfs_graph_1()
        x = DFSCache(1,q,search_head_type=1)
        x.exec_DFS() 
        x.store_minpaths(num_paths=1000)

        assert x.min_paths[0][0].cost() == 1
        assert x.min_paths[2][0].cost() == 2
        assert x.min_paths[3][0].cost() == 2

if __name__ == '__main__':
    unittest.main()