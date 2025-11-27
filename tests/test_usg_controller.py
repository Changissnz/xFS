from quant.usg_controller import * 
import unittest

### lone file test 
"""
python -m tests.test_usg_controller
"""
###
class USGControllerClass(unittest.TestCase):

    def test__USGController__full_run__case_1(self):

        D = {0:{1,2,3},\
            1:{0},2:{0,4,5},\
            3:{0},4:{2,6},\
            5:{2,6},6:{4,5,7},\
            7:{6}} 
        D = defaultdict(set,D) 


        usg = USGController()
        usg.set_new_search(is_dfs=True,start_node=0,d=D,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
                nextnode_priority_function=None,search_target_nodeset=set())
        S = usg.searches[0] 

        assert S.reference == 0
        Q = usg.move_search(0) 
        assert S.reference == 1
        Q2 = usg.move_search(0) 
        assert S.reference == 2 
        Q3 = usg.move_search(0)
        assert S.reference == 4 


        usg = USGController()
        usg.set_new_search(is_dfs=True,start_node=0,d=D,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
                nextnode_priority_function=None,search_target_nodeset={1,6})
        S = usg.searches[0] 

        Q4 = usg.move_search(0) 
        assert usg.found_target_nodeset[0] == {1}

        for _ in range(4): usg.move_search(0) 
        assert usg.found_target_nodeset[0] == {1,6} 


if __name__ == '__main__':
    unittest.main()