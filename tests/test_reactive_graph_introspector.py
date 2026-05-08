from graph_models.graph_gen import * 
from quant.reactive_graph_introspector import * 
from morebs2.numerical_generator import prg__LCG 
import unittest

### lone file test 
"""
py -m tests.test_reactive_graph_introspector
"""
###
class ReactiveGraphIntrospectorTypeCNOClass(unittest.TestCase):

    def test__ReactiveGraphIntrospectorTypeCNO__next__case1(self):  
        prg = prg__LCG(55.4,-166.5,94.34,404.555) 

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

        S = ReactiveGraphIntrospectorTypeCNO.generate_instance(\
            G,nodechange_range,edgechange_range,period_range,maintain_connectivity,\
            is_rule_constant,node_weight_range,is_dsg,is_bfs,\
            ascending_priority,cycle_length_range,prg,verbose=False)

        S.set_ref_node(7) 

        c = 0 
        while not S.introspector.fin_stat and c < 1000: 
            next(S) 
            c += 1 

        assert c == 272 
        X = S.output_minpaths(2) 
        assert sum([len(v) for v in X.values()]) == 144


if __name__ == '__main__':
    unittest.main()        