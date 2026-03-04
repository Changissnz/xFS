from graph_models.lattice_graph import * 
import unittest

### lone file test 
"""
py -m tests.test_lattice_graph
"""
###
class VCLatticeGraphGenClass(unittest.TestCase):
    
    """
    checks for intersection between two parallel surfaces
    """
    def test__VCLatticeGraphGen__make__case_1(self):
        # make two instances of the same parameters 
        shape = (4,4)
        prg = prg__LCG(45.55,78.32,-414.99,500.12) 
        parallel_length_range = (4,5) 
        connection_density = 1.0

        q = VCLatticeGraphGen(shape,prg,parallel_length_range,connection_density,\
                is_dsg=False)
        q.make() 

        prg1 = prg__LCG(37.55,178.32,-4141.99,1501.12) 

        q2 = VCLatticeGraphGen(shape,prg1,parallel_length_range,connection_density,\
                is_dsg=False)
        q2.make() 
        #-----------------------------

        nodeset_dict = q.surface_to_nodeset_map(False) 
        nodeheads_dict = q.surface_to_node_heads_map()

        nodeset0 = nodeset_dict[0] 
        nodeset1 = nodeset_dict[1] 

        G0 = {k:q.G[k] for k in nodeset0} 
        base_nodeset = set(G0.keys()) 
        entire_nodeset = flatten_setseq([v for v in G0.values()]) | base_nodeset 
        diff_nodeset_ = entire_nodeset - base_nodeset 

        #-------------------------------

        nodeset_dict2 = q2.surface_to_nodeset_map(False) 
        nodeheads_dict2 = q2.surface_to_node_heads_map()

        nodeset0_ = nodeset_dict2[0] 
        nodeset1_ = nodeset_dict2[1] 

        G1 = {k:q2.G[k] for k in nodeset0_} 
        base_nodeset_ = set(G1.keys()) 
        entire_nodeset_ = flatten_setseq([v for v in G1.values()]) | base_nodeset_ 
        diff_nodeset = entire_nodeset_ - base_nodeset 
        assert diff_nodeset != diff_nodeset_

        surface = q.surfaces[1] 
        parallels = set() 
        for d in diff_nodeset: 
            i = surface.node_to_parallel_index(d) 
            parallels |= {i}  

        assert parallels == {0,1,2,3} 

        x = q2.surface_parallels_to_interception_map()
        diff_nodeset_check = set() 

        # parallel index -> other surface 
        for v in x[0].values():
            for k2,v2 in v.items(): 
                for v3 in v2.values(): 
                    diff_nodeset_check |= v3 
        assert diff_nodeset_check == diff_nodeset

if __name__ == '__main__':
    unittest.main()