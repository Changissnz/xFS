from .bkb import * 

def BKB_env_prng_assignment_function(bkbot:BKBot,prg):
    bkbot.set_LCG_prng_derivatives_for_agents(prg)
    return

def BKB_env_mode_shift_function(bkbot:BKBot): 
    return None 

def BKB_env_solution_fetch_function(bkbot:BKBot): 
    bscore = bkbot.bull.stat()
    q = [] 
    for a in bkbot.agents.values(): 
        ascore = a.stat() 
        q.append(ascore) 
    for a in bkbot.terminated_agents.values(): 
        ascore = a.stat() 
        q.append(ascore) 

    return bscore,q  

"""
NOTE: 
somewhat wonky score function 
"""
def BKB_env_solution_score_(bkbot:BKBot,verbose=False):  

    bscore,ascore = BKB_env_solution_fetch_function(bkbot)
    if verbose: 
        print("bull info")
        print("-- capture: ",bkbot.bull_cap)
        print(bscore)
        print("agent info") 
        print(ascore)
        print() 

    B = bscore[0] * bscore[1] + (bscore[0] - bscore[1]) 
    A = sum([a[0] * a[1] + (a[0] + a[1]) for a in ascore])  
    return -B + A 

#def BKB_env_cmp_solution_(active_mode_weight,verbose=True): 
def BKB_env_cmp_solution_(verbose=True): 

    def f(bkbot1:BKBot,bkbot2:BKBot): 
        b0 = BKB_env_solution_score_(bkbot1,verbose)
        b1 = BKB_env_solution_score_(bkbot2,verbose) 

        if verbose: 
            print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
        return b0 > b1 
    return f 

def BKB_env_run(bkbot):

    while not bkbot.fin_stat: 
        next(bkbot)  