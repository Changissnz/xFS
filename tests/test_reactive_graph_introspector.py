from graph_models.graph_gen import * 
from quant.reactive_graph_introspector import * 
from morebs2.numerical_generator import prg__LCG 
import unittest

def ReactiveGraphIntrospectorTypeCNO__sample_RSAP(prg): 

    is_dsg = False ## 

    G = GraphGen(is_dsg=is_dsg,prg=prg,is_realtime_gen=False,\
        vertex_degree=50,edge_connectivity=0.2,verbose=False)
    G.full_run() 

    G = graph_to_one_component(G.d,prg) 
    nodechange_range = [-3,3]
    edgechange_range = [-4,4] 
    period_range = [2,6] 
    maintain_connectivity = True     
    is_rule_constant = False 
    node_weight_range = None #[0.5,6]
    edge_weight_range = [0.5,6] 
    is_bfs = True 
    ascending_priority = True 
    cycle_length_range = [2,9] 

    return ReactiveGraphIntrospectorTypeCNO.generate_instance(\
        G,nodechange_range,edgechange_range,period_range,maintain_connectivity,\
        is_rule_constant,node_weight_range,is_dsg,is_bfs,\
        ascending_priority,cycle_length_range,prg,verbose=False)


### lone file test 
"""
py -m tests.test_reactive_graph_introspector
"""
###
class ReactiveGraphIntrospectorTypeCNOClass(unittest.TestCase):

    def test__ReactiveGraphIntrospectorTypeCNO__next__case1(self):  
        prg = prg__LCG(55.4,-166.5,94.34,404.555) 
        S = ReactiveGraphIntrospectorTypeCNO__sample_RSAP(prg) 
        G2 = deepcopy(S.G)  
 
        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat and c < 1000: 
            next(S) 
            c += 1 

        assert c == 119,"got {}".format(c) 
        X = S.output_minpaths(2) 
        y = sum([len(v) for v in X.values()]) 
        assert y == 97,"got {}".format(y) 

        q = MicroGraph(S.G)
        q2 = MicroGraph(G2) 

        d0 = q.sub_ve_score(q2)
        d1 = q2.sub_ve_score(q) 

        assert d0 == (5, 40) 
        assert d1 == (15, 376)

    def test__ReactiveGraphIntrospectorTypeCNO__next__case2(self): 
        prg = prg__LCG(-1155.4,166.5,-94.34,-25404.555) 
        S = ReactiveGraphIntrospectorTypeCNO__sample_RSAP(prg) 
        G2 = deepcopy(S.G)  
 
        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat and c < 1000: 
            next(S) 
            c += 1 

        q = MicroGraph(S.G)
        q2 = MicroGraph(G2) 

        d0 = q.sub_ve_score(q2)
        d1 = q2.sub_ve_score(q) 

        assert d0 == (12, 65) 
        assert d1 == (14, 396)


if __name__ == '__main__':
    unittest.main()        