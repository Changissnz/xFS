from quant.strangle_form import * 
from morebs2.numerical_generator import * 
import unittest

### lone file test 
"""
py -m tests.test_strangle_form  
"""
###
class StrangleFormClass(unittest.TestCase):

    def test__StrangleForm__move__case_1(self): 

        G = defaultdict(set,\
            {0:{1,3},\
            1:{0,2},\
            2:{1,3},\
            3:{0,2,4},\
            4:{3,5,7},\
            5:{4,6},\
            6:{5,7},\
            7:{4,6}}) 

        prg = prg__LCG(34.4,-14.31,55.7,505.11) 

        sf = StrangleForm(G,prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
                force_assignment_type="random",force_per_node_range=[10,1000]) 

        sf.move({0,3})
        #print("ONE")
        #print(sf.held_nodes)
        # {0: 44.4, 3: 78.54599999999999, 2: 44.131696200286626}
        assert set(sf.held_nodes.keys()) == {0,2,3} 
        assert len(sf.usgcs) == 1 

        sf.move({0,3})
        #print("TWO")
        #print(sf.held_nodes)
        assert set(sf.held_nodes.keys()) == {0,1,2,3,4} 
        # {0: 44.4, 3: 78.54599999999999, 2: 44.131696200286626, 4: 140.30031446015215, 1: 69.18682392356254}
        assert len(sf.usgcs) == 1 

        reaction = {0:-50.,3:-80.}
        sf.register_reaction(reaction) 
        sf.move({0,3})
        #print("THREE")
        #print(sf.held_nodes)
        assert set(sf.held_nodes.keys()) == {0,1,2,3,4,7} 
        assert len(sf.usgcs) == 2 

if __name__ == '__main__':
    unittest.main()