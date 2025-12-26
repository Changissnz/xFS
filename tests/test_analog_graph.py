from graph_models.analog_graph import * 
from morebs2.numerical_generator import prg__LCG 
import unittest

def analog_info__sample_VUN(): 

    prg = prg__LCG(87,354,675456,20) 
    tg = TreeGen(starting_nodeset = {0},is_dsg=False,prg=prg,branching_range=DEFAULT_TREE_BRANCHING_RANGE)

    for _ in range(5): 
        next(tg) 

    ctr_function = SimpleCounter(len(tg.d)).__next__
    G2,isomap = shortest_paths_graph_analogue(tg.d,0,False,3,4,prg,ctr_function) 

    return tg.d,G2,isomap,prg  


"""
py -m tests.test_analog_graph
"""
class AnalogGraphClass(unittest.TestCase):

    """
    checks that node analogy maps, calculated with aid of PRNG `prg`, 
    obey expected accuracy. 
    """
    def test__AnalogGraph__draw_analogy_to__case1(self):
        ref_graph,G2,isomap,prg = analog_info__sample_VUN() 
        ag = AnalogGraph(reference_graph=ref_graph,isomap=isomap,prg=prg,\
            isomorphic_subgraph_radius=DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS)

        diffs = [] 
        for _ in range(10): 
            R2 = ag.draw_analogy_to(G2,_ * 0.05)  
            d = dict_diff(ag.isomap,R2) 
            diffs.append(d) 

        assert diffs == [8, 6, 7, 6, 6, 6, 5, 5, 4, 4]

        return 


if __name__ == '__main__':
    unittest.main()