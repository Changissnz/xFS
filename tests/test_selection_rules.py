from quant.selection_rules import * 
import unittest 

### lone file test 
"""
py -m tests.test_selection_rules 
"""
class BooleanSelectionFunctions(unittest.TestCase):

    def test__boolean_selection__type_Q__case_1(self): 
        ival0 = True  
        req_val0 = 0.5 
        res_val0 = 0.5 

        ival01 = False 

        b0 = boolean_selection__type_B1(ival0,req_val0,res_val0)
        b01 = boolean_selection__type_B1(ival01,req_val0,res_val0)
        assert b0 == b01 == 0. 

        ival1 = True 
        req_val1 = 0.6 
        res_val1 = 0.4 

        ival11 = False 

        b1 = boolean_selection__type_B1(ival1,req_val1,res_val1)
        b11 = boolean_selection__type_B1(ival11,req_val1,res_val1)
        assert b1 == 0.2 
        assert b11 == -0.2 

        ival2 = 1.0 
        req_val2 = 0.4 
        res_val2 = 0.6 

        ival21 = 0.0  

        b1_ = boolean_selection__type_F1(ival2,req_val1,res_val1)
        b11_ = boolean_selection__type_F1(ival21,req_val1,res_val1)
        assert b1_ == 0.6 
        assert b11_ == -0.4 

        b2_ = boolean_selection__type_F1(ival2,req_val2,res_val2)
        b21_ = boolean_selection__type_F1(ival21,req_val2,res_val2)
        assert b2_ == 0.4 
        assert b21_ == -0.6 

        ival3 = 0.5 
        ival3_ = 0.75 
        b3_ = boolean_selection__type_F1(ival3,req_val2,res_val2)
        b31_ = boolean_selection__type_F1(ival3_,req_val2,res_val2)
        assert b3_ == -0.1 
        assert b31_ == 0.15 


        b4_ = boolean_selection__type_F1(ival3,req_val0,res_val0)
        b41_ = boolean_selection__type_F1(ival3_,req_val0,res_val0)
        b42_ = boolean_selection__type_F1(1.0,req_val0,res_val0)
        assert b4_ == 0. 
        assert b41_ == 0.25 
        assert b42_ == 0.5 


if __name__ == '__main__':
    unittest.main()