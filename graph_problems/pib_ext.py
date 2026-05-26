from .pib import * 

def PIB_env_prng_assignment_function(pibot:PIBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    pibot.set_prg(prg,"defender") 
    return

def PIB_env_mode_shift_function(pibot:PIBot): 
    return None 

"""
score is 
    number of rounds where offendor and defender moves are different. 
"""
def PIB_env_solution_fetch_function(pibot:PIBot): 
    return pibot.diff

"""
maximal score for autonomous agent 
"""
def PIB_env_cmp_solution(pibot1:PIBot,pibot2:PIBot): 

    s0 = PIB_env_solution_fetch_function(pibot1)
    s1 = PIB_env_solution_fetch_function(pibot2) 
    print("best {} now {}".format(s1,s0)) 
    return s0 <= s1  


def PIB_env_run_(num_iter:int): 

    def f(pibot:PIBot): 
        while pibot.c < num_iter:  
            next(pibot)

    return f 