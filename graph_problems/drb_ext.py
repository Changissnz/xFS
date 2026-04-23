from .drb import * 

def DRB_env_prng_assignment_function(drbot:DualRoleBot,prg):
    drbot.set_prg(prg,for_dual_agent=True) 
    return

def DRB_env_mode_shift_function(drbot:DualRoleBot): 
    return None 

def DRB_env_solution_fetch_function(drbot:DualRoleBot): 

    s0 = drbot.cost_record.third_party
    s1 = drbot.cost_record.independent
    return s0 + s1  

def DRB_env_cmp_solution(drbot1:DualRoleBot,drbot2:DualRoleBot):  

    b0 = DRB_env_solution_fetch_function(drbot1)
    b1 = DRB_env_solution_fetch_function(drbot2) 

    print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
    return b0 <= b1

def DRB_env_run(drbot:DualRoleBot):

    while not drbot.fin_stat: 
        next(drbot)   