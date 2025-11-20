from graph_models._mg_sample import * 
from graph_models.bfs import * 
import unittest 

"""
python -m tests.test_bfs
"""
class BFSCacheClass(unittest.TestCase):

    def test__BFSCache_exec__case1(self):

        q = test_dfs_graph_4()
        x = BFSCache(1,q)
        x.exec() 
        x.store_minpaths(num_paths=1000)
        distances = {0:1,1:0,2:1,3:2,4:3}

        for k,v in x.min_paths.items():
            assert distances[k] == v[0].cost()
        return 

    def test__BFSCache_exec__case2(self):

        q = test_dfs_graph_2()
        x = BFSCache(1,q)
        x.exec() 
        x.store_minpaths(num_paths=1000)

        distances = {0:1,1:0,2:1,3:2,4:3,5:2,6:3,7:2,8:3}
        for k,v in x.min_paths.items():
            assert distances[k] == v[0].cost(), "key {}, want {}, got {}".format(k,distances[k],v[0].cost())
        return 
        
if __name__ == '__main__':
    unittest.main()