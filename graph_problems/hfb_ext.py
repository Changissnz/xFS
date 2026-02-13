from .hfb import * 

def HFB_env_prng_assignment_function(hfbot:HomoFrameBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    hfbot.set_prgs_for_agents(prg)
    return

def HFB_env_mode_shift_function(hfbot:HomoFrameBot): 
    return None 

def HFB_env_solution_fetch_function(hfbot:HomoFrameBot): 
    return hfbot.timestamp 

def HFB_env_solution_score(hfbot:HomoFrameBot): 
    return HFB_env_solution_fetch_function(hfbot) 

"""
maximal score for autonomous agent 
"""
def HFB_env_cmp_solution(hfbot1:HomoFrameBot,hfbot2:HomoFrameBot,verbose=True): 
    s0 = HFB_env_solution_score(hfbot1) 
    s1 = HFB_env_solution_score(hfbot2) 

    if verbose: 
        print("now {}\nbest {}".format(round(s0,5),round(s1,5))) 

    return s0 > s1 
   
def HFB_env_run(hfbot:HomoFrameBot): 
    while not hfbot.fin_stat: 
        next(hfbot)