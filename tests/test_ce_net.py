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

    def test__CEAgentNetwork__move_agents__case_1(self): 
        can = CEAgentNetwork__sample_1() 
        can.move_agents()
        cm = can.cea_map
        for v in cm.values():
            print("DB FOR {}".format(v.idn))
            print(v.dbq)
            x = set(v.dbq.agent_info.keys())
            x2 = set(v.s_port_variance.keys())
            assert x == x2 

        can.move_agents() 
        for x in can.main_db.agent_info.values(): 
            assert x.info.shape[0] == 2 

    def test__CEAgentNetwork__move_one_timestamp__case_1(self): 

        can = CEAgentNetwork__sample_1() 
        for _ in range(200): 
            can.move_one_timestamp() 
        
        for i in range(13): 
            c = can.cea_map[i] 
            print("{}:{}".format(c.idn,c.score))
        return 

if __name__ == '__main__':
    unittest.main()
