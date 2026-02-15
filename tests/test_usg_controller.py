from quant.usg_controller import * 
from graph_models.graph_gen import * 
import unittest

### lone file test 
"""
py -m tests.test_usg_controller
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
        assert S.reference == 0,"got {}".format(S.reference) 
        Q3 = usg.move_search(0)
        assert S.reference == 2 

        usg = USGController()
        usg.set_new_search(is_dfs=True,start_node=0,d=D,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
                nextnode_priority_function=None,search_target_nodeset={1,6})
        S = usg.searches[0] 

        Q4 = usg.move_search(0) 
        assert usg.found_target_nodeset[0] == {1}

        for _ in range(4): usg.move_search(0) 
        assert usg.found_target_nodeset[0] == {1,6} 

    def test__USGController__full_run__case_2(self): 

        prg = prg__LCG(-78.6,400.56,202.2,-2511.3)
        prg2 = prg__LCG(1,1,1,5)

        #G = generate_graph__path(5,0,True)  
        G = generated_graph_sample_1000(vertex_degree=50,edge_connectivity=0.5) 


        usg = USGController()
        usg.set_new_search(is_dfs=True,start_node=0,d=G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
            nextnode_priority_function=DEFAULT_PRNG_TO_NEXTNODE_PRIORITY_FUNCTION__DFS(prg),\
            search_target_nodeset=set())

        usg.set_new_search(is_dfs=True,start_node=0,d=G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
            nextnode_priority_function=DEFAULT_PRNG_TO_NEXTNODE_PRIORITY_FUNCTION__DFS(prg),\
            search_target_nodeset=set())

        for _ in range(10): 
            q0,q1,q2 = usg.move_search(0)
            x = usg.searches[0] 
            #print("Q: ",q0,q1,q2) 
            #print("X: ",x.previous_edges)

            q0,q1,q2 = usg.move_search(1)
            x2 = usg.searches[1] 
            #print("Q1: ",q0,q1,q2) 
            #print("X1: ",x.previous_edges)
            assert x != x2 

if __name__ == '__main__':
    unittest.main()