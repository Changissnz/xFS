from graph_models.community import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg__LCG
from graph_models._mg_sample import \
    base_graph_sample_G,base_graph_sample_H
import unittest

def assert_connected_communities(G,comm): 
    for c in comm: 
        sg = MicroGraph(G).subgraph_by_nodeset_(c) 

        gd = GraphComponentDecomposition(sg.dg)
        gd.decompose() 
        assert len(gd.components) == 1,"got {}".format(len(gd.components))
        print("# of components: ",len(gd.components)) 

"""
py -m tests.test_community
"""
class RadialGraphCommunitiesClass(unittest.TestCase):

    def test__RadialGraphCommunities__exec__case1(self):
        D = base_graph_sample_G()

        prg = prg__LCG(56,765,-8165,911)
        rs = RadialGraphCommunities(D,prg,2)
        rs.exec()
        assert rs.community_nodesets == [{0, 1, 2, 3}, {8, 9, 10, 11}, {4, 5, 6, 7}]

class ReinforcementCommunityFinderClass(unittest.TestCase):

    """
    community detection on small graph 
    """
    def test__ReinforcementCommunityFinder__exec__case1(self):
        D = base_graph_sample_H() 

        prg = prg__LCG(-44,66,7898,-7991)
        rcf = ReinforcementCommunityFinder(D,prg,max_reassignment=False,verbose=False)   
        rcf.exec() 
        assert rcf.communities == [{3, 5}, {0, 1, 2, 6}, {4}]

        rcf2 = ReinforcementCommunityFinder(D,prg,max_reassignment=True,verbose=False)   
        rcf2.exec() 
        assert rcf2.communities == [{0, 1, 2, 3, 4, 5, 6}]

        return

    """
    community detection on small graph 
    """
    def test__ReinforcementCommunityFinder__exec__case2(self):

        D = base_graph_sample_G() 

        prg = prg__LCG(-44,66,7898,-7991)
        rcf = ReinforcementCommunityFinder(D,prg,max_reassignment=False,verbose=False)   
        rcf.exec() 
        assert rcf.communities == [{1}, {7}, {0, 2, 3, 4, 5, 6}, {8, 9, 10, 11}]

        rcf = ReinforcementCommunityFinder(D,prg,max_reassignment=False,verbose=False)   
        rcf.exec() 
        assert rcf.communities == [{9, 10, 11}, {0, 1, 2, 3}, {4}, {8, 5, 6, 7}]

        rcf2 = ReinforcementCommunityFinder(D,prg,max_reassignment=True,verbose=False)   
        rcf2.exec() 
        assert rcf2.communities == [{0, 1, 2, 3, 4, 5}, {9, 10, 11}, {8, 6, 7}]

        rcf2 = ReinforcementCommunityFinder(D,prg,max_reassignment=True,verbose=False)   
        rcf2.exec()
        assert rcf2.communities == [{4, 5}, {0, 1, 2, 3}, {6, 7, 8, 9, 10, 11}]

        D2 = base_graph_sample_H()
        prg = prg__LCG(55,62,-3344,771) 
        rcf3 = ReinforcementCommunityFinder(D2,prg,max_reassignment=False,verbose=False)   
        rcf3.exec() 
        assert rcf3.communities == [{0, 2, 3, 6}, {1, 4}, {5}],"got {}".format(rcf3.communities)
        return

    """
    demonstrates community detection on a graph of 250 nodes, 1 component. 
    """
    def test__ReinforcementCommunityFinder__partition_into_n_communities__case1(self): 
        D = base_graph_sample_FU()
        prg = prg__LCG(-44,66,7898,-7991)

        # case 1 
        rcf = ReinforcementCommunityFinder(D,prg,max_reassignment=False,verbose=False)   
        rcf.exec() 
        assert len(rcf.communities) == 74 
        Q = [len(c) for c in rcf.communities] 

        assert Q == [1, 1, 1, 1, 2, 3, 2, 1, 2, 1, 1, 1, 4, 1, 1, 2, 5, 7, 4, \
            2, 2, 9, 7, 14, 7, 1, 6, 3, 2, 2, 4, 5, 1, 1, 3, 3, 2, 1, 1, 3, 7,\
            3, 1, 7, 2, 1, 7, 1, 4, 1, 5, 2, 7, 10, 1, 2, 3, 6, 1, 3, 1, 1, 7,\
            2, 7, 6, 7, 1, 11, 1, 1, 1, 9, 1] 

        # case 2 
        rcf2 = ReinforcementCommunityFinder(D,prg,max_reassignment=False,verbose=False)   
        rcf2.exec() 

        assert len(rcf2.communities) == 86 
        Q2 = [len(c) for c in rcf.communities] 
        assert Q2 == [1, 1, 1, 1, 2, 3, 2, 1, 2, 1, 1, 1, 4, 1, 1, 2, 5, 7, 4, \
            2, 2, 9, 7, 14, 7, 1, 6, 3, 2, 2, 4, 5, 1, 1, 3, 3, 2, 1, 1, 3, 7, \
            3, 1, 7, 2, 1, 7, 1, 4, 1, 5, 2, 7, 10, 1, 2, 3, 6, 1, 3, 1, 1, 7, \
            2, 7, 6, 7, 1, 11, 1, 1, 1, 9, 1]

        # case 3
        num_comm = 10 
        comm = ReinforcementCommunityFinder.partition_into_n_communities(D,num_comm,prg,verbose=False) 
        Q3 = [len(c) for c in comm] 
        assert Q3 == [56, 5, 2, 66, 79, 12, 1, 9, 11, 9] and sum(Q3) == 250 and len(Q3) == num_comm, \
            "got {}".format(Q3)

        # case 4
        num_comm = 4 
        comm = ReinforcementCommunityFinder.partition_into_n_communities(D,num_comm,prg,verbose=False) 
        Q4 = [len(c) for c in comm] 
        assert Q4 == [223, 4, 12, 11] and sum(Q3) == 250 and len(Q4) == num_comm,"got {}".format(Q4)

    def test__ReinforcementCommunityFinder__partition_into_n_communities__case2(self): 
        D = base_graph_sample_25N() 
        prg = prg__LCG(67,-200,3111,9000.3) 
        num_comm = 5
        comm = ReinforcementCommunityFinder.partition_into_n_communities(D,num_comm,prg,fast_part=True,\
            verbose=False) 
        Q3 = [len(c) for c in comm] 
        assert Q3 == [379, 427, 472, 555, 667], "got {}".format(Q3)


if __name__ == '__main__':
    unittest.main()