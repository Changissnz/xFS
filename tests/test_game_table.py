from graph_models.game_table import * 
from morebs2.numerical_generator import prg__LCG 
import unittest

def FullMultiAgentActionTable__sample_FF(ref_is_immediate_payoff:bool):  

    agents = {0,1,2}
    agent2movesize_map = {0:3,1:2,2:2}
    agent_action_value_range = [-10,10]

    bracket_size_range = [3,7] 
    total_payoff_multiplier_range = [-50,50] 
    prg = prg__LCG(84.47,15.31,-173.22,4042.555)

    move_idn_counter = SimpleCounter(0).__next__

    ft = FullMultiAgentActionTable.generate_instance(agents,agent2movesize_map,\
        agent_action_value_range,prg,bracket_size_range,move_idn_counter,\
        total_payoff_multiplier_range,\
        duration_range=FullMultiAgentActionTable.DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE,\
        ref_is_immediate_payoff=ref_is_immediate_payoff)
    return ft 

### lone file test 
"""
py -m tests.test_game_table
"""
###
class FullMultiAgentActionTableClass(unittest.TestCase):

    def test__FullMultiAgentActionTable__case_1(self):
        ft = FullMultiAgentActionTable__sample_FF(True) 

        d0 = {0:-1.51527,1:-9.50904,2:-7.84753} 
        dx0 = ft["0,0,1,3,2,5"] 
        assert d0 == dx0 

        d1 = {0:9.15707,1:360.40506,2:360.86114} 
        dx1 = ft.agent_action_cmap["0,0,1,3,2,5"] 
        assert d1 == dx1 

        d2 = {0:6,1:14,2:18} 
        dx2 = ft.agent_action_dmap["0,0,1,3,2,5"] 
        assert d2 == dx2 
        return

    def test__FullMultiAgentActionTable__case_2(self):
        ft = FullMultiAgentActionTable__sample_FF(False)  
        d0 = {0:-0.02546,1:0.01245,2:0.03171} 
        dx0 = ft["0,0,1,3,2,5"] 
        assert d0 == dx0 

        d1 = {0:-1.51527,1:-9.50904,2:-7.84753} 
        dx1 = ft.agent_action_cmap["0,0,1,3,2,5"] 
        assert d1 == dx1 

        d2 = {0:6,1:14,2:18} 
        dx2 = ft.agent_action_dmap["0,0,1,3,2,5"] 
        assert d2 == dx2 
        return

if __name__ == '__main__':
    unittest.main()