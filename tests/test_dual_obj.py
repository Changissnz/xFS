from quant.dual_obj import * 
import unittest

"""
py -m tests.test_dual_obj
"""
class DualEnvTypeHLClass(unittest.TestCase):

    """
    tests that an agent in <DualEnvTypeHL>, with independent demands 
    identical to third-party demands, encounters 0 cost in execution. 
    """
    def test__DualEnvTypeHL__move_one__case_1(self):
        
        prg = prg__LCG(43,-5444.6,19.55,4520.77) 
        env = DualEnvTypeHL.generate_instance(prg)

        # try identical demands 
        env.dual_agent.independent_demands =  deepcopy(env.third_party_demands)

        while not env.fin_stat: 
            env.move_one() 

        assert env.cost_record.independent == 0 == env.cost_record.third_party

    """
    demonstrates non-zero cost for non-identical independent and third-party demands 
    """
    def test__DualEnvTypeHL__move_one__case_2(self):

        prg = prg__LCG(-13.45,114.66,-794.55,-91665.55)
        env = DualEnvTypeHL.generate_instance(prg)

        while not env.fin_stat: 
            env.move_one() 

        assert env.cost_record.independent == 138.16413
        assert env.cost_record.third_party == 150 


if __name__ == '__main__':
    unittest.main()