from graph_models.graph_gen import * 
from quant.cng import * 
import unittest

### lone file test 
"""
py -m tests.test_graph_gen 
"""
###
class GraphGenClass(unittest.TestCase):

    def test__GraphGen__full_run__case_1(self):
        lx = prg__LCG(55,3,19,212) 
        lx2 = prg__LCG(31,78,2,2120) 
        lx3 = prg__LCG(0,0,0,2) 

        # case 1 
        ##print("11")
        is_dsg = 0  
        prg = lx 
        is_realtime_gen = True 
        vertex_degree = 12 
        edge_connectivity = 0.5 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg.d) == 0 
        gg.full_run() 
        assert gg.current_edge_degree == 33 
        assert max_simple_edges(12) == 66 

        # case 2 
        ##print("22")
        is_dsg = 1 
        prg = lx3 
        gg2 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg2.d) == 0 
        gg2.full_run() 
        assert gg2.current_edge_degree == 66 

        # case 3
        ##print("33")
        prg = lx2 
        is_realtime_gen = False 
        gg3 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg3.d) == 12 
        gg3.full_run() 
        assert gg3.current_edge_degree == 66 

        # case 4
        ##print("44")
        edge_connectivity = 0.25 
        gg4 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg4.d) == 12 
        gg4.full_run() 
        assert gg4.current_edge_degree == 33  

        # case 5 
        ##print("55")
        is_dsg = 0 
        gg5 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg5.d) == 12 
        gg5.full_run() 
        assert gg5.current_edge_degree == 17  

        # case: isotransform 
        ##print("66")
        gg5.isotransform(25)
        D2 = gg5.d 

        ans = defaultdict(set,{25: {27}, 26: {35, 27}, \
            27: {32, 33, 34, 35, 36, 25, 26, 28, 29, 30, 31}, \
            28: {27, 35}, 29: {35, 27}, 30: {27}, 31: {27, 35}, \
            32: {27}, 33: {35, 27}, 34: {27, 35}, \
            35: {33, 34, 26, 27, 28, 29, 31}, 36: {27}}) 
        assert D2 == ans 

    """
    test if produced graph is directed or not. 
    """
    def test__GraphGen__full_run__case_2(self): 
        lx = prg__LCG(551,3,19,2132) 

        vertex_degrees = [12,24,50,32,75] 
        for i in range(5): 
            is_dsg = i % 2 
            is_realtime_gen = bool(not i % 2) 
            vertex_degree = vertex_degrees[i] 
            edge_connectivity = 0.5 
            gg = GraphGen(is_dsg,lx,is_realtime_gen,vertex_degree,edge_connectivity)
            gg.full_run() 
            assert len(gg.d) == vertex_degree 
            stat = is_undirected_graph(gg.d) 
            assert stat == (not is_dsg )

    def test__GraphGen__full_run__case_3(self): 

        lx = prg__LCG(55,3,19,212) 

        is_dsg = 0  
        prg = lx 
        is_realtime_gen = True 
        vertex_degree = 20 
        edge_connectivity = 0.33 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        gg.full_run() 
        D = gg.d 

        assert gg.current_edge_degree == ceil(edge_connectivity * max_simple_edges(20)) 

    def test__GraphGen__full_run__case_4(self): 
        is_dsg = False 
        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
        is_realtime_gen = True 
        vertex_degree = 30 
        edge_connectivity = 0.1#0.175 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity) 
        gg.full_run() 
        assert abs(gg.edge_connectivity_() - 0.1) < 2 * 10 ** -2 
        assert len(gg.d) == vertex_degree

class GraphWeightGenClass(unittest.TestCase):

    def test__GraphWeightGen__generate__case_1(self): 

        prg = prg__LCG(67.4,-100,89.6,9196.66)
        is_realtime_gen = True 
        vertex_degree = 35 
        edge_connectivity = 0.2  
        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
                vertex_degree=vertex_degree,edge_connectivity=edge_connectivity,\
                verbose=False)
        gg.full_run() 

        gw = GraphWeightGen(gg.d,prg,is_dsg=True,weight_range=[-10.,10.]) 
        niw,nb = nonequal_edge_weight_counts(gg.d,gw.weight) 
        assert niw == nb == 238 

        gw2 = GraphWeightGen(gg.d,prg,is_dsg=False,weight_range=[-10.,10.]) 
        niw2,nb2 = nonequal_edge_weight_counts(gg.d,gw2.weight) 
        assert niw2 == 0 == nb2 - 238 

class OtherGraphGeneratorFunctionsClass(unittest.TestCase): 

    def test__generate_graph__X__case_1(self): 

        P = generate_graph__path(5,starting_node_idn=3,is_dsg=False)
        P1 = generate_graph__path(7,starting_node_idn=4,is_dsg=True) 
        P2 = generate_graph__path(1,starting_node_idn=5,is_dsg=False) 
        G_c = generate_graph__complete(4,starting_node_idn=4)

        assert P == defaultdict(set, {3: {4}, 4: {3, 5}, 5: {4, 6}, 6: {5, 7}, 7: {6}})
        assert P1 == defaultdict(set, {4: {5}, 5: {6}, 6: {7}, 7: {8}, 8: {9}, 9: {10}})
        assert P2 == defaultdict(set, {5: set()})
        assert G_c == defaultdict(set, {4: {5, 6, 7}, 5: {4, 6, 7}, 6: {4, 5, 7}, 7: {4, 5, 6}})

if __name__ == '__main__':
    unittest.main()