from .pdib import * 

def PDIB_env_prng_assignment_function(pbot:PDIBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    pbot.set_prg(prg,set_for_solver=True) 
    return

def PDIB_env_mode_shift_function(pbot:PDIBot): 
    return None 

"""
score is (# of swaps) if token graph is solved, 
        infinity otherwise. 
"""
def PDIB_env_solution_fetch_function(pbot:PDIBot): 
    return pbot.iscore_full() 

"""
minimize score 
"""
def PDIB_env_cmp_solution(pbot1:PDIBot,pbot2:PDIBot): 

    if ftype == 1: 
        Q = PDIB_env_score_function_type_1
    else: 
        Q = PDIB_env_score_function_type_2

    s1 = Q(pbot1) 
    s2 = Q(pbot2) 

    print("best {} now {}".format(s2,s1)) 
    return s1 < s2 
    return f 

def PDIB_env_run(pbot:PDIBot):
    while not pbot.fin_stat:   
        next(pbot)  
    return 