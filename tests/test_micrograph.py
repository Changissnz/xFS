from graph_models._mg_sample import *
import unittest

def unordered_setseq__equals(s1,s2):
    if len(s1) != len(s2): return False

    for s in s1:
        stat = False
        for q in s2:
            if q == s:
                stat = True
                break
        if not stat: return False
    return True

### lone file test 
"""
python -m tests.test_micrograph 
"""
###
class MicroGraphClass(unittest.TestCase):

    def test__MicroGraph___sub__(self):
        mg4 = sample_MicroGraph_4()
        mg6 = sample_MicroGraph_6()
        
        mgx = mg4 - mg6

        dg = defaultdict(set, {'2': {'1', '3'},\
            '3': {'0', '2'},\
            '4': {'0'},\
            '5': {'0'}})
        assert mgx.dg == dg
        return

    def test__MicroGraph_alt_subtract(self):
        mgx1 = MicroGraph(defaultdict(set,{"0":set(),"1":set()}))
        mgx2 = MicroGraph(defaultdict(set,{"0":{"1"},"1":{"0"}}))
        mgx = mgx2.alt_subtract(mgx1) 

        sol10 = set()
        sol11 = {'0,1', '1,0'}
        assert mgx[0] == sol10 and mgx[1] == sol11
        return

    def test__MicroGraph_component_seq(self):
        # case 1
        dg = {"0":{"1","2","3"},\
            "1":{"0","3"},\
            "2":{"0","3","4","5"},\
            "3":{"0","1","2","5"},\
            "4":{"2"},\
            "5":{"2","3"},\
            "6":{"7","8","9"},\
            "7":{"6","8"},\
            "8":{"6","7"},\
            "9":{"6"},\
            "10":{"11"},\
            "11":{"10"},\
            "12":{"13","14"},\
            "13":{"12"},\
            "14":{"12"}}
        mg = MicroGraph(defaultdict(set,dg)) 
        cs = mg.component_seq() 
        sol = [{'7', '6', '9', '8'},\
            {'5', '0', '3', '1', '2', '4'},\
            {'14', '13', '12'}, {'11', '10'}]

        assert unordered_setseq__equals(cs,sol)

        # case 2
        dg2 = {"0":{"1"},\
                "1":{"0"},\
                "2":{"3","4"},\
                "3":{"2"},\
                "4":{"2"},\
                "5":set(),\
                "6":{"7","8"},\
                "7":{"6"},\
                "8":{"6"}}
        mg2 = MicroGraph(defaultdict(set,dg2)) 
        cs2 = mg2.component_seq() 

        sol2 = [{'5'}, {'0', '1'}, {'2', '3', '4'}, {'7', '6', '8'}]
        assert unordered_setseq__equals(cs2,sol2) 

        return 

      
if __name__ == '__main__':
    unittest.main()