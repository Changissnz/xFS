from .tsb import * 
from types import MethodType,FunctionType

def TSB_env_prng_assignment_function(tsbot:TokenSwappingBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    tsbot.set_prg(prg)
    return

def TSB_env_mode_shift_function(tsbot:TokenSwappingBot): 
    return None 

"""
score is (# of swaps) if token graph is solved, 
        infinity otherwise. 
"""
def TSB_env_solution_fetch_function(tsbot:TokenSwappingBot): 

    if tsbot.fin_stat: 
        return tsbot.num_swaps() 
    return float('inf')

"""
"""
def TSB_env_cmp_solution(tsbot1:TokenSwappingBot,tsbot2:TokenSwappingBot): 
    s0 = TSB_env_solution_fetch_function(tsbot1)
    s1 = TSB_env_solution_fetch_function(tsbot2) 
    print("best {} now {}".format(s1,s0)) 
    return s0 < s1 

def TSB_env_run_(num_iter:int): 

    def f(tsbot:TokenSwappingBot): 
        for _ in range(num_iter): 
            tsbot.auto_solution_search() 

    return f 