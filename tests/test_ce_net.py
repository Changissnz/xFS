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
        can.update_bridges() 
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
        can = CEAgentNetwork__sample_1(False) 
       
        # t=0
        can.move_one_timestamp()

        idn = 4
        a4 = can.fetch_agent(idn) 

        comm_delta,exec_delta = 0,0
        dx = defaultdict(float)
        for k,v in a4.communication_delta.items():
            comm_delta += sum(v.values())
            dx[k] = sum(v.values())

        for c in can.cea_map.values():
            print("C: {}->{}".format(c.idn,c.current_reaction[idn]))
            exec_delta += c.current_reaction[idn]

        s = -comm_delta + exec_delta
        assert abs(a4.score - s) <= 10 ** -4 


        # t=1 
        can.move_one_timestamp()
        comm_delta2,exec_delta2 = 0,0
        for k,v in a4.communication_delta.items():
            comm_delta2 += sum(v.values()) - dx[k] 

        for c in can.cea_map.values():
            exec_delta2 += c.current_reaction[idn]

        assert abs(comm_delta2 - comm_delta) > 10 ** -5 
        assert abs(exec_delta2 - exec_delta) > 10 ** -5 

        expected2 = s + (-comm_delta2 + exec_delta2)
        assert abs(a4.score - expected2) <= 10 **-4, "got {} expected {}".format(a4.score,expected2)

    """
    a print-test 
    """
    def test__CEAgentNetwork__move_one_timestamp__case_2(self): 

        can = CEAgentNetwork__sample_1(False) 
        for _ in range(100): 
            can.move_one_timestamp() 
        
        for i in range(13): 
            c = can.cea_map[i] 
            print("{}:{}".format(c.idn,c.score))
        return 

    """
    demonstrates difference in score outcomes of mode `negative_reaction_allowed` 
    """
    def test__CEAgentNetwork__move_one_timestamp__case_3(self):

        can = CEAgentNetwork__sample_1(False) 
        can.deterministic_one_hundred(True)
        for _ in range(2): 
            can.move_one_timestamp() 

        can2 = CEAgentNetwork__sample_1(True) 
        can2.deterministic_one_hundred(True) 
        for _ in range(2): 
            can2.move_one_timestamp() 

        can3 = CEAgentNetwork__sample_1(False) 
        can3.deterministic_one_hundred(True)
        for _ in range(2): 
            can3.move_one_timestamp() 
        

        dmap = dict()
        dmap2 = dict() 
        for k in can.cea_map.keys(): 
            c0 = can.cea_map[k]
            c1 = can2.cea_map[k]
            c2 = can3.cea_map[k]

            dmap[k] = round(c1.score - c0.score,5) 
            dmap2[k] = round(c2.score - c0.score,5) 

        ans = {7: -28322.35617, 10: -21942.95849, \
            11: -38520.52462, 8: -35641.55698, \
            3: -20882.65389, 1: -44257.85061, \
            2: -39529.9821, 4: -23711.98803, \
            9: -23506.23402, 5: -47716.20482, \
            0: -41717.49754, 12: -29574.0191, \
            6: -31418.37468}

        # difference in negatives  
        for k in dmap.keys(): 
            assert ans[k] == dmap[k],"got {} want {}".format(dmap[k],ans[k])

        # equal in positives 
        for k in dmap2.keys(): 
            assert dmap2[k] == 0. 
        return 

    '''
    demonstrates difference in score outcomes of mode `reaction_requires_connection` 
    '''
    def test__CEAgentNetwork__move_one_timestamp__case_4(self):

        can = CEAgentNetwork__sample_1(True,False) 
        can.deterministic_one_hundred(True)
        for _ in range(2): 
            can.move_one_timestamp() 

        can2 = CEAgentNetwork__sample_1(True,True) 
        can2.deterministic_one_hundred(True) 
        for _ in range(2): 
            can2.move_one_timestamp() 

        dmap = dict()
        for k in can.cea_map.keys(): 
            c0 = can.cea_map[k]
            c1 = can2.cea_map[k]
            dmap[k] = round(c1.score - c0.score,5) 

        ans = {7: 18687.32172, 10: 15710.03073, \
            11: 18139.67816, 8: 15120.80177, \
            3: 9155.88729, 1: 23477.91154, \
            2: 25798.92263, 4: 5967.76383, \
            9: 19788.48679, 5: 29034.4076, \
            0: 22024.78274, 12: 13681.44473, \
            6: 6191.73424}
        assert dmap == ans 

if __name__ == '__main__':
    unittest.main()
