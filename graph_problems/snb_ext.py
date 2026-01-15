from .snb import * 
from types import MethodType,FunctionType

# functions implemented for exactly 1 autonomous agent 

def SNB_env_prng_assignment_function(snbot:SNBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    a_idn =  snbot.t_auto 
    snbot.set_agent_prg(a_idn,prg)
    return

def SNB_env_mode_shift_function(snbot:SNBot): 
    return None 

def SNB_env_solution_fetch_function(snbot:SNBot): 

    # collect scores into map 
    m = snbot.agent_scores() 
    a_idn = snbot.t_auto 

    s = m[a_idn]
    del m[a_idn] 

    q = sorted(m.values()) 
    return s,q 

"""
maximal score for autonomous agent 
"""
def SNB_env_cmp_solution__type_1(snbot1:SNBot,snbot2:SNBot): 
    s0,s1 = SNB_env_solution_fetch_function(snbot1)
    t0,t1 = SNB_env_solution_fetch_function(snbot2) 
    return s0 > t0

"""
maximal score difference of autonomous agent with others 
"""
def SNB_env_cmp_solution__type_2(snbot1:SNBot,snbot2:SNBot):
    s0,s1 = SNB_env_solution_fetch_function(snbot1)
    t0,t1 = SNB_env_solution_fetch_function(snbot2) 

    d0 = sum([s0 - s1_ for s1_ in s1]) 
    d1 = sum([t0 - t1_ for t1_ in t1]) 
    return d0 > d1

def rank_one_in_all(one,others): 
    d0 = [(one,"a")] + [(s1_,"-") for s1_ in others]  
    d0 = sorted(d0,key=lambda x:x[0])

    r0 = None 
    for (i,d0_) in enumerate(d0): 
        if d0_[1] == "-": continue 
        r0 = i 
        break 
    return r0 

"""
highest relative ranking for autonomous agent
"""
def SNB_env_cmp_solution__type_3(snbot1:SNBot,snbot2:SNBot):
    s0,s1 = SNB_env_solution_fetch_function(snbot1)
    t0,t1 = SNB_env_solution_fetch_function(snbot2) 
    
    r0 = rank_one_in_all(s0,s1) 
    r1 = rank_one_in_all(t0,t1) 
    return r0 > r1    

def SNB_env_run_(num_iter:int): 

    def f(snbot:SNBot): 
        for _ in range(num_iter): 
            next(snbot)

    return f 

