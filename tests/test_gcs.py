from graph_models.gcs import *
from graph_models._mg_sample import * 
import unittest

### lone file test 
"""
python -m tests.test_gcs
"""
###
class GCSContainerClass(unittest.TestCase):

    def test__GCSContainer_search__FullNeighborFitT2__case_1(self):
        X = greatest_common_subgraph_case_3()
        gcg3 = GCSContainer(X,search_type="full neighbor fit- type 2")
        gcg3.initialize_cache() 
        s1,s2 = gcg3.search(None) 
        assert s2 == 6
        return

    def test__GCSContainer_search__FullNeighborFitT2__case_1(self):
        X = greatest_common_subgraph_case_2()
        gcg2 = GCSContainer(X,search_type="full neighbor fit- type 2")
        gcg2.search_type = "full neighbor fit- type 1"
        gcg2.initialize_cache() 
        s1,s2 = gcg2.search(None) 
        assert s2 == 7
        return

    def test__GCSContainer_search__MatchingNeighborFit__case_1(self):
        X = greatest_common_subgraph_case_1()
        gcg1 = GCSContainer(X,search_type="matching neighbor fit")
        gcg1.initialize_cache() 
        s1,s2 = gcg1.search(None) 
        assert s2 == 7
        return

if __name__ == '__main__':
    unittest.main()