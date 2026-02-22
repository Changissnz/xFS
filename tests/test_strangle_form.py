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

class StrangleSubjectMethods(unittest.TestCase):

    """
    case: impossible for any force to break stranglehold 
    """
    def test__default_strangle_breaking_function__case_1(self): 
        D = {0:0,\
            1:0,\
            2:50,\
            3:50} 

        q = default_strangle_breaking_function(D,-200) 
        q2 = default_strangle_breaking_function(D,-400) 
        q2_ = default_strangle_breaking_function(D,-800) 

        assert q == q2 == q2_ 
        assert q == {0: 0, 1: 0, 2: 0.0, 3: 0.0} 
        return 

    """
    case: possible for force to break stranglehold 
    """
    def test__default_strangle_breaking_function__case_2(self): 

        D2 = {0:0,\
            1:25,\
            2:50,\
            3:50} 
        q3 = default_strangle_breaking_function(D2,-50) 
        q4 = default_strangle_breaking_function(D2,-100) 

        assert q3 == {0: 0, 1: -8.33333, 2: -8.33333, 3: -8.33333}
        assert q4 == {0: 0, 1: -16.66667, 2: -16.66667, 3: -16.66667}

    """
    case: weighted case, possible for force to break stranglehold 
    """
    def test__default_strangle_breaking_function__case_3(self): 

        D = {0:0,\
            1:0,\
            2:50,\
            3:50} 

        W = {0:1,\
            1:1,\
            2:2,\
            3:1} 
        q5 = default_strangle_breaking_function(D,-200,W)  
        assert q5 == {0: 0, 1: 0, 2: -16.66667, 3: -16.66667}

    """
    case: weighted case, min force to break stranglehold 
    """
    def test__min_strangle_breaking_force__case_1(self): 

        D = {0:0,\
            1:0,\
            2:50,\
            3:50} 

        W = {0:1,\
            1:1,\
            2:2,\
            3:1} 

        mf = min_strangle_breaking_force(D,None)
        assert type(mf) == type(None) 

        mf2 = min_strangle_breaking_force(D,W)
        q6 = default_strangle_breaking_function(D,-mf2,W) 
        assert q6 == {0: 0, 1: 0, 2: -50.0, 3: -50.0}

    """
    case: unweighted case, min force to break stranglehold 
    """
    def test__min_strangle_breaking_force__case_2(self): 
        D2 = {0:0,\
            1:25,\
            2:50,\
            3:50} 
        mf = min_strangle_breaking_force(D2,None)
        assert round(mf,5) == 300 

if __name__ == '__main__':
    unittest.main()