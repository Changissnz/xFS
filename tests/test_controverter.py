from quant.gt_agent import * 
from morebs2.numerical_generator import prg__LCG 
import time 
import unittest

def GameControverter__sample_GCX(pcorrelation_payoff,pcorrelation_upturn): 
    agents = {0,1,2}
    agent2movesize_map = {0:3,1:2,2:2}
    agent_action_value_range = [-10,10]
    bracket_size_range = [3,7] 
    total_payoff_multiplier_range = [-50,50] 
    move_idn_counter = SimpleCounter(0).__next__

    prg = prg__LCG(17.47,16.31,-179.22,4042.555)

    gc = GameControverter.generate_instance(agents,agent2movesize_map,\
        agent_action_value_range,prg,bracket_size_range,move_idn_counter,\
        total_payoff_multiplier_range,\
        pcorrelation_payoff,pcorrelation_upturn)
    return gc 

def GTAgent__sample_TA(): 
    prg = prg__LCG(65.5,-155.4,131.55,7070.55) 
    gta = GTAgent(agent_idn=0,objective="self",objective_var=2,prg=prg) 
    return gta 

"""
py -m tests.test_controverter
"""
class GTAgentClass(unittest.TestCase): 

    def test__GTAgent__decision__case_1(self): 
        gc = GameControverter__sample_GCX(0,0) 

        r0 = deepcopy(gc.agent2payoff_range)

        prg = prg__LCG(65.5,-155.4,131.55,7070.55) 
        gta = GTAgent(agent_idn=0,objective="self",objective_var=2,prg=prg) 

        T = gc.ftable.agent_action_cmap 
        qx = gta.decision(T,other_agent_moves={})

        T2 = gc.ftable  
        qx2 = gta.decision(T2,other_agent_moves={}) 
        assert qx == 0 
        assert qx2 == 1 

class GameControverterClass(unittest.TestCase):

    def test__GameControverter__next__case_1(self):
        gta = GTAgent__sample_TA() 
        gc = GameControverter__sample_GCX(0,0) 
        M = GTAgent.best_decision_for_game(gta,gc,"c") 

        #before = deepcopy(gc.ftable)
        gc.recv_agent_move_map(M)
        next(gc) 
        r0 = deepcopy(gc.agent2payoff_range)

        assert gc.previous_agent_move_rank == {0: (0, 2), 1: (0, 1), 2: (0, 1)},"got {}".format(gc.previous_agent_move_rank)

        M = GTAgent.best_decision_for_game(gta,gc,"c") 
        gc.recv_agent_move_map(M)
        next(gc) 

        #after = deepcopy(gc.ftable)
        r1 = deepcopy(gc.agent2payoff_range)
        assert gc.previous_agent_move_rank == {0: (0, 6), 1: (0, 1), 2: (0, 2)},"got {}".format(gc.previous_agent_move_rank)

        # check for correct payoff range adjustment 
        for k,v in r0.items(): 
            v2 = r1[k] 
            assert v[0] > v2[0] 

    def test__GameControverter__next__case_2(self):
        gta = GTAgent__sample_TA() 
        
        gc = GameControverter__sample_GCX(0,0) 
        gc1 = GameControverter__sample_GCX(1,0) 

        M = GTAgent.best_decision_for_game(gta,gc,"c") 
        gc.recv_agent_move_map(M)

        next(gc) 
        r0 = deepcopy(gc.agent2payoff_range)

        gc1.recv_agent_move_map(M) 
        next(gc1) 

        assert gc.previous_agent_move_rank == {0: (0, 2), 1: (0, 1), 2: (0, 1)}
        assert gc1.previous_agent_move_rank == {0: (2, 2), 1: (1, 1), 2: (1, 1)}
        assert gc.agent2payoff_range == gc1.agent2payoff_range

    def test__GameControverter__next__case_3(self):
        gta = GTAgent__sample_TA() 
        
        gc = GameControverter__sample_GCX(0,0.5) 
        gc1 = GameControverter__sample_GCX(1,0.5)  

        r0 = deepcopy(gc.agent2payoff_range)

        M = GTAgent.best_decision_for_game(gta,gc,"c") 
        gc.recv_agent_move_map(M)

        next(gc) 
        r0 = deepcopy(gc.agent2payoff_range)

        M_ = GTAgent.best_decision_for_game(gta,gc1,"c")
        gc1.recv_agent_move_map(M_) 
        next(gc1) 

        M10 = GTAgent.best_decision_for_game(gta,gc,"c") 

        gc.recv_agent_move_map(M10)
        next(gc) 
        M11 = GTAgent.best_decision_for_game(gta,gc1,"c") 


        gc1.recv_agent_move_map(M11)
        next(gc1)

        r10 = deepcopy(gc.agent2payoff_range)
        r11 = deepcopy(gc1.agent2payoff_range) 

        # check for correct move ranking 
        assert gc.previous_agent_move_rank == {0: (0, 6), 1: (0, 1), 2: (0, 2)}
        assert gc1.previous_agent_move_rank == {0: (6, 6), 1: (1, 1), 2: (2, 2)}

        # check for correct bracket relation 
        for k,v in gc.next_agent_bracket.items(): 
            v2 = gc1.next_agent_bracket[k] 
            assert v2[0] < v[0] 

        # check for correct payoff relation 
        ans = {0: np.array([2183.79434, 2186.65148]), \
            1: np.array([16860.58422, 16870.58422]), \
            2: np.array([989.91245, 996.57912])}

        for k,v in gc.next_agent_bracket.items(): 
            assert np.all(v == ans[k])
            sx = r10[k] 
            b0 = np.array([v]) 
            b1 = np.array([sx]) 
            assert bounds_is_subbounds(b1,b0) 

        ans = {0: np.array([-3574.2933 , -3571.43616]), \
            1: np.array([-4125.92428, -4115.92428]), \
            2: np.array([-4518.70272, -4512.03605])}

        for k,v in gc1.next_agent_bracket.items(): 
            assert np.all(v == ans[k])
            sx = r11[k] 
            b0 = np.array([v]) 
            b1 = np.array([sx]) 
            assert bounds_is_subbounds(b1,b0) 

if __name__ == '__main__':
    unittest.main()