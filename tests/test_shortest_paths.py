from graph_models.graph_gen import * 
from graph_models.shortest_paths import * 
from morebs2.numerical_generator import prg__LCG
import unittest

### lone file test 
"""
py -m tests.test_shortest_paths 
"""
###
class BDFSCacheClass(unittest.TestCase):

    def test__BDFSCache__full_run__case_1(self):

        lx = prg__LCG(55,3,19,212) 
        is_dsg = 0  
        prg = lx 
        is_realtime_gen = True 
        vertex_degree = 150 
        edge_connectivity = 0.33 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        gg.full_run() 
        D = gg.d 

        bcache = BDFSCache(0,D,is_bfs=True,prg=lx,edge_cost_function=lambda u,v:1,num_paths_per_node=10)
        bcache.exec()

        dcache = BDFSCache(0,D,is_bfs=False,prg=lx,edge_cost_function=lambda u,v:1,num_paths_per_node=10)
        dcache.exec()


        qx,qx2 = bcache.min_paths,dcache.min_paths

        for i in range(150):
            paths = qx[i]
            paths2 = qx2[i]

            assert paths[0].cost() == paths2[0].cost()
            assert paths[-1].cost() == paths2[-1].cost()

    def test__BDFSCache__full_run__case_2(self):

        lx = prg__LCG(55,3,19,212) 

        D = defaultdict(set,\
            {0:{1,2,3},\
            1:{0},\
            2:{0,6,9,11},\
            3:{0,4},\
            4:{3,5,9},\
            5:{4,6,11,15},\
            6:{2,5,7,8,15},\
            7:{6,10,14},\
            8:{6,10,12},\
            9:{2,4,11},\
            10:{7,8,13},\
            11:{2,5,9,12},\
            12:{8,11},\
            13:{10},\
            14:{7,15},\
            15:{5,6,14}}) 

        bcache = BDFSCache(0,D,is_bfs=True,prg=lx,edge_cost_function=lambda u,v:1,num_paths_per_node=10)
        bcache.exec() 

        dcache = BDFSCache(0,deepcopy(D),is_bfs=False,prg=lx,edge_cost_function=lambda u,v:1,num_paths_per_node=10)
        dcache.exec()

        qx,qx2 = bcache.min_paths,dcache.min_paths

        for i in range(16):
            paths = qx[i]
            paths2 = qx2[i]
            assert paths[0].cost() == paths2[0].cost()

        assert qx[0][0].cost() == 0 
        assert qx[1][0].cost() == 1 
        assert qx[2][0].cost() == 1 
        assert qx[3][0].cost() == 1

        assert qx[4][0].cost() == 2 
        assert qx[6][0].cost() == 2
        assert qx[9][0].cost() == 2 
        assert qx[11][0].cost() == 2

        assert qx[5][0].cost() == 3 
        assert qx[7][0].cost() == 3 
        assert qx[12][0].cost() == 3
        assert qx[15][0].cost() == 3
        assert qx[8][0].cost() == 3
 
        assert qx[10][0].cost() == 4  
        assert qx[14][0].cost() == 4 

        assert qx[13][0].cost() == 5

 

 
 


if __name__ == '__main__':
    unittest.main()