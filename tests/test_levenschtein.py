from quant.levenschtein import *
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
py -m tests.test_levenschtein 
"""
###
class LevenschteinClass(unittest.TestCase):
    
    def test__levenschtein_distance__case_1(self):
        s1 = "cat"
        s2 = "kattle" 

        s3 = "fordinos"
        s4 = "fraudinos" 
        s5 = "taskos" 

        s6 = "white cat"
        s7 = "black hat"

        s8 = "stray bridge" 
        s9 = "all rigged"

        s10 = "locked"
        s11 = "dead john locke"


        q = levenschtein_distance(s1,s2)
        q2 = levenschtein_distance(s3,s4)
        q3 = levenschtein_distance(s3,s5) 
        q4 = levenschtein_distance(s6,s7) 
        q5 = levenschtein_distance(s8,s9) 
        q6 = levenschtein_distance(s10,s11) 

        assert [q,q2,q3,q4,q5,q6] == [4,3,6,6,8,11]

if __name__ == '__main__':
    unittest.main()