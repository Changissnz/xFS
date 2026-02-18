from .mkb import * 

def MKB_env_prng_assignment_function(mkbot:MKBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    mkbot.assign_prng_to_antimob(prg)
    return

def MKB_env_mode_shift_function(mkbot:MKBot): 
    return None 

def MKB_env_solution_fetch_function_(neg_to_zero:bool=True): 
    
    def f(mkbot:MKBot): 
        s,b = mkbot.agent_scores(neg_to_zero)
        return s,b 
    
    return f

"""
anti-mob score - SUM([mob agent scores])
"""
def MKB_env_solution_score_(neg_to_zero:bool=True):
    
    def f(mkbot:MKBot,verbose=False):  
        s,b = MKB_env_solution_fetch_function_(neg_to_zero)(mkbot)
        bsum = sum(list(b.values()))
        return s - bsum

    return f 

def MKB_env_cmp_solution_(neg_to_zero:bool=True,verbose=True): 

    def f(mkbot1:MKBot,mkbot2:MKBot): 
        b0 = MKB_env_solution_score_(neg_to_zero)(mkbot1,verbose)
        b1 = MKB_env_solution_score_(neg_to_zero)(mkbot2,verbose) 

        if verbose: 
            print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
        return b0 > b1 
    return f 

def MKB_env_run(mkbot):

    while not mkbot.fin_stat: 
        next(mkbot)
