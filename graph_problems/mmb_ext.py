from .mmb import * 

def MMB_env_prng_assignment_function(mbot:MiddleManBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    mbot.set_prg(prg,None,for_buying_agent=True)
    return

def MMB_env_mode_shift_function(mbot:MiddleManBot): 
    return None 

"""
score is cumulative expenses of buying agent 
    mm.buying_agent.cumulative_expenses
"""
def MMB_env_solution_fetch_function(mbot:MiddleManBot): 
    return mbot.buying_agent.cumulative_expenses

"""
maximal score for autonomous agent 
"""
def MMB_env_cmp_solution(mbot1:MiddleManBot,mbot2:MiddleManBot): 
    
    s1 = MMB_env_solution_fetch_function(mbot1)
    s2 = MMB_env_solution_fetch_function(mbot2) 
    print("now {}\nbest {}".format(round(s1,5),round(s2,5))) 
    return s1 <= s2
 
def MMB_env_run_(num_iter:int): 

    def f(mbot:MiddleManBot): 
        while mbot.num_transactions < num_iter:  
            next(mbot)

    return f 