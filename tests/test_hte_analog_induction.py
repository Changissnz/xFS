from graph_models.graph_gen import * 
from quant.hte_analog_induction import * 

import time 
import unittest 

def base_graph_sample_I(): 
    is_dsg = False 
    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
    is_realtime_gen = True 
    vertex_degree = 25 
    edge_connectivity = 0.15#0.175 
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity,verbose=False) 
    gg.full_run() 
    G = graph_to_one_component(deepcopy(gg.d),prg)
    return G 

### lone file test 
"""
py -m tests.test_hte_analog_induction
"""
###
class HTEAnalogInducerClass(unittest.TestCase):

    def test__HTEAnalogInducer__generate__case_1(self): 
        G = base_graph_sample_I() 
        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
        qsf = QuickSubgraphFetcher(G,prg)
        sg = qsf.subgraph(5,2)

        ctr_function = SimpleCounter(max(G.keys()) + 1).__next__
        sg,iso = graph_automorphism(sg,ctr_function)

        threat_nodes = [1,17,7,9] 
        threat_iso_map = {t:iso[t] for t in threat_nodes}

        hai = HTEAnalogInducer.generate_instance(G,sg,threat_iso_map,\
                isomorphic_subgraph_radius_range=[1,2],\
                hyp_node_distance_range=[1,2],prg=prg)
        assert hai.next_graph_hyp_map == {1: (27, 1), 17: (40, 1), 7: (36, 1), 9: (28, 1)},"got {}".format(\
            hai.next_graph_hyp_map)

        stat_map = {1:False,17:True,7:False,9:False}
        stat2 = {} 
        for t in threat_nodes:
            #print("T: ",t)
            possible = hai.possible_threat_analogs(t)

            stat2_ = threat_iso_map[t] in possible
            stat2[t] = stat2_ 
        assert stat_map == stat2,"got {}".format(stat2) 

    def test__HTEAnalogInducer__generate__case_2(self): 
        G = base_graph_sample_I() 
        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
        qsf = QuickSubgraphFetcher(G,prg)
        sg = qsf.subgraph(10,2)

        ctr_function = SimpleCounter(max(G.keys()) + 1).__next__
        sg,iso = graph_automorphism(sg,ctr_function)

        threat_nodes = [6,11,16] 
        threat_iso_map = {t:iso[t] for t in threat_nodes}

        hai = HTEAnalogInducer.generate_instance(G,sg,threat_iso_map,\
                isomorphic_subgraph_radius_range=[1,2],\
                hyp_node_distance_range=[1,3],prg=prg)
        #assert hai.next_graph_hyp_map == {1: (27, 1), 17: (40, 1), 7: (36, 1), 9: (28, 1)}

        stat_map = {6: True, 11: False, 16: True}
        stat2 = {} 
        for t in threat_nodes:
            #print("T: ",t)
            possible = hai.possible_threat_analogs(t)

            stat2_ = threat_iso_map[t] in possible
            stat2[t] = stat2_ 
        assert stat_map == stat2 

    def test__HTEAnalogInducer__generate__case_3(self): 
        G = base_graph_sample_I() 
        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
        qsf = QuickSubgraphFetcher(G,prg)
        sg = qsf.subgraph(5,3)

        ctr_function = SimpleCounter(max(G.keys()) + 1).__next__
        sg,iso = graph_automorphism(sg,ctr_function)

        threat_nodes = [1,17,7,9] 
        threat_iso_map = {t:iso[t] for t in threat_nodes}

        hai = HTEAnalogInducer.generate_instance(G,sg,threat_iso_map,\
                isomorphic_subgraph_radius_range=[1,2],\
                hyp_node_distance_range=[2,3],prg=prg)

        stat_map = {1: True, 17: False, 7: False, 9: True}
        stat2 = {} 
        for t in threat_nodes:
            possible = hai.possible_threat_analogs(t)

            stat2_ = threat_iso_map[t] in possible
            stat2[t] = stat2_ 
        assert stat_map == stat2,"got {}".format(stat2) 

if __name__ == '__main__':
    unittest.main()
