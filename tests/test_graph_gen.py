from quant.graph_gen import * 
from quant.cng import * 
import unittest

### lone file test 
"""
python -m tests.test_graph_gen 
"""
###
class GraphGenClass(unittest.TestCase):

    def test__GraphGen__full_run__case_1(self):
        lx = prg__LCG(55,3,19,212) 
        lx2 = prg__LCG(31,78,2,2120) 
        lx3 = prg__LCG(0,0,0,2) 

        # case 1 
        is_dsg = 0  
        prg = lx 
        is_realtime_gen = True 
        vertex_degree = 12 
        edge_connectivity = 0.5 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg.d) == 0 
        gg.full_run() 
        assert gg.current_edge_degree == 33 
        assert gg.max_simple_edges(12) == 66 

        # case 2 
        is_dsg = 1 
        prg = lx3 
        gg2 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg2.d) == 0 
        gg2.full_run() 
        assert gg2.current_edge_degree == 66 

        # case 3
        prg = lx2 
        is_realtime_gen = False 
        gg3 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg3.d) == 12 
        gg3.full_run() 
        assert gg3.current_edge_degree == 66 

        # case 4
        edge_connectivity = 0.25 
        gg4 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg4.d) == 12 
        gg4.full_run() 
        assert gg4.current_edge_degree == 33  

        # case 5 
        is_dsg = 0 
        gg5 = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
        assert len(gg5.d) == 12 
        gg5.full_run() 
        assert gg5.current_edge_degree == 17  

if __name__ == '__main__':
    unittest.main()