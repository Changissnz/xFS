from graph_models._mg_sample import * 
from graph_models.graph_gen import * 
from graph_models.dfs import * 
import time 
import unittest

"""
py -m tests.test_dfs
"""
class DFSCacheClass(unittest.TestCase):

    def test__DFSCache_exec__search_head_type_1__case3(self):

        q = test_dfs_graph_3()
        x = DFSCache(1,q,search_head_type=1)
        x.exec() 
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

    def test__DFSCache_exec__search_head_type_1AND2__case2(self):
        g = test_dfs_graph_2()
        x = DFSCache(1,g,search_head_type=1)

        x.exec()

        q = x.paths_to_head(7)
        q = sorted(q,key=lambda x: x.cost())
        assert len(q) == 10
        assert q[0].cost() == 2

        x = DFSCache(1,g,search_head_type=2)
        x.exec()
        q2 = x.paths_to_head(7)
        assert len(q) > len(q2) 
        return

    def test__DFSCache_exec__search_head_type_1AND2__case4(self):
        q = test_dfs_graph_4()
        x = DFSCache(1,q,search_head_type=1)
        x.exec() 
        x.store_minpaths(num_paths=1000)

        x2 = DFSCache(1,q,search_head_type=2)
        x2.exec()
        x2.store_minpaths(num_paths=1000)

        distances = {0:1,1:0,2:1,3:2,4:3}
        for k,v in x.min_paths.items():
                assert len(v) == 1
                assert distances[k] == v[0].cost()
                assert len(v) == len(x2.min_paths[k])

    def test__DFSCache_exec__search_head_type_1__case1(self):

        q = test_dfs_graph_1()
        x = DFSCache(1,q,search_head_type=1)
        x.exec() 
        x.store_minpaths(num_paths=1000)

        assert x.min_paths[0][0].cost() == 1
        assert x.min_paths[2][0].cost() == 2
        assert x.min_paths[3][0].cost() == 2

    """
    test to demonstrate timeliness of algorithm on graph of 1000 nodes 
    """
    def test__DFSCache_exec__search_head_type_1__case2(self):
        prg = prg__LCG(-78.6,400.56,202.2,-2511.3)

        G = generated_graph_sample_1000(vertex_degree=1000,edge_connectivity=0.002) 
        G = graph_to_one_component(G,prg)
        dfsc = DFSCache(45,G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
            search_head_type=1,nextnode_priority_function=None,no_duplicate_touch_nodes=True)

        t = time.time() 
        dfsc.exec() 
        print("DFS runtime: ",time.time() - t)

        t = time.time() 
        q = dfsc.store_minpaths(num_paths=1)
        print("min paths runtime: ",time.time() - t)

        for v in dfsc.min_paths.values(): 
            for v_ in v: 
                assert does_path_exist(G,v_.p) 

if __name__ == '__main__':
    unittest.main()