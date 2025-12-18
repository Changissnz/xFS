from graph_problems.sim_solution_search import * 
from .rnb_samples import * 
import unittest

def prng_seq__sample_TRDEAD(): 
    prg1 = prg__LCG(14,53,23,1212)
    prg2 = default_std_Python_prng(4000)
    prg3 = default_std_Python_prng(143)
    prg4 = default_std_Python_prng(675)
    prg5 = default_std_Python_prng(2121)
    prg6 = default_std_Python_prng(54199)
    prg7 = default_std_Python_prng(4412)
    prg8 = prg__LCG(0,1,1,3) 
    prg9 = prg__LCG(1,2,1,5) 
    prng_seq = [prg1,prg2,prg3,prg4,prg5,prg6,prg7,prg8,prg9]
    return prng_seq 

### lone file test 
"""
py -m tests.test_sim_solution_search 
"""
###
class SimulationSolutionSearchClass(unittest.TestCase):

    def test__SimulationSolutionSearch__full_run__case_1(self):

        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 

        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(0,0,0,0)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=False)
        rnbot.qstruct.energy /= 10
        rnbot.qstruct.nfa_type = 1 

        prng_seq = prng_seq__sample_TRDEAD() 

        S = SimulationSolutionSearch(rnbot,RNB_env_run,prng_seq,\
                RNB_env_prng_assignment_function,RNB_env_mode_shift_function,\
                RNB_env_solution_fetch_function,RNB_env_cmp_solution__type_1)#RNB_env_cmp_solution__type_2_function())

        i = 0 
        while not S.fin_stat: 
            print("iter ",i)
            S.process_one()
            i += 1 
        return 



if __name__ == '__main__':
    unittest.main()