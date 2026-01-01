from quant.hte_aux import * 
from morebs2.numerical_generator import * 
import time 
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

        entry_obj_inter = htes.entry_points.intersection(set(htes.threat_map))
        assert entry_obj_inter ==  {5, 7, 9, 21, 27}, "got {}".format(entry_obj_inter)

        contra_threats = htes.threat_node_identifiers({"contra"})
        threats = htes.threat_node_identifiers({"contra","constant"})
        assert len(threats) * threat_mobility_ratio == len(contra_threats)

    """
    tests for timeliness of generating instance of connected graph of 250 nodes
    """
    def test__HTESurface__generate__case_3(self): 
        D = base_graph_sample_FU()
        num_entry_points = 30  
        num_objective_points = 23  
        threat_ratio = 0.5
        threat_mobility_ratio = 0.25 
        threat_nodes_include_entry_points = True 

        prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 

        print("GENERATING")
        t = time.time() 
        htes = HTESurface.generate_instance(D,num_entry_points,num_objective_points,\
            threat_ratio,threat_mobility_ratio,threat_nodes_include_entry_points,\
            prg)

        for _ in range(5): 
            q = time.time() 
            htes2 = htes.prng_reproduction(gen_subgraph_shortest_paths_parameters=[10,15])
            print("\n\t\treproduced")
            print(htes2)
            print() 
            print("reprod time: ",time.time() - q) 
            print("-" * 75)
        print("\n\t\tORIGINAL")
        print(htes) 
        print() 

        print("total runtime: ",time.time() - t) 

if __name__ == '__main__':
    unittest.main()