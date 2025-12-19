from quant.rstruct import * 
from quant.qstruct import * 
from .rnb_samples import * 
import unittest

def RStructGraph_sample_1():
    num_nodes = 12 
    resistance = 100 
    num_questions = 7 
    answer_obj = 1 
    answer_range = [-5,5] 
    num_questions_to_vary = 0 

    prg = prg__LCG(10,2,3,12) 
    Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,num_questions,answer_obj,\
            answer_range,num_questions_to_vary,prg,start_node_idn=0) 
    return Q 

### lone file test 
"""
py -m tests.test_rstruct
"""
###
class RNBClasses(unittest.TestCase):

    def test__RStruct__generate_RStructGraph__type_uniform__case_1(self):
        Q = RStructGraph_sample_1() 
        D = Q[0] 
        K = list(D.keys()) 
        for i in range(len(K)):
            R = D[K[i]]
            assert R.resistance == 100
            assert R.answer_objective == 1
            for v in R.answers_range.values(): 
                assert v == [-5,5], "got {}".format(v)

            for j in range(i+1,len(K)):
                R2 = D[K[j]] 
                dx,dx2 = R.cmp_answer(R2)

                assert not sum(dx.values())

    def test__RStruct__generate_RStructGraph__type_uniform__case_2(self):
        num_nodes,resistance,num_questions,\
        answer_objective,answer_range,num_questions_to_vary,\
        prg,start_node_idn = RStructGraph_generation_parameters() 

        Q = RStruct.generate_RStructGraph__type_uniform(num_nodes,resistance,num_questions,answer_objective,\
                answer_range,num_questions_to_vary,prg,start_node_idn) 

        DX = defaultdict(set) 
        for q in Q[0].values(): 
            c = q.answer_map() 
            for k,v in c.items(): 
                DX[k] |= {v} 
        assert len(DX[0]) > 1 
        assert len(DX[1]) > 1 
        assert len(DX[2]) > 1 
        assert len(DX[3]) == 1 
        assert len(DX[4]) == 1 
        assert len(DX[5]) == 1 

        rs_map = Q[0] 
        answer_type = "most frequent"

        qs0 = QStruct.generate_instance_from_RStructMap(rs_map,answer_type,prg)
        qs0_ans = {np.int64(0): -8, np.int64(1): -1, np.int64(2): 9, np.int64(3): 9, np.int64(4): 8, np.int64(5): -9}
        assert qs0.answers == qs0_ans 

        answer_type = "random" 
        qs1 = QStruct.generate_instance_from_RStructMap(rs_map,answer_type,prg)
        qs1_ans = {np.int64(0): -6, np.int64(1): -4, np.int64(2): 6, np.int64(3): -4, np.int64(4): -10, np.int64(5): -4}
        assert qs1.answers == qs1_ans

    def test__DelegationRuleOperator__delegate_from_node(self):
        Q = RStructGraph_sample_1() 
        do = DelegationRuleOperator(defaultdict(set,Q[1]),default_delegation) 
        N = do.delegate_from_node(0,0,Q[0]) 
        assert N[1] == {0,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, "got {}".format(N)

if __name__ == '__main__':
    unittest.main()