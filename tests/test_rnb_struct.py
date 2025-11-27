from quant.rnb_struct import * 
from morebs2.numerical_generator import * 
import unittest

### lone file test 
"""
python -m tests.test_rnb_struct
"""
###
class RNBClasses(unittest.TestCase):

    def test__RStruct__generate_RStructGraph__type_uniform__case_1(self):

        num_nodes = 12 
        resistance = 100 
        num_questions = 7 
        answer_obj = 1 
        answer_range = [-5,5] 
        num_questions_to_vary = 0 

        prg = prg__LCG(10,2,3,12) 
        Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,num_questions,answer_obj,\
                answer_range,num_questions_to_vary,prg,start_node_idn=0) 

        D = Q[0] 
        K = list(D.keys()) 
        for i in range(len(K)):
            R = D[K[i]]
            assert R.resistance == resistance
            assert R.answer_objective == answer_obj
            assert R.answers_range == answer_range
            for j in range(i+1,len(K)):
                R2 = D[K[j]] 
                dx,dx2 = R.cmp_answer(R2)

                assert not sum(dx.values())
        print("%")


if __name__ == '__main__':
    unittest.main()