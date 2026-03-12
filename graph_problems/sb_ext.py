from .sb import * 

def SB_env_prng_assignment_function(sbot:StrangleBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    sbot.set_prng_for_strangler(prg)
    return

def SB_env_mode_shift_function(sbot:StrangleBot): 
    return None 

"""
score is 
    W(currently held nodes) + leftover energy 
"""
def SB_env_solution_fetch_function__type_1(sbot:StrangleBot): 

    score0 = sbot.strangler.score(sbot.node_weights)
    leftover_energy = 0 if sbot.strangler.energy <= 0. else \
        sbot.strangler.energy 
    return score0 + leftover_energy 

"""
score is 
    max  (W(held nodes H_)) + leftover energy 
  H_ in H 
"""
def SB_env_solution_fetch_function__type_2(sbot:StrangleBot): 

    score0 = sbot.strangler.highest_score
    leftover_energy = 0 if sbot.strangler.energy <= 0. else \
        sbot.strangler.energy 
    return score0 + leftover_energy 

"""
score is 
    1 if strangler wins, 
    0 otherwise. 
"""
def SB_env_solution_fetch_function__type_3(sbot:StrangleBot): 
    return int(sbot.win_stat == "strangler") 


"""
maximal score for autonomous agent 
"""
def SB_env_cmp_solution_(score_function): 
    assert score_function in {SB_env_solution_fetch_function__type_1,\
        SB_env_solution_fetch_function__type_2,\
        SB_env_solution_fetch_function__type_3}
    
    def f(sbot1:StrangleBot,sbot2:StrangleBot): 
        s1 = score_function(sbot1)
        s2 = score_function(sbot2) 
        print("now {}\nbest {}".format(round(s1,5),round(s2,5))) 
        return s1 >= s2
    
    return f 

 
def SB_env_run_(num_iter:int): 

    def f(sbot:StrangleBot): 
        while not sbot.fin_stat and sbot.timestamp < num_iter:  
            next(sbot)

    return f 

