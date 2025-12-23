from graph_models.analog_schemes import * 
from morebs2.graph_basics import * 
from morebs2.numerical_generator import * 
import unittest 

def graph__sample_ASCHEME(): 

    return defaultdict(set,\
        {0:{1,2,3},\
        1:{0},\
        2:{0,6,9,11},\
        3:{0,4},\
        4:{3,5,9},\
        5:{4,6,11,15},\
        6:{2,5,7,8,15},\
        7:{6,10,14},\
        8:{6,10,12},\
        9:{2,4,11},\
        10:{7,8,13},\
        11:{2,5,9,12},\
        12:{8,11},\
        13:{10},\
        14:{7,15},\
        15:{5,6,14}}) 

class SimpleCounter: 

    def __init__(self,x): 
        self.x = x 
    
    def __next__(self):
        x2 = self.x 
        self.x += 1 
        return x2 

def prng__sample_ASCHEME(): 
    lx = prg__LCG(55,3,19,2120) 
    lx_ = prg__LCG(-4.2,-55.6,67.87,-987.65) 

    def lx2(): 
        return lx() + lx_() 
    return lx2 

"""
py -m tests.test_analog_schemes_aux
"""
class AnalogSchemeAuxFile(unittest.TestCase):

    def test__shortest_paths_graph_analogue__case_1(self): 
        D = graph__sample_ASCHEME()

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        lx2 = prng__sample_ASCHEME() 

        # subcase 1 
        D2,isomap = shortest_paths_graph_analogue(D,0,False,10,1,lx2,ctr_function) 
        isomap2 = {v:k for k,v in isomap.items()} 

        count = check_for_shortest_paths_of_isomorphic_subgraph(D,D2,isomap,\
            num_paths_per_node=10,prg=lx2) 
        assert count == 5

        mg = MicroGraph(D2) 
        mg3 = MicroGraph.isotransform_MG(mg,isomap2)

        mg_ = MicroGraph(D) 

        stat = mg_.is_supergraph_of(mg3) 
        stat2 = mg_.is_subgraph_of(mg3) 
        assert stat and not stat2 

        v0,e0 = mg_.ve_score() 
        v1,e1 = mg3.ve_score() 

        assert e0 == 46 
        assert e1 == 12

    def test__shortest_paths_graph_analogue__case_2(self): 
        D = graph__sample_ASCHEME()
         
        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        lx2 = prng__sample_ASCHEME() 

        D2,isomap = shortest_paths_graph_analogue(D,0,False,10,12,lx2,ctr_function) 
        isomap2 = {v:k for k,v in isomap.items()} 

        count = check_for_shortest_paths_of_isomorphic_subgraph(D,D2,isomap,\
            num_paths_per_node=10,prg=lx2) 
        assert count == 15

        mg = MicroGraph(D2) 
        mg3 = MicroGraph.isotransform_MG(mg,isomap2)

        mg_ = MicroGraph(D) 

        stat = mg_.is_supergraph_of(mg3) 
        stat2 = mg_.is_subgraph_of(mg3) 
        assert stat and not stat2 

        v0,e0 = mg_.ve_score() 
        v1,e1 = mg3.ve_score() 

        assert e0 == 46 
        assert e1 == 36  

    def test__shortest_paths_graph_analogue__case_3(self): 
        D = graph__sample_ASCHEME()
         
        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        lx2 = prng__sample_ASCHEME()

        D2,isomap = shortest_paths_graph_analogue(D,0,False,10,7,lx2,ctr_function) 
        isomap2 = {v:k for k,v in isomap.items()} 

        count = check_for_shortest_paths_of_isomorphic_subgraph(D,D2,isomap,\
            num_paths_per_node=10,prg=lx2) 
        assert count == 12

        mg = MicroGraph(D2) 
        mg3 = MicroGraph.isotransform_MG(mg,isomap2)

        mg_ = MicroGraph(D) 

        stat = mg_.is_supergraph_of(mg3) 
        stat2 = mg_.is_subgraph_of(mg3) 

        v0,e0 = mg_.ve_score() 
        v1,e1 = mg3.ve_score() 

        assert e0 == 46 
        assert e1 == 28  

if __name__ == '__main__':
    unittest.main()