from .ptb import * 
from morebs2.measures import zero_div 

# NOTE: 
# functions implemented for exactly 1 autonomous agent 

def PTB_env_prng_assignment_function(ptbot:PTBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    a_idn =  ptbot.auto_agent
    ptbot.set_target_prngs({a_idn:prg})
    return

def PTB_env_mode_shift_function(ptbot:PTBot): 
    return None 

def PTB_env_solution_fetch_function(ptbot:PTBot): 
    return ptbot.target_perf(ptbot.auto_agent)

"""
maximal score for autonomous agent 
"""
def PTB_env_cmp_solution(ptbot1:PTBot,ptbot2:PTBot,verbose=True): 
    t0,g0,p0 = PTB_env_solution_fetch_function(ptbot1)
    t1,g1,p1 = PTB_env_solution_fetch_function(ptbot2) 

    s0 = g0 + g0 * zero_div(t0,p0,0.0) 
    s1 = g1 + g1 * zero_div(t1,p1,0.0) 

    if verbose: 
        print("now {}\nbest {}".format(round(s0,5),round(s1,5))) 

    return s0 < s1 
   
def PTB_env_run_(num_iter:int): 

    def f(ptbot:PTBot): 
        for _ in range(num_iter): 
            next(ptbot)

    return f 

