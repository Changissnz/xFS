'''
NOTE: requirements are positive, restrictions are negative 
'''
from types import MethodType,FunctionType

#------------------------------------------ weight functions for boolean choice of rule. 

def selection_rule_parameter_assertion(input_val,requirement_value,restriction_value,is_bool_type:bool): 
    assert type(is_bool_type) == bool 

    if is_bool_type: 
        assert type(input_val) == bool 
    else: 
        assert 0. <= input_val <= 1.

    assert requirement_value + restriction_value == 1.0 
    assert min([requirement_value,restriction_value]) >= 0. 
    return

"""
the "choice" selection 

return: 
- difference b/t weights of choice and anti-choice
"""
def boolean_selection__type_B1(input_val,requirement_value,restriction_value,rounding_depth=5):  
    selection_rule_parameter_assertion(input_val,requirement_value,\
        restriction_value,is_bool_type=True) 

    if input_val: 
        return round(requirement_value - restriction_value,rounding_depth)
    return round(restriction_value - requirement_value,rounding_depth) 

"""
the "predominant" selection 

return: 
- float, 
  F = predominant element (req XOR res) 
  + non-predominant if `input_val` equals predominant element 
  - non-predominant otherwise. 

"""
def boolean_selection__type_B2(input_val,requirement_value,restriction_value,rounding_depth=5): 
    selection_rule_parameter_assertion(input_val,requirement_value,\
        restriction_value,is_bool_type=True) 

    # case: req == res 
    if requirement_value == restriction_value: 
        return 0.0 

    R = [restriction_value,requirement_value] 
    dindex = np.argmax(R) 

    predom = R[dindex]
    nondom = R[(dindex + 1) % 2] 

    if int(input_val) == dindex: 
        return round(predom + nondom,rounding_depth)
    return round(predom - nondom,rounding_depth)

"""
the "choice" selection: weighted difference 
"""
def boolean_selection__type_F1(input_val,requirement_value,restriction_value,rounding_depth=5): 
    selection_rule_parameter_assertion(input_val,requirement_value,\
        restriction_value,is_bool_type=False) 

    x = (input_val * requirement_value) - ((1.0 - input_val) * restriction_value) 
    return round(x,rounding_depth)

"""
the "predominant" selection : weighted difference 
"""
def boolean_selection__type_F2(input_val,requirement_value,restriction_value,rounding_depth=5): 
    selection_rule_parameter_assertion(input_val,requirement_value,\
        restriction_value,is_bool_type=False) 

    x = None 
    if requirement_value > restriction_value: 
        neg = 1.0 - input_val
        x = requirement_value - (restriction_value * neg) 
    elif requirement_value < restriction_value: 
        pos = input_val
        x = restriction_value - (requirement_value * pos) 
    else: 
        x = 0. 
    return round(x,rounding_depth)

#----------------------------------------- effect functions for float output from boolean choice 

"""
echo choice 
"""
def boolean_choice_effect__type_1(output_value): 
    return True 

"""
?is predominant? choice 
"""
def boolean_choice_effect__type_2(output_value):
    maximum = 1.0 if output_value >= 0. else -1.
    anti = maximum - output_value
    return abs(output_value) >= abs(anti)

#--------------------------------------------------------------------------------------------------

"""
re(Q)uirement + re(S)triction selection rule. 

A decision structure that determines if agent input value satisfies rules to be of or do `label`, 
given two non-negative floats `requirement_value` (positive) and `restriction_value` (negative) 
that add up to 1.0. 

Decision consists of 2 layers: 
- layer 1: degree for label 
    pro: >= 0.
    con: < 0. 
- layer 2: boolean for `pro` XOR `con`. 
"""
class QSSelectionRule: 

    def __init__(self,label,requirement_value,restriction_value,selection_value_function,\
        value_effect_function):  

        assert type(selection_value_function) in {MethodType,FunctionType}
        assert type(value_effect_function) in {MethodType,FunctionType}
 
        self.label = label 
        self.req_val = requirement_value
        self.res_val = restriction_value
        self.sel_val_function = selection_value_function
        self.val_effect_function = value_effect_function
        return 

    """
    return: 
    - degree for label, ?accepted? 
    """
    def output(self,input_val): 
        assert type(input_val) in {bool,float} 
        if type(input_val) == float: assert 0 <= input_val <= 1

        x = self.sel_val_function(input_val,self.req_val,self.res_val) 
        return x,self.val_effect_function(x) 

"""
A decision structure that associates one `label` with n >= 0 `antilabels`. 
Agent input value determines each antilabel's degree of exclusion and whether 
the boolean from that degree bears effect (a boolean). 

Decision structure is an XOR-extended relative of <QSSelectionRule>. 
"""
class QSSelectionExclusionRule: 

    def __init__(self,label,requirement_value,antilabel_map,selection_value_function,\
        value_effect_function): 
        assert type(antilabel_map) == dict
        assert 0. <= requirement_value <= 1. 
        assert type(selection_value_function) in {MethodType,FunctionType}
        assert type(value_effect_function) in {MethodType,FunctionType}

        self.label = label 
        self.req_val = requirement_value
        self.antilabel_map = antilabel_map

        self.sel_val_function = selection_value_function
        self.val_effect_function = value_effect_function
        return 

    """
    return: 
    - dict, antilabel -> (positive degree for antilabel exclusion,?excluded?) 
    """
    def output(self,input_val):
        D = dict() 
        for k,v in self.antilabel_map.items(): 
            s = self.sel_val_function(input_val,v,self.req_val) 
            b = self.val_effect_function(s) 
            D[k] = (s,b) 
        return D