from morebs2.numerical_generator import * 
from quant.bool_rules import * 
from graph_models.expr_tree import * 
import unittest

### lone file test 
"""
python -m tests.test_bool_rules 
"""
###
class BoolExprCNFGeneratorClass(unittest.TestCase):

    def test__BoolExprCNFGenerator__make__case_1(self):
        prg = prg__LCG(32,14,2,4202)
        var_list = ["A","B","C","D","E","F","G","H"]
        chunk_ratio_range = [0.2,0.5] 
        num_chunks = 3 
        q = BoolExprCNFGenerator(var_list,prg,chunk_ratio_range,num_chunks=5)
        q.make() 
        assert q.S == '(C | F | D | B) & (E | D) & (A | B) & (G | D | C | B) & (E | C)'

        et = ExprTree(q.S) 
        et.process()
        assert len(et.possibleDecisions) == 128 

if __name__ == '__main__':
    unittest.main()