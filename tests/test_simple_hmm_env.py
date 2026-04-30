from quant.simple_hmm_env import * 
from morebs2.numerical_generator import * 
import unittest

def SimpleHMMEnv__TwoAgents__sample_EXCALIBUR(info_mode,offendor_lcg_delta_pattern_type="constant",\
    offendor_pattern_max_length_multiple=4): 
    num_hidden = 8 
    num_observed = 12 

    lcg_o = prg__LCG(34.1,54.3,-31.2,300.15) 
    lcg_d = prg__LCG(-76.54,34.5,-76.55,-1199.5) 
    lcg_e = prg__LCG(356.54,-1334.5,76.55,3199.5) 

    initial_offendor_hidden_state = 3 
    ##offendor_lcg_delta_pattern_type = "constant" 
    offendor_lcgv_range = [-100,100]  

    ##info_mode = "perfect-partial" #"predictive" # "stochastic" # "perfect-full" # 

    she = SimpleHMMEnv__TwoAgents.generate_instance(num_hidden,num_observed,\
        lcg_o,lcg_d,lcg_e,initial_offendor_hidden_state,\
        offendor_lcg_delta_pattern_type,offendor_lcgv_range,\
        offendor_pattern_max_length=int(DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE * offendor_pattern_max_length_multiple),\
        defender_pattern_recognizer_max_size=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE,\
        open_info_mode = info_mode)

    return she 

### lone file test 
"""
py -m tests.test_simple_hmm_env
"""
###
class SimpleHMMEnv__TwoAgentsClass(unittest.TestCase):
    
    def test__SimpleHMMEnv__TwoAgents__next__case_1(self):
        print("stochastic/constant/4")
        she0 = SimpleHMMEnv__TwoAgents__sample_EXCALIBUR("stochastic","constant",4) 
        she0.run_n_rounds(800)

        print("predictive/constant/4")
        she1 = SimpleHMMEnv__TwoAgents__sample_EXCALIBUR("predictive","constant",4) 
        she1.run_n_rounds(800)

        print("perfect-partial/constant/4")
        she2 = SimpleHMMEnv__TwoAgents__sample_EXCALIBUR("perfect-partial","constant",4) 
        she2.run_n_rounds(800)

        print("perfect-full/constant/4")
        she3 = SimpleHMMEnv__TwoAgents__sample_EXCALIBUR("perfect-full","constant",4) 
        she3.run_n_rounds(800)

        assert she0.diff > she1.diff > she2.diff > she3.diff 

        assert she0.diff == 369,"got {}".format(she0.diff)
        assert she1.diff == 323,"got {}".format(she1.diff)
        assert she2.diff == 235,"got {}".format(she2.diff)
        assert she3.diff == 0,"got {}".format(she3.diff)

    def test__SimpleHMMEnv__TwoAgents__next__case_2(self):
        print("predictive/multiple/0.5")
        she0 = SimpleHMMEnv__TwoAgents__sample_EXCALIBUR("predictive","multiple",0.5) 
        she0.run_n_rounds(800)

        assert she0.diff == 645 

if __name__ == '__main__':
    unittest.main()