from graph_models.graph_gen import base_graph_sample_25N
from graph_models.radial_subgraph import * 
from morebs2.numerical_generator import prg__LCG 
import time 
import unittest

def graph__sample_RAD1(): 
    return defaultdict(set,{\
        0:{1,3},\
        1:{0,2,6,9,12},\
        2:{1,5},\
        3:{0,4},\
        4:{3,8},\
        5:{2,6},\
        6:{1,5,7},\
        7:{6,13,17},\
        8:{4},\
        9:{1,10,12},\
        10:{9,11,15},\
        11:{10,14},\
        12:{1,9,13},\
        13:{7,12,17},\
        14:{11,15},\
        15:{10,14,16},\
        16:{15},\
        17:{7,13}})

def graph__sample_RAD2(): 

    return defaultdict(set,{\
        0:{1},\
        1:{2},\
        2:{3,4},\
        3:{5,6},\
        4:{5}})


### lone file test 
"""
py -m tests.test_radial_subgraph
"""
###
class RadialSubgraphFetcherClass(unittest.TestCase):

    def test__RadialSubgraphFetcher__subgraph__case1(self):  
        D = graph__sample_RAD1()
        prg2 = prg__LCG(8711,754,-675456,9999) 

        rsg = RadialSubgraphFetcher(D,prg=prg2) 

        x = rsg.subgraph(0,1) 
        assert x == defaultdict(set, {0: {1, 3}, 1: {0}, 3: {0}})

        x2 = rsg.subgraph(0,2) 
        assert x2 == \
            defaultdict(set, {0: {1, 3}, 1: {0, 2, 6, 9, 12}, 2: {1}, 3: {0, 4}, 4: {3}, 6: {1}, 9: {1, 12}, 12: {1, 9}})

        x3 = rsg.subgraph(13,0) 
        assert x3 == defaultdict(set, {13: set()})

        x4 = rsg.subgraph(13,1) 
        assert x4 == defaultdict(set, {7: {17, 13}, 12: {13}, 13: {17, 12, 7}, 17: {13, 7}})

        x5 = rsg.subgraph(13,3) 
        assert {11,14,15,16}.intersection(set(x5.keys())) == set() 

    def test__RadialSubgraphFetcher__subgraph__case2(self):
        D2 = graph__sample_RAD2() 
        rsg2 = RadialSubgraphFetcher(D2,return_type="paths") 

        z = rsg2.subgraph(1,1) 
        assert z == defaultdict(set, {1: {2}, 2: set()}) 

        z2 = rsg2.subgraph(1,2)
        assert z2 == defaultdict(set, {1: {2}, 2: {3, 4}, 3: set(), 4: set()})

class QuickSubgraphFetcherClass(unittest.TestCase): 

    def test__QuickSubgraphFetcher__subgraph__case1(self): 
        D = graph__sample_RAD1()
        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 

        qsf = QuickSubgraphFetcher(D,prg)
        D_ = qsf.subgraph(5,5)

        x = qsf.subgraph(0,1) 
        assert x == defaultdict(set, {0: {1, 3}, 1: {0}, 3: {0}})

        x2 = qsf.subgraph(0,2) 
        assert x2 == \
            defaultdict(set, {0: {1, 3}, 1: {0, 2, 6, 9, 12}, 2: {1}, 3: {0, 4}, 4: {3}, 6: {1}, 9: {1, 12}, 12: {1, 9}})

        x3 = qsf.subgraph(13,0) 
        assert x3 == defaultdict(set, {13: set()})

        x4 = qsf.subgraph(13,1) 
        assert x4 == defaultdict(set, {7: {17, 13}, 12: {13}, 13: {17, 12, 7}, 17: {13, 7}})

    def test__QuickSubgraphFetcher__subgraph__case2(self): 

        D = base_graph_sample_25N() 
        prg = prg__LCG(556,6344,-117,9199.1) 

        print("retrieving subgraph on graph of 2500 nodes")
        t = time.time()
        qsf = QuickSubgraphFetcher(D,prg)
        D_ = qsf.subgraph(5,5)
        print("-- exec time: ",time.time() - t)

if __name__ == '__main__':
    unittest.main()