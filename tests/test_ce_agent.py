from .ce_net_samples import * 
import unittest 

### lone file test 
"""
py -m tests.test_ce_agent
"""
###
class CEAgentClass(unittest.TestCase):

    def test__CEAgent__port_functions__case_1(self): 
        can = CEAgentNetwork__sample_1() 
        a6 = can.fetch_agent(6) 

        try: a6.alter_port(10,'s',False)
        except: assert True

        assert 10 not in a6.fetch_ports('s') 
        assert not a6.is_related(10,'s')
        a6.alter_port(10,'s',True) 
        assert 10 in a6.fetch_ports('s') 
        assert a6.is_related(10,'s')

    def test__CEAgent__port_functions__case_1(self):
        np.random.seed(45)
        random.seed(45) 
        can = CEAgentNetwork__sample_1(True,True)  
        can.deterministic_one_hundred(True) 

        for _ in range(50): 
            can.move_one_timestamp() 
                
        a5 = can.cea_map[5] 
        cr = a5.close_port__max_decision("r",False) 
        cs = a5.close_port__max_decision("s",False) 
        ct = a5.close_port__max_decision("t",False) 

        ro = a5.open_port__max_decision("r",False) 
        so = a5.open_port__max_decision("s",False) 
        to = a5.open_port__max_decision("t",False) 

        assert ro[0][0] == 6 and ro[0][0] not in a5.fetch_ports("r")
        assert so[0][0] == 3 and so[0][0] not in a5.fetch_ports("s")
        assert to[0][0] == 10 and to[0][0] not in a5.fetch_ports("t")

        assert cr[0][0] == 9 and cr[0][0] in a5.fetch_ports("r")
        assert cs[0][0] == 11 and cs[0][0] in a5.fetch_ports("s")
        assert ct[0][0] in {6,9} and ct[0][0] in a5.fetch_ports("t"), "got {}".format(ct)

if __name__ == '__main__':
    unittest.main()
