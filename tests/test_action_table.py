from graph_models.action_table import * 
from morebs2.numerical_generator import prg__LCG 

def MultiAgentActionTable__sample_P(): 
    agents = {0,1,2}
    agent2movesize_map = {0:3,1:2,2:2}
    agent_action_value_range = [-10,10]
    prg = prg__LCG(-14.44,23.31,-73.22,-4040.555)
    mt = MultiAgentActionTable.generate_instance__type_prng(agents,agent2movesize_map,agent_action_value_range,\
            prg,move_idn_counter=SimpleCounter(0).__next__)
    return mt 

def MultiAgentActionTable__sample_S(): 
    agents = {0,1,2}
    agent2movesize_map = {0:3,1:2,2:2}
    agent_action_value_range = [-10,10]

    bracket_size_range = [3,7] 
    prg = prg__LCG(84.47,15.31,-173.22,4042.555)
    mt2 = MultiAgentActionTable.generate_instance__type_strict_percentile(agents,\
        agent2movesize_map,agent_action_value_range,prg,bracket_size_range,\
        move_idn_counter=SimpleCounter(0).__next__)
    return mt2 

def MultiAgentActionTable__sample_A(): 

    agents = {4,5,6} 
    agent_action_map = {"4,0,5,0,6,0": {4:3,5:-8,6:5},\
            "4,0,5,1,6,0": {4:4,5:3,6:6},\
            "4,0,5,0,6,1": {4:5,5:-6,6:-1},\
            "4,0,5,1,6,1": {4:8,5:4,6:-1},\
            "4,1,5,0,6,0": {4:-6,5:-7,6:-1},\
            "4,1,5,0,6,1": {4:-8,5:-4,6:-1},\
            "4,1,5,1,6,0": {4:-2,5:5,6:6},\
            "4,1,5,1,6,1": {4:-1,5:5,6:5}}

    mt3 = MultiAgentActionTable(agents,agent_action_map) 
    return mt3 

import unittest

### lone file test 
"""
py -m tests.test_action_table
"""
###
class MultiAgentActionTableClass(unittest.TestCase):

    def test__MultiAgentActionTable__base_info_on_agent_move__case_1(self):
        mt = MultiAgentActionTable__sample_A() 
        agent_idn = 4 
        x0 = mt.base_info_on_agent_move(agent_idn,0) 
        x1 = mt.base_info_on_agent_move(agent_idn,1) 
        assert x0 == (3,8,5) 
        assert x1 == (-8,-1,-4.25) 
        return

    def test__MultiAgentActionTable__base_info_on_agent_move__case_2(self):
        mt = MultiAgentActionTable__sample_S() 
        agent_idn = 0 
        x = mt.base_info_on_agent_move(agent_idn,0) 
        assert x == (-1.51527, 1.29126, 0.00887)
        x1 = mt.base_info_on_agent_move(agent_idn,1) 
        assert x1 ==  (-8.99638,-3.8763, -6.46651)
        x2 = mt.base_info_on_agent_move(agent_idn,2) 
        assert x2 == (4.26161,9.89284,7.52241) 

    def test__MultiAgentActionTable__sort_agent_moves__case_1(self):
        mt = MultiAgentActionTable__sample_S() 
        agent_idn = 0 
        o1 = mt.sort_agent_moves(agent_idn,0,other_agent_moves={})
        o1_ = [o[0] for o in o1] 
        o2 = mt.sort_agent_moves(agent_idn,1,other_agent_moves={})
        o2_ = [o[0] for o in o2] 
        o3 = mt.sort_agent_moves(agent_idn,2,other_agent_moves={})
        o3_ = [o[0] for o in o3] 
        assert o1_ == o2_ == o3_ == [1, 0, 2]

    def test__MultiAgentActionTable__possible_ranks_of_agent_by_move__case_1(self):
        mt = MultiAgentActionTable__sample_A() 
        agent_idn = 4 

        other_moves = {}
        r = mt.possible_ranks_of_agent_by_move(agent_idn,0,other_moves)
        assert r == [1, 2, 1, 2]

        other_moves = {5:0}
        r2 = mt.possible_ranks_of_agent_by_move(agent_idn,0,other_moves)
        assert r2 == [1, 2]

        return

    def test__MultiAgentActionTable__agent_move_for_minmean_value_by_other_agents__case_1(self):
        mt = MultiAgentActionTable__sample_A() 
        agent_idn = 4 

        prg = prg__LCG(4.47,715.31,-1173.22,44040.555)
        r3 = mt.agent_move_for_minmean_value_by_other_agents(agent_idn,{5},other_agent_moves={6:1},\
                prg = prg)
        assert r3 == 0 

if __name__ == '__main__':
    unittest.main()