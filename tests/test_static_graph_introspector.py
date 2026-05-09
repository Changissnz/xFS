from quant.static_graph_introspector import * 
from morebs2.numerical_generator import prg__LCG
import unittest

def StaticGraphIntrospectorTypeCNO__sample_graph_MID(): 

    G = defaultdict(set, {0: {5}, 1: {8, 17, 5, 6}, 2: {4, 7}, \
        3: {16, 17, 12, 7}, 4: {2}, 5: {0, 1, 12, 6}, \
        6: {8, 1, 5, 16}, 7: {2, 3}, 8: {1, 17, 6, 10, 14}, \
        9: {19, 11}, 10: {8, 13}, 11: {16, 9, 19}, 12: {16, 3, 5}, \
        13: {10, 15}, 14: {8, 19}, 15: {13}, 16: {3, 11, 12, 6}, \
        17: {8, 1, 18, 3}, 18: {17}, 19: {9, 11, 14}})
    return G 

def StaticGraphIntrospectorTypeCNO__sample_FIRST(is_bfs,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg): 

    G = StaticGraphIntrospectorTypeCNO__sample_graph_MID() 

    node_weight_range = None 
    edge_weight_range = [3,45] 
    is_dsg = False 
    ascending_priority = True 
    cycle_length_range = [5,17]

    S = StaticGraphIntrospectorTypeCNO.generate_instance(G,node_weight_range,edge_weight_range,is_dsg,is_bfs,ascending_priority,cycle_length_range,\
        edges_can_be_forgotten,ref_nodes_can_be_repeated,prg)
    
    return S 

### lone file test 
"""
py -m tests.test_static_graph_introspector 
"""
###
class StaticGraphIntrospectorTypeCNOClass(unittest.TestCase):

    def test__StaticGraphIntrospectorTypeCNO__next__case_1(self): 
        is_bfs = True 
        edges_can_be_forgotten = 1.0 
        ref_nodes_can_be_repeated = 1.0 
        prg = prg__LCG(55.4,-166.5,94.34,404.555) 
        S = StaticGraphIntrospectorTypeCNO__sample_FIRST(is_bfs,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg) 

        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat: 
            next(S) 
            c += 1 

        assert c == 132 

        X = S.output_minpaths(2) 
        q = sorted(X.keys())

        actual_path_numbers = {0:0,\
            1:0,2:1,3:1,4:1,5:0,6:0,\
            7:1,8:0,9:0,10:0,11:0,\
            12:2,13:0,14:0,15:0,16:1,\
            17:0,18:0,19:0}

        for q_ in q: 
            p = X[q_]
            assert len(p) == actual_path_numbers[q_]
        return

    def test__StaticGraphIntrospectorTypeCNO__next__case_2(self): 
        
        is_bfs = True 
        edges_can_be_forgotten = 0.5 
        ref_nodes_can_be_repeated = 0.2 
        prg = prg__LCG(76.4,-6666.5,4.34,4004.555) 
        S = StaticGraphIntrospectorTypeCNO__sample_FIRST(is_bfs,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg) 

        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat: 
            next(S) 
            c += 1 

        assert c == 52 

        X = S.output_minpaths(2) 
        q = sorted(X.keys())

        actual_path_numbers = {0 : 2,\
            1 : 2,2 : 1,3 : 1,4 : 0,\
            5 : 2,6 : 1,7 : 1,8 : 2,\
            9 : 0,10 : 2,11 : 1,12 : 2,\
            13 : 2,14 : 2,15 : 2,16 : 1,\
            17 : 2,18 : 2,19 : 2} 

        for q_ in q: 
            p = X[q_]
            assert len(p) == actual_path_numbers[q_]

    def test__StaticGraphIntrospectorTypeCNO__next__case_3(self): 

        is_bfs = False 
        edges_can_be_forgotten = 0.5 
        ref_nodes_can_be_repeated = 0.2 
        prg = prg__LCG(76.4,-6666.5,4.34,4004.555) 
        S = StaticGraphIntrospectorTypeCNO__sample_FIRST(is_bfs,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg) 

        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat: 
            next(S) 
            c += 1 

        assert c == 200  

        X = S.output_minpaths(2) 
        q = sorted(X.keys())

        actual_path_numbers = {0 : 0,\
            1 : 0,2 : 1,3 : 0,4 : 1,\
            5 : 0,6 : 0,7 : 1,8 : 0,\
            9 : 0,10 : 0,11 : 0,12 : 0,\
            13 : 0,14 : 0,15 : 0,16 : 0,\
            17 : 0,18 : 0,19 : 0} 

        for q_ in q: 
            p = X[q_]
            assert len(p) == actual_path_numbers[q_]


    def test__StaticGraphIntrospectorTypeCNO__next__case_3(self): 
        # run <StaticGraphIntrospectorTypeCNO> 
        is_bfs = True 
        edges_can_be_forgotten = 0.5 
        ref_nodes_can_be_repeated = 0.8 
        prg = prg__LCG(76.4,-6666.5,4.34,4004.555) 
        S = StaticGraphIntrospectorTypeCNO__sample_FIRST(is_bfs,edges_can_be_forgotten,ref_nodes_can_be_repeated,prg) 
        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat: 
            next(S) 
            c += 1 

        X = S.output_minpaths(2) 

        # run normal BFS process 
        G = StaticGraphIntrospectorTypeCNO__sample_graph_MID() 
        B = BFSCache(7,G,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None,no_duplicate_touch_nodes=False)
        B.exec() 

        B.store_minpaths(num_paths=2) 
        mpaths = B.min_paths 

        # compare differences between existing shortest pairs 
        cdiff = 0 
        for k,v in mpaths.items(): 
            q = len(X[k]) 
            if not q: continue 

            r = len(v[0]) 
            r2 = len(X[k][0])
            cdiff += (r != r2)

        assert cdiff == 11 

if __name__ == '__main__':
    unittest.main()