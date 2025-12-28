from graph_models.analog_schemes import * 
from morebs2.graph_basics import * 
from morebs2.numerical_generator import * 
import unittest 

"""
graph with 2 separate components
"""
def graph__sample_2COMP(): 

    D = defaultdict(set,\
        {0:{1,2,3},\
        1:{0,4},\
        2:{0,5},\
        3:{0,6},\
        4:{1,7},\
        5:{2},\
        6:{3},\
        7:{4}}) 

    lx = prg__LCG(55,3,19,212) 
    is_dsg = 0  
    prg = lx 
    is_realtime_gen = True 
    vertex_degree = 8 
    edge_connectivity = 0.22 
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity)
    gg.full_run() 
    D2 = gg.d 

    cx = SimpleCounter(len(D2)) 
    def ctr_function(): return next(cx) 

    keys2 = sorted(D2.keys())
    isomap = {k:ctr_function() for k in keys2} 
    D2 = MicroGraph.isotransform_MG(MicroGraph(D2),isomap).dg

    return (MicroGraph(D) + MicroGraph(D2)).dg,prg 

"""
py -m tests.test_analog_schemes
"""
class GraphAnalogAdderClass(unittest.TestCase):

    """
    demonstrates that component caching mechanism works, so that 
    component-to-component disconnection is maintained through 
    iteration of extending with subgraphs, each generated through any 
    one of the three generative schemes. 
    """
    def test__GraphAnalogAdder_extend__case1(self):
        DX,_ = graph__sample_2COMP() 
        lx = prg__LCG(551,-13,199,2341) 
 
        gaa = GraphAnalogAdder(DX,is_dsg=False,prg=lx)

        assert len(gaa.nodeset_cache) == 2
        assert len(gaa.new_nodesets) == 0 

        gaa.extend() 
        assert len(gaa.nodeset_cache) == 1
        assert len(gaa.new_nodesets) == 1 

        gaa.extend() 
        assert len(gaa.nodeset_cache) == 0
        assert len(gaa.new_nodesets) == 2 

        gaa.extend()
        assert len(gaa.nodeset_cache) == 1
        assert len(gaa.new_nodesets) == 1 

        # checks that component disconnection is maintained 
        gaa2 = GraphAnalogAdder(gaa.d,is_dsg=False,prg=lx) 
        assert len(gaa2.nodeset_cache) == 2

        # check that graph increases in size 
        v0,e0 = MicroGraph(gaa.d).ve_score()
        assert v0 == 34 and e0 == 98 
        assert is_undirected_graph(gaa.d)

        # check for diversity of generator scheme use 
        assert gaa.gen_scheme_log == [3, 2, 2] 
        gaa.extend()
        assert gaa.gen_scheme_log == [3, 2, 2,1] 

    """
    inconclusive test; does not check if subgraphs [2]+[3] are actually trees. 
    """
    def test__GraphAnalogAdder_extend__case2(self): 
        DX,_ = graph__sample_2COMP() 
        lx = prg__LCG(55,3,19,212) 
        gaa = GraphAnalogAdder(DX,is_dsg=False,prg=lx,gen_scheme_zero_types={"tree"},store_isomaps=True)

        for _ in range(5): 
            gaa.extend() 

        assert gaa.gen_scheme_log == [2, 2, 1, 1, 2], "got {}".format(gaa.gen_scheme_log)
        assert len(gaa.subgraph_nodeset_log) == 7
        return 

    """
    tests for disconnected subgraphs 
    """
    def test__GraphAnalogAdder__extend__case3(self): 
        
        DX,lx = graph__sample_2COMP() 
        gaa = GraphAnalogAdder(DX,is_dsg=False,prg=lx,gen_scheme_zero_types={"tree","random"},connect_components=False,store_isomaps=True)
        for _ in range(5): 
            gaa.extend() 

        gxx = GraphComponentDecomposition(gaa.d)
        gxx.decompose() 
        assert len(gxx.components) == 7 

    """
    tests for correct number of isomaps and correct number of 
    subgraph nodesets from prng reproduction. 
    """
    def test__GraphAnalogAdder__prng_reproduction(self): 
        DX,lx = graph__sample_2COMP() 

        gaa = GraphAnalogAdder(DX,is_dsg=False,prg=lx,\
            gen_subgraph_shortest_paths_parameters=[10,3],\
            gen_scheme_zero_types={"tree","random"},connect_components=False,every_subgraph_is_connected=True,\
            store_isomaps=True)

        for _ in range(7):   
            gaa.extend() 

        gaa2,_ = gaa.prng_reproduction()

        assert len(gaa2.isomap_log) == len(gaa2.subgraph_nodeset_log) / 2 

if __name__ == '__main__':
    unittest.main()