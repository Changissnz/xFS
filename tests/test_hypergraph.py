from graph_models.hypergraph import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence
import unittest

### lone file test 
"""
py -m tests.test_hypergraph
"""
###
class HyperGraphClass(unittest.TestCase):

    """
    correctness test 
    """
    def test__HyperGraph__generate_instance__case_1(self): 
        hg_nodesize = 10 
        hg_connectivity = 0.3 
        is_directed = False 
        base_nodesize = 30 
        node2nodeset_sizerange = [4,6]  
        prg = prg__LCG(43,-5444.6,19.55,4520.77) 

        hg = HyperGraph.generate_instance(hg_nodesize,hg_connectivity,is_directed,base_nodesize,node2nodeset_sizerange,prg)
        q = hg.base_nodeset()

        assert is_valid_hypergraph(hg.rep,hg.node2nodeset) 

    """
    correctness test 
    """
    def test__HyperGraph__generate_instance__case_2(self): 
        hg_nodesize = 12 
        hg_connectivity = 0.25 
        is_directed = False 
        base_nodesize = 15 
        node2nodeset_sizerange = [3,5]  
        prg = prg__LCG(321,-444.6,2219.55,11520.77) 

        hg = HyperGraph.generate_instance(hg_nodesize,hg_connectivity,is_directed,base_nodesize,node2nodeset_sizerange,prg)
        q = hg.base_nodeset()

        assert is_valid_hypergraph(hg.rep,hg.node2nodeset) 

    """
    correctness test 
    """
    def test__HyperGraph__generate_instance__case_3(self): 
        hg_nodesize = 25 
        hg_connectivity = 0.3 
        is_directed = False 
        base_nodesize = 35 
        node2nodeset_sizerange = [5,9]  
        prg = prg__LCG(35.7,-1544.6,3319.55,9520.77) 

        hg = HyperGraph.generate_instance(hg_nodesize,hg_connectivity,is_directed,base_nodesize,node2nodeset_sizerange,prg)
        q = hg.base_nodeset()

        assert is_valid_hypergraph(hg.rep,hg.node2nodeset) 

    """
    correctness test 
    """
    def test__HyperGraph__generate_instance__case_4(self): 
        hg_nodesize = 20 
        hg_connectivity = 0.3 
        is_directed = False 
        base_nodesize = 20 
        node2nodeset_sizerange = [4,6]  
        prg = prg__LCG(1143,-9444.6,1669.55,36520.77) 

        hg = HyperGraph.generate_instance(hg_nodesize,hg_connectivity,is_directed,base_nodesize,node2nodeset_sizerange,prg)
        q = hg.base_nodeset()

        assert is_valid_hypergraph(hg.rep,hg.node2nodeset) 

    def test__HyperGraph__generate_instance__case_5(self): 

        hg_nodesize = 10 
        hg_connectivity = 0.3 
        is_directed = False 
        base_nodesize = 30 
        node2nodeset_sizerange = [2,6]  
        prg = prg__LCG(43,-5444.6,19.55,4520.77) 
        prg_seq = prg_to_prg__LCG_sequence(prg,20,4.5+4/3)

        for prg in prg_seq: 
            hg = HyperGraph.generate_instance(hg_nodesize,hg_connectivity,is_directed,base_nodesize,node2nodeset_sizerange,prg)
            q = hg.base_nodeset()

            D = hg.H_node_density_map()
            V = set(D.values()) 
            assert 2 <= min(V) <= max(V) <= 10 
            ##print("density")
            ##print(D)

if __name__ == '__main__':
    unittest.main()