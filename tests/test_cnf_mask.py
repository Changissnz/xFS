from quant.cng import * 
from quant.cnf_mask import * 
from graph_models._mg_sample import * 
import unittest

def sample_path(): 
    p = [3, 2, 1, 0]
    pw = [1, 1, 1]
    return NodePath.preload(p,pw)

"""
py -m tests.test_cnf_mask 
"""
class CNFGraphMaskClass(unittest.TestCase):

    def test__CNFGraphMask__mask_case1(self):
        d = base_graph_sample_E() 
        path = sample_path() 

        cgm = CNFGraphMask(path,d,prior_connectivity=None,prior_potential=1.0,prng=None)
        cgm.mask() 
        sg1 = cgm.to_subgraph() 

        ans1 = defaultdict(set, {0: {1, 4, 5}, 1: {0, 2}, 2: {1, 3}, 3: {2}, 4: {0}, 5: {0}})
        assert sg1 == ans1 

        d2 = base_graph_sample_F()
        cgm2 = CNFGraphMask(path,d2,prior_connectivity=None,prior_potential=1.0,prng=None)
        cgm2.mask() 
        sg2 = cgm2.to_subgraph() 
        assert 6 not in sg2 and 11 not in sg2 


    def test__CNFGraphMask__mask_case2(self):
        d3 = base_graph_sample_F() 
        path = sample_path() 

        cgm3 = CNFGraphMask(path,d3,prior_connectivity=0.66,prior_potential=1.0,prng=None)
        cgm3.mask() 
        sg3 = cgm3.to_subgraph() 
        ans3 = defaultdict(set, {3: {2}, 2: {8, 1, 3, 9}, 1: {0, 2}, 8: {2}, 9: {2}, 0: {1, 4, 5, 7}, 4: {0}, 5: {0}, 7: {0}})
        assert ans3 == sg3 
        assert cgm3.neighbor_sets == [set(), {8, 9}, set(), {4, 5, 7}]

        cgm4 = CNFGraphMask(path,d3,prior_connectivity=0.33,prior_potential=1.0,prng=None)
        cgm4.mask() 
        sg4 = cgm4.to_subgraph() 
        ans4 = defaultdict(set, {3: {2, 10}, 2: {8, 1, 3, 9}, 10: {3}, 1: {0, 2}, 8: {2}, 9: {2}, 0: {1, 4, 5, 7}, 4: {0}, 5: {0}, 7: {0}})
        assert sg4 == ans4 
        assert cgm4.neighbor_sets == [{10}, {8, 9}, set(), {4, 5, 7}]
        sg4_ = cgm4.to_subgraph(False) 
        assert sg4 != sg4_ 

if __name__ == '__main__':
    unittest.main()