from .ce_net_samples import * 
import unittest 

### lone file test 
"""
py -m tests.test_ce_net
"""
###
class CEAgentNetworkClass(unittest.TestCase):

    def test__CEAgentNetwork__is_reactive_dtriplet__case_1(self): 
        can = CEAgentNetwork__sample_1() 
        assert can.is_reactive_dtriplet((6,11,1)) == (True,True,True) 
        assert can.is_reactive_dtriplet((6,0,1)) == (True, True, False)
        assert can.is_reactive_dtriplet((6,5,8)) == (True, False, False)

if __name__ == '__main__':
    unittest.main()
