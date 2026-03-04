from graph_models.lattice_graph_gen import * 
import unittest

def sample_VCLatticeGraphGen_pair(): 
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

    return q,q2 

### lone file test 
"""
py -m tests.test_lattice_graph_gen
"""
###
class VCLatticeGraphGenClass(unittest.TestCase):
    
    """
    Generates 2-dimensional variably connected lattice graphs, 
    of shape (4,4). 

    Checks for intersection between two parallel surfaces and 
    differences between graph outputs from different PRNGs. 
    """
    def test__VCLatticeGraphGen__make__case_1(self):
        q,q2 = sample_VCLatticeGraphGen_pair() 

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

    """
    Tests for intersection between every pair of the 3-dimensional 
    variably connected lattice graph. 
    """
    def test__VCLatticeGraphGen__make__case_2(self): 

        shape = (3,7,6)
        prg = prg__LCG(45.55,78.32,-414.99,500.12) 
        parallel_length_range = (4,5) 
        connection_density = 1.0

        q = VCLatticeGraphGen(shape,prg,parallel_length_range,connection_density,\
                is_dsg=False)
        q.make() 

        x = q.surface_parallels_to_interception_map()

        assert set(x[0].keys()) == set([0, 1, 2])
        assert set(x[1].keys()) == set([0, 1, 2, 3, 4, 5, 6])
        assert set(x[2].keys()) == set([0, 1, 2, 3, 4, 5])

        s0,s1 = q.surfaces[0],q.surfaces[1]
        s2 = q.surfaces[2] 

        dx1 = s0.parallel_intersection_degree_map(s1) 
        assert dx1 == defaultdict(int, {5: 2, 6: 3, 2: 1, 3: 3, 1: 1, 4: 1})

        dx2 = s1.parallel_intersection_degree_map(s2) 
        assert dx2 == defaultdict(int, {4: 5, 5: 8, 0: 2, 2: 4, 1: 4, 3: 4})

        dx3 = s0.parallel_intersection_degree_map(s2)
        assert dx3 == defaultdict(int, {0: 4, 2: 1, 5: 2, 1: 2, 4: 2})

class SymmetricLatticeGraphGenClass(unittest.TestCase):

    """
    Tests for edge difference between symmetric and variably connected 
    lattice graph. 
    """
    def test__LatticeGraphGen__make__case_1(self):
        q,q2 = sample_VCLatticeGraphGen_pair() 

        # generate a symmetric lattice graph 
        prg = prg__LCG(-117.6,-45.55,9001.5,-7575.66) 
        shape = (4,4)
        sl = SymmetricLatticeGraphGen(shape,prg,parallel_length_range=[4,5],is_dsg=False)
        sl.make() 

        mg2_ = MicroGraph(q2.G)
        mg1,mg2 = MicroGraph(sl.G), MicroGraph(q.G) 

        # check the scores 
        score = mg1.sub_ve_score(mg2)
        score2 = mg2.sub_ve_score(mg1)
    
        score_ = mg1.ve_score() 
        score2_ = mg2.ve_score() 
        score2__ = mg2_.ve_score() 

        assert score == (0, 146)
        assert score2 == (0, 80)
        assert score_ == (32, 224)
        assert score2_ == (32, 158)
        assert score2__ == (32, 152)

        return 

if __name__ == '__main__':
    unittest.main()