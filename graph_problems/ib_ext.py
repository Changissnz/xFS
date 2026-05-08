from .ib import * 

def IB_env_prng_assignment_function(ibot:IntrospectionBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    mkbot.assign_prng_to_antimob(prg)
    return

def IB_env_mode_shift_function(ibot:IntrospectionBot): 
    return None 

def IB_env_solution_fetch_function(ibot:IntrospectionBot): 
    return ibot.ilog,ibot.rlog 

"""
pathsize difference + (node,cycle output) sequence difference 
"""
def IB_env_solution_score_type(ibot:IntrospectionBot): 
    I,R = IB_env_solution_fetch_function(ibot) 

    path_size0 = sum([len(v) for v in I[1].values()]) 
    path_size1 = sum([len(v) for v in R[1].values()]) 
    D0 = abs(path_size0 - path_size1) 

    D = contiguous_cyclical_difference_(I[0],R[0],diff_type="bool")
    return D0 + D

def IB_env_cmp_solution(verbose=True): 

    def f(ibot1:IntrospectionBot,ibot2:IntrospectionBot): 
        b0 = IB_env_solution_score(ibot1)
        b1 = IB_env_solution_score(ibot2)

        if verbose: 
            print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
        return b0 < b1 
    return f 

def IB_env_run(ibot:IntrospectionBot):
    ibot.run(is_ref=False)