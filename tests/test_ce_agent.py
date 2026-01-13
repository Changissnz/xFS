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

if __name__ == '__main__':
    unittest.main()
