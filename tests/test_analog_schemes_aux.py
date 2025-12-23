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

def graph__sample_ASCHEME2(): 
    return defaultdict(set,\
        {0:{1,2,3},\
        1:{},\
        2:{6,9,11},\
        3:{0},\
        4:{3,5,9},\
        5:{4,6,11,15},\
        6:{2,5,8,15},\
        7:{6,10,14},\
        8:{6,12},\
        9:{2,4,11},\
        10:{7,8,13},\
        11:{2,9,12},\
        12:{8,11},\
        13:{10},\
        14:{7},\
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

    def test__one_edge_change__case_1(self):

        D = graph__sample_ASCHEME()
        prg = prg__LCG(45,677,-5462,3112) 

        # subcase 1 
        D2 = deepcopy(D)
        one_edge_change(D,is_dsg=False,add_edge=True,prg=prg) 

        m2 = MicroGraph(D2) 
        m1 = MicroGraph(D)  

        v1,e1 = m1.ve_score() 
        v2,e2 = m2.ve_score() 

        assert e2 == 46 == e1 - 2

        # subcase 2 
        D3 = deepcopy(D2) 
        one_edge_change(D2,is_dsg=False,add_edge=False,prg=prg) 

        m3 = MicroGraph(D2) 
        v3,e3 = m3.ve_score() 

        assert e3 == e2 - 2 == 44 
        prev = 44
        for i in range(10): 
            one_edge_change(D2,is_dsg=False,add_edge=False,prg=prg) 
            v3,e3 = m3.ve_score() 
            assert e3 == prev - 2 
            prev -= 2 

    def test__one_edge_change__case_2(self): 

        D = graph__sample_ASCHEME2()
        prg = prg__LCG(45,677,-5462,3112) 

        # subcase 1 
        D2 = deepcopy(D)
        one_edge_change(D,is_dsg=True,add_edge=True,prg=prg) 

        m2 = MicroGraph(D2) 
        m1 = MicroGraph(D)  

        v1,e1 = m1.ve_score() 
        v2,e2 = m2.ve_score() 

        assert e1 == 40 == e2 + 1, "got {}".format(e1)  
        prev = e1  

        for i in range(10): 
            one_edge_change(D,is_dsg=True,add_edge=False,prg=prg) 
            v3,e3 = m1.ve_score() 
            assert e3 == prev - 1 
            prev -= 1 

        for i in range(5): 
            one_edge_change(D,is_dsg=True,add_edge=True,prg=prg) 
            v3,e3 = m1.ve_score() 
            assert e3 == prev + 1 
            prev += 1 

    # case: undirected graph, 0 new nodes, 0.2 change in edges  
    def test__graph_derivation__case_1(self): 
        prg = prg__LCG(4543,6771,-115462,31167) 
        D = graph__sample_ASCHEME()
        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=False,node_change_ratio=0.0,edge_change_ratio=0.2,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        assert mg3.is_supergraph_of(mg1) and not mg1.is_supergraph_of(mg3) 

        _,e1 = mg1.ve_score()
        _,e3 = mg3.ve_score()

        rem_edges = max_simple_edges(16) / 2 - e1 / 2
        additional = ceil(rem_edges * 0.2) * 2 

        assert e1 + additional == e3 
        return

    # case: undirected graph, 0 new nodes, -0.2 change in edges  
    def test__graph_derivation__case_2(self): 
        prg = prg__LCG(4543,6771,-115462,31167) 
        D = graph__sample_ASCHEME()

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=False,node_change_ratio=0.0,edge_change_ratio=-0.2,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        assert mg3.is_subgraph_of(mg1) and not mg1.is_subgraph_of(mg3) 

        _,e1 = mg1.ve_score()
        _,e3 = mg3.ve_score()

        assert e1 - ceil(e1 * 0.2) == e3 
        return

    # case: directed graph, 0 new nodes, -0.2 change in edges  
    def test__graph_derivation__case_3(self): 

        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=0.0,edge_change_ratio=-0.2,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        _,e1 = mg1.ve_score()
        _,e3 = mg3.ve_score()

        assert e1 == 39 
        assert e3 == 39 - ceil(e1 * 0.2)

    # case: directed graph, 0 new nodes, 0.2 change in edges  
    def test__graph_derivation__case_4(self): 

        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=0.0,edge_change_ratio=0.2,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        _,e1 = mg1.ve_score()
        _,e3 = mg3.ve_score()

        assert e1 == 39 
        assert e3 == 39 + ceil(81 * 0.2)

    # case: directed graph, 0.2 new nodes, 0.2 change in edges  
    def test__graph_derivation__case_5(self): 

        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=0.2,edge_change_ratio=0.0,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        v1,e1 = mg1.ve_score()
        v2,e2 = mg3.ve_score()

        assert ceil(v1 + v1 * 0.2) == v2 
        assert e2 - (v2-v1) == e1 

    # case: directed graph, -0.2 new nodes, 0.0 change in edges  
    def test__graph_derivation__case_6(self): 

        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=-0.2,edge_change_ratio=0.0,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        v1,e1 = mg1.ve_score()
        v2,e2 = mg3.ve_score()

        assert v1 - ceil(v1 * 0.2) == v2, "got {}->{}".format(v1,v2) 

    # case: directed graph, -0.2 new nodes, 0.5 change in edges  
    def test__graph_derivation__case_7(self): 
        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=-0.2,edge_change_ratio=0.5,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        #assert mg3.is_supergraph_of(mg1) and not mg1.is_supergraph_of(mg3) 

        v1,e1 = mg1.ve_score()
        v3,e3 = mg3.ve_score()

        assert v1 == 16 and v3 == 12

        assert e1 == 39 and e3 == 43 

    # case: directed graph, 0.5 new nodes, -0.2 change in edges  
    def test__graph_derivation__case_8(self): 
        D = graph__sample_ASCHEME2()

        prg = prg__LCG(4543,6771,-115462,31167) 

        sc = SimpleCounter(len(D))
        def ctr_function(): return next(sc) 

        mg1 = MicroGraph(deepcopy(D))
        D2 = graph_derivation(D,is_dsg=True,node_change_ratio=0.5,edge_change_ratio=-0.2,prg=prg,\
            ctr_function=ctr_function)
        mg2 = MicroGraph(D2[0]) 
        isomap = {v:k for k,v in D2[1].items()}
        mg3 = MicroGraph.isotransform_MG(mg2,isomap) 

        #assert mg3.is_supergraph_of(mg1) and not mg1.is_supergraph_of(mg3) 

        v1,e1 = mg1.ve_score()
        v3,e3 = mg3.ve_score()

        assert v1 == 16 and v3 == 24
        assert e1 == 39 and e3 == 37 

    def test__connect_subgraphs__prior_to_current(self): 
        D = graph__sample_ASCHEME() 
        D2 = defaultdict(set,{16:set(),17:set(),18:set(),19:set()})
        sg2sg_conn_ratios = [0.5,0.5] 
        prg = prg__LCG(4543,6771,-115462,31167) 

        new_sg = connect_subgraphs__prior_to_current(D,D2,\
            is_dsg=False,sg2sg_conn_ratios=sg2sg_conn_ratios,prg=prg)
        new_edge_count = sum([len(new_sg[i]) for i in range(16,20)])
        assert new_edge_count == 15 

        new_sg2 = connect_subgraphs__prior_to_current(D,D2,\
            is_dsg=False,sg2sg_conn_ratios=sg2sg_conn_ratios,prg=prg)
        new_edge_count2 = sum([len(new_sg2[i]) for i in range(16,20)])
        assert new_edge_count2 == 24 

        new_sg3 = connect_subgraphs__prior_to_current(D,D2,\
            is_dsg=False,sg2sg_conn_ratios=sg2sg_conn_ratios,prg=prg)
        new_edge_count3 = sum([len(new_sg3[i]) for i in range(16,20)])
        assert new_edge_count3 == 8 

        new_sg4 = connect_subgraphs__prior_to_current(D,D2,\
            is_dsg=False,sg2sg_conn_ratios=sg2sg_conn_ratios,prg=prg)
        new_edge_count4 = sum([len(new_sg4[i]) for i in range(16,20)])
        assert new_edge_count4 == 22 

if __name__ == '__main__':
    unittest.main()