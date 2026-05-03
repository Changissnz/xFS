from graph_models.node_priority_function import * 
from morebs2.numerical_generator import prg__LCG 
import unittest 

def NodePriorityFunctionStruct__sample_graph_C5(): 
    return defaultdict(set, \
        {0: {1, 2, 3, 4}, \
        1: {0, 2, 3, 4}, \
        2: {0, 1, 3, 4}, \
        3: {0, 1, 2, 4}, \
        4: {0, 1, 2, 3}})

def NodePriorityFunctionStruct__case_C5(output_type,prg=None): 

    G = NodePriorityFunctionStruct__sample_graph_C5() 

    priority_type = "frequency" 
    node_weights = dict() 
    is_ascending = True 

    npf = NodePriorityFunctionStruct(priority_type,output_type,\
        node_weights = dict(),is_ascending=is_ascending,prg=prg) 
    return npf,G 

def NodePriorityFunctionStruct__case_C5_weighted(weights_map,output_type,is_ascending,prg=None): 

    G = NodePriorityFunctionStruct__sample_graph_C5() 
    priority_type = "weight"     
    npf = NodePriorityFunctionStruct(priority_type,output_type,weights_map,is_ascending,prg) 
    return npf,G 

### lone file test 
"""
py -m tests.test_node_priority_function
"""
class NodePriorityFunctionStructClass(unittest.TestCase):

    """
    frequency priority 
    """
    def test__NodePriorityFunctionStruct__next_node__case_1(self): 

        npf,G = NodePriorityFunctionStruct__case_C5("single",prg=None)

        i = 0 
        L = [i] 
        for _ in range(10): 
            i = npf.next_node(i,G[i]) 
            L.append(i) 

        assert L == [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0]

    """
    frequency priority 
    """
    def test__NodePriorityFunctionStruct__next_node__case_2(self): 
        prg = prg__LCG(55.4,-166.5,94.34,404.555) 

        npf,G = NodePriorityFunctionStruct__case_C5("single",prg=prg) 

        i = 0 
        L = [i] 
        for _ in range(10): 
            i = npf.next_node(i,G[i]) 
            L.append(i) 

        assert L == [0, 4, 2, 3, 1, 4, 1, 2, 3, 0, 4]

    """
    frequency priority 
    """
    def test__NodePriorityFunctionStruct__next_node__case_3(self): 
        npf,G = NodePriorityFunctionStruct__case_C5("sequence",prg=None) 

        i = 0 
        L = [[i]] 
        for _ in range(10): 
            i = npf.next_node(i,G[i]) 
            L.append(i)
            i = i[0]  

        assert L == [[0], [1, 2, 3, 4], \
            [2, 3, 4, 0], [3, 4, 0, 1], \
            [4, 0, 1, 2], [0, 1, 2, 3], \
            [1, 2, 3, 4], [2, 3, 4, 0], \
            [3, 4, 0, 1], [4, 0, 1, 2], \
            [0, 1, 2, 3]]

    """
    missing a weight for 4 
    """
    def test__NodePriorityFunctionStruct__next_node__case_4(self): 
        node_weights = {0:10,1:15,2:5,3:20} 

        npf,G = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=True,prg=None)

        npf2,G2 = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=False,prg=None)

        q = npf.next_node(0,G[0])
        q2 = npf.next_node(0,G2[0]) 

        assert q == q2 == 4 

    """
    weighted
    """
    def test__NodePriorityFunctionStruct__next_node__case_5(self): 
        node_weights = {0:10,1:15,2:5,3:20,4:25} 

        npf,G = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=True,prg=None)

        npf2,G2 = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=False,prg=None)

        q = npf.next_node(0,G[0])
        q2 = npf2.next_node(0,G2[0]) 

        assert q == 2 and q2 == 4 

    """
    weighted
    """
    def test__NodePriorityFunctionStruct__next_node__case_6(self): 

        node_weights = {0:10,1:15,2:5,3:20,4:25} 

        npf,G = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=True,prg=None)
        
        i = 2 
        L = [i] 
        for _ in range(10): 
            i = npf.next_node(i,G[i]) 
            L.append(i)
        assert L == [2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2]

        npf2,G2 = NodePriorityFunctionStruct__case_C5_weighted(\
            node_weights,output_type="single",is_ascending=False,prg=None)

        i = 2 
        L = [i] 
        for _ in range(10): 
            i = npf2.next_node(i,G[i]) 
            L.append(i)
        assert L == [2, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3]

if __name__ == '__main__':
    unittest.main()