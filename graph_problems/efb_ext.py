from .efb import * 

def EFB_env_prng_assignment_function(efbot:EndsFixatedBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    efbot.set_prg(prg)  
    return

def EFB_env_mode_shift_function_(pr_vec=[(0.5,0.)]):  

    for x in pr_vec: 
        assert len(x) == 2 
        assert 0. <= x[0] <= 1. 
        assert 0. <= x[1] <= 1. 

    I = 0 
    def f(efbot:EndsFixatedBot): 
        nonlocal I 
        if I >= len(pr_vec): 
            I = 0 
            return None 
        
        x = pr_vec[I]
        print("X: ",x)
        efbot.dipn.set_backtrack_pr(x[0],x[1]) 
        I += 1 
        return efbot 

    return f 

"""
score is 
    number of rounds where offendor and defender moves are different. 
"""
def EFB_env_solution_fetch_function(efbot:EndsFixatedBot): 
    return (efbot.dipn.fin_stat,efbot.dipn.total_expense)

"""
score is 
    total expense from bot 
"""
def EFB_env_cmp_solution__type_1(efbot1:EndsFixatedBot,efbot2:EndsFixatedBot): 

    s0 = EFB_env_solution_fetch_function(efbot1)
    s1 = EFB_env_solution_fetch_function(efbot2) 
    print("best {} now {}".format(s1,s0)) 
    return s0[1] <= s1[1] 

def EFB_env_score_function__type_2(efbot:EndsFixatedBot): 
    s0 = EFB_env_solution_fetch_function(efbot)
    return int(s0[0]) * s0[1] 

"""
score is 
    (total expense from bot) * bool(finished)

min. objective function, except for 0 [implies bot did not finish -> failed]
"""
def EFB_env_cmp_solution__type_2(efbot1:EndsFixatedBot,efbot2:EndsFixatedBot): 

    S0 = EFB_env_score_function__type_2(efbot1)
    S1 = EFB_env_score_function__type_2(efbot2) 
    print("best {} now {}".format(S1,S0)) 

    # case: both did not finish, go with older  
    if S0 == S1 == 0: 
        return False 
    
    if S0 == 0: 
        return False  

    if S1 == 0: 
        return True  

    return S0 <= S1 

"""
"""
def EFB_env_cmp_solution_(cmp_type:int): 

    assert cmp_type in {1,2} 

    if cmp_type == 1: 
        return EFB_env_cmp_solution__type_1
    return EFB_env_cmp_solution__type_2

def EFB_env_run_(num_iter:int): 

    def f(efbot:EndsFixatedBot): 
        while efbot.c < num_iter and not efbot.dipn.fin_stat:  
            next(efbot)

    return f 