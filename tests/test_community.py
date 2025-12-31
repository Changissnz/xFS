from graph_models.community import * 
from morebs2.numerical_generator import prg__LCG
from graph_models._mg_sample import * 
import unittest

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

if __name__ == '__main__':
    unittest.main()