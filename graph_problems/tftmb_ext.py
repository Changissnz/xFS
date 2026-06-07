from .tftmb import * 

def TFTMB_env_prng_assignment_function(tfbot:TwoFacesThreeMotivesBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    tfbot.set_prg(0,prg)
    return

def TFTMB_env_mode_shift_function(tfbot:TwoFacesThreeMotivesBot): 
    return None 

def TFTMB_env_solution_fetch_function(tfbot:TwoFacesThreeMotivesBot): 
    return tfbot.scores()

"""
score of agent 0 
"""
def TFTMB_env_score_function_type_1(tfbot:TwoFacesThreeMotivesBot): 
    S = TFTMB_env_solution_fetch_function(tfbot) 
    return S[0][0] 

def TFTMB_env_score_function_type_2(tfbot:TwoFacesThreeMotivesBot): 
    S = TFTMB_env_solution_fetch_function(tfbot) 
    d = S[0][0] 
    d1 = S[1][0] 
    d2 = S[2][0] 
    return (d - d1) + (d - d2)

"""
maximize score 
"""
def TFTMB_env_cmp_solution_(ftype:int): 

    assert ftype in {1,2} 

    def f(tfbot1:TwoFacesThreeMotivesBot,tfbot2:TwoFacesThreeMotivesBot): 

        if ftype == 1: 
            Q = TFTMB_env_score_function_type_1
        else: 
            Q = TFTMB_env_score_function_type_2

        s1 = Q(tfbot1) 
        s2 = Q(tfbot2) 

        print("best {} now {}".format(s2,s1)) 
        return s1 > s2 
    
    return f 

def TFTMB_env_run_(num_iter:int): 

    def f(tfbot:TwoFacesThreeMotivesBot): 
        for _ in range(num_iter): 
            next(tfbot)  

    return f 