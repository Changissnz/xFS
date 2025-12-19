from graph_problems.rnb import * 
from .rnb_samples import * 
import unittest

### lone file test 
"""
py -m tests.test_rnb 
"""
###
class RNBotClass(unittest.TestCase):

    def test__RNBot__facilitate_question_case_1(self):

        num_nodes,resistance,num_questions,\
        answer_objective,answer_range,num_questions_to_vary,\
        prg,start_node_idn = RStructGraph_generation_parameters()  


        qstructgen_answer_type = "most frequent"
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type)

        neighbors = {2, 3, 4, 5, 6}
        assert neighbors == rnbot.d[1] 

        n1 = rnbot.rstruct_map[1]
        n2 = rnbot.rstruct_map[2]
        n3 = rnbot.rstruct_map[3]
        n4 = rnbot.rstruct_map[4]
        n5 = rnbot.rstruct_map[5]
        n6 = rnbot.rstruct_map[6]

        assert n1.answer_(0) == n2.answer_(0)
        for x in [n3,n4,n5,n6]: 
            assert n1.answer_(0) != x.answer_(0)

        for x in [n2,n3,n4,n5,n6]: 
            assert n1.answer_(1) != x.answer_(1)

        assert n1.answer_(2) == n5.answer_(2) 
        for x in [n2,n3,n4,n6]: 
            assert n1.answer_(2) != x.answer_(2) 

        ans_map = {0:-8,1:3,2:-3,3:9,4:8,5:-9} 
        nodeset_map = {0:{1, 2},\
                1:{1},\
                2:{1, 5},\
                3:{0, 1, 2, 3, 4, 5, 6, 8, 9},\
                4:{0, 1, 2, 3, 4, 5, 6, 8, 9},\
                5:{0, 1, 2, 3, 4, 5, 6, 8, 9}}

        for i in range(6): 
            qx = rnbot.facilitate_question(1,i)
            assert qx[0] == ans_map[i] 
            assert qx[1] == nodeset_map[i] 
        return

    def test__RNBot__next__case_1(self):

        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 

        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(1,1,1,1)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=True) 

        while not rnbot.fin_stat:
            next(rnbot) 

        q = rnbot.sim_status() 
        ans = '\tQ is active?\nTrue\n\n\tActive <RStruct> Nodes:\n'
        assert q == ans 

    def test__RNBot__next__case_2(self):

        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 
        num_questions_to_vary = 0 

        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(1,1,1,1)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=True) 

        while not rnbot.fin_stat:
            next(rnbot) 

        q = rnbot.sim_status() 
        ans = '\tQ is active?\nTrue\n\n\tActive <RStruct> Nodes:\n'
        assert q == ans 

    def test__RNBot__next__case_3(self):

        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 

        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(0,0,0,0)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=True) 

        while not rnbot.fin_stat:
            next(rnbot) 

        q = rnbot.sim_status() 
        ans = '\tQ is active?\nFalse\n\n\tActive <RStruct> Nodes:\n0,1,2,3,4,5,6,7,9'
        assert q == ans,"got {}".format(q)

    """
    case: Q and RNet are already aligned. 
    """
    def test__RNBot__next__case_4(self):
        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 
        num_questions_to_vary = 0 

        qstructgen_answer_type = "most frequent"
        qstruct_open_info_mode=(1,1,1,1)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=True) 
        rnbot.qstruct.energy /= 100 

        while not rnbot.fin_stat:
            next(rnbot) 

        q = rnbot.sim_status()
        assert q == '\tQ is active?\nFalse\n\n\tActive <RStruct> Nodes:\n0,1,2,3,4,5,6,7,8,9' 

    """
    tests for correct <QStruct> move repeat. 
    """
    def test__RNBot__next__case_5(self): 
        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 

        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(0,0,0,0)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=False)
        rnbot.qstruct.energy /= 100 
        rnbot.qstruct.nfa_type = 1 
        rnbot2 = deepcopy(rnbot) 

        while not rnbot.fin_stat:
            next(rnbot) 

        q0 = rnbot.qstruct.energy 
        rdict0 = rnbot.rstruct_node_resistances()


        rnbot2.qstruct.load_prior_QSMoveLog(rnbot.qstruct.qsm_log) 
        while not rnbot2.fin_stat:
            next(rnbot2) 

        q1 = rnbot2.qstruct.energy 
        rdict1 = rnbot2.rstruct_node_resistances()

        assert q0 == q1 
        assert rdict0 == rdict1 
        return 

    """
    test NFA#3 
    """
    def test__RNBot__next__case_6(self): 
        num_nodes,resistance,num_questions,answer_objective,\
            answer_range,num_questions_to_vary,prg,start_node_idn = \
            RNBot_parameters_case_T() 

        num_questions_to_vary = 0 
        qstructgen_answer_type = "random"
        qstruct_open_info_mode=(0,0,0,0)
        rnbot = RNBot.generate_instance(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,0,qstructgen_answer_type,qstruct_open_info_mode,\
                verbose=True)
        rnbot.qstruct.energy /= 10 
        rnbot.qstruct.nfa_type = 3 
        rnbot2 = deepcopy(rnbot) 

        while not rnbot.fin_stat:
            next(rnbot) 

        q0 = rnbot.qstruct.energy 
        rdict0 = rnbot.rstruct_node_resistances()


        rnbot2.qstruct.load_prior_QSMoveLog(rnbot.qstruct.qsm_log) 
        while not rnbot2.fin_stat:
            next(rnbot2) 

        q1 = rnbot2.qstruct.energy 
        rdict1 = rnbot2.rstruct_node_resistances()

        assert q0 == q1 
        assert rdict0 == rdict1 
        assert np.float64(2640.0) == q0 

###

if __name__ == '__main__':
    unittest.main()