from graph_models.community import * 
from morebs2.numerical_generator import prg__LCG
import unittest

"""
py -m tests.test_community
"""
class RadialGraphCommunitiesClass(unittest.TestCase):

    def test__RadialGraphCommunities__exec__case1(self):
        D = defaultdict(set,{\
            0:{1,2},\
            1:{0,3},\
            2:{0,3},\
            3:{1,2,4},\
            4:{3,5,6},\
            5:{4,7},\
            6:{4,7},\
            7:{5,6,8},\
            8:{7,9,10},\
            9:{8,11},\
            10:{8,11},\
            11:{9,10}})

        prg = prg__LCG(56,765,-8165,911)
        rs = RadialGraphCommunities(D,prg,2)
        rs.exec()
        assert rs.community_nodesets == [{0, 1, 2, 3}, {8, 9, 10, 11}, {4, 5, 6, 7}]

if __name__ == '__main__':
    unittest.main()