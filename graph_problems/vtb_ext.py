from .vtb import * 

def VTB_env_prng_assignment_function(vbot:VTBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    vbot.set_prg(prg,False) 
    return

def VTB_env_mode_shift_function(vbot:VTBot): 
    return None 

"""
score is, over the course of arbitrary n timestamps, 

    (cumulative euclidean distance  
    between target vector and tracking  
    vectors) 
    + 
    (cumulative balance of tracking vectors) 
"""
def VTB_env_solution_fetch_function(vbot:VTBot): 

    s1 = vbot.euclidean_difference
    s2 = vbot.mt_group.cumulative_balance

    return s1 + s2 

"""
maximal score for autonomous agent 
"""
def VTB_env_cmp_solution(vbot1:VTBot,vbot2:VTBot): 
    
    s1 = VTB_env_solution_fetch_function(vbot1)
    s2 = VTB_env_solution_fetch_function(vbot2) 
    print("now {}\nbest {}".format(round(s1,5),round(s2,5))) 
    return s1 <= s2
 
def VTB_env_run_(num_iter:int): 

    def f(vbot:VTBot): 
        assert type(vbot) == VTBot
        while vbot.timestamp < num_iter:  
            next(vbot)

    return f 