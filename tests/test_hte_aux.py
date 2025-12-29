from quant.hte_aux import * 
from morebs2.numerical_generator import * 
import unittest 

def graph__sample_HTE1(): 
    is_dsg = False 
    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
    is_realtime_gen = True 
    vertex_degree = 30 
    edge_connectivity = 0.1#0.175 
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity) 
    gg.full_run() 

    D = graph_to_one_component(deepcopy(gg.d),prg)
    assert D != gg.d 
    return D,prg 

### lone file test 
"""
py -m tests.test_hte_aux
"""
###
class HTESurfaceClass(unittest.TestCase):

    def test__HTESurface__generate__case_1(self): 
        D,prg = graph__sample_HTE1()

        num_entry_points = 3 
        num_objective_points = 4 
        threat_ratio = 0.5 
        threat_mobility_ratio = 0.25 
        threat_nodes_include_entry_points = False 

        htes = HTESurface.generate_instance(D,num_entry_points,num_objective_points,\
            threat_ratio,threat_mobility_ratio,threat_nodes_include_entry_points,\
            prg) 

        assert len(htes.entry_points) == num_entry_points
        assert len(htes.objective_points) == num_objective_points
        assert len(htes.threat_map) == ceil((30 - 7) / 2)
        assert htes.entry_points.intersection(set(htes.threat_map.keys())) == set() 

    def test__HTESurface__generate__case_2(self): 
        D,prg = graph__sample_HTE1()

        num_entry_points = 13 
        num_objective_points = 7 
        threat_ratio = 0.5
        threat_mobility_ratio = 0.25 
        threat_nodes_include_entry_points = True 

        htes = HTESurface.generate_instance(D,num_entry_points,num_objective_points,\
            threat_ratio,threat_mobility_ratio,threat_nodes_include_entry_points,\
            prg)

        assert len(htes.entry_points) == num_entry_points
        assert len(htes.objective_points) == num_objective_points
        assert len(htes.threat_map) == ceil((30-7) / 2)

        entry_obj_points = htes.entry_points.intersection(set(htes.threat_map))
        assert entry_obj_points == {6, 13, 18, 21, 23, 24, 26, 27}

        contra_threats = htes.threat_node_identifiers({"contra"})
        threats = htes.threat_node_identifiers({"contra","constant"})
        assert len(threats) * threat_mobility_ratio == len(contra_threats)

if __name__ == '__main__':
    unittest.main()