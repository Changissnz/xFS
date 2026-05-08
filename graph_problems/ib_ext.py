from .ib import * 
from quant.levenschtein import * 

def IB_env_prng_assignment_function(ibot:IntrospectionBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    ibot.set_prg(prg) 
    return

def IB_env_mode_shift_function(ibot:IntrospectionBot): 
    return None 

def IB_env_solution_fetch_function(ibot:IntrospectionBot): 
    return ibot.ilog,ibot.rlog 

"""
pathsize difference + (node,cycle output) sequence difference 
"""
def IB_env_solution_score(ibot:IntrospectionBot): 
    I,R = IB_env_solution_fetch_function(ibot) 

    path_size0 = sum([len(v) for v in I[1].values()]) 
    path_size1 = sum([len(v) for v in R[1].values()]) 
    D0 = abs(path_size0 - path_size1) 

    L = max([len(I[0]),len(R[0])]) 
    for i in range(L): 
        ii = I[0][i] 
        rr = R[0][i]
        D = contiguous_cyclical_difference_(ii,rr,diff_type="bool")
        D0 += D 
    return D0

def IB_env_cmp_solution(ibot1:IntrospectionBot,ibot2:IntrospectionBot): 

    b0 = IB_env_solution_score(ibot1)
    b1 = IB_env_solution_score(ibot2)

    print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
    return b0 < b1 

def IB_env_run(ibot:IntrospectionBot):
    ibot.run(is_ref=False)