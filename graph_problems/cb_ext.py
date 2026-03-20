from .cb import * 

def CB_env_prng_assignment_function_(agent_idn): 
    
    def f(cbot:ControverterBot,prg):
        assert type(prg) in {MethodType,FunctionType} 
        cbot.set_non_auto_agent(agent_idn,prg) 

    return f 

def CB_env_mode_shift_function(cbot:ControverterBot): 
    return None 

def CB_env_solution_fetch_function_(agent_idn): 
    
    def f(cbot:ControverterBot): 
        d = [] 
        d0 = None 

        for k,v in cbot.amap.items(): 
            if k == agent_idn: 
                d0 = v.value  
                continue 
            d.append(v.value) 
        return d0,d
    
    return f

"""
type 1: direct score (objective max) 
type 2: difference with others (objective max)
"""
def CB_env_solution_score_(agent_idn,score_type):
    assert score_type in {1,2}

    def f(cbot:ControverterBot):  
        d0,d = CB_env_solution_fetch_function_(agent_idn)(cbot)
        if score_type == 1: 
            return d0 
        return np.sum(d0 - np.array(d)) 

    return f 

def CB_env_cmp_solution_(agent_idn,score_type): 

    def f(cbot1:ControverterBot,cbot2:ControverterBot): 
        f2 = CB_env_solution_score_(agent_idn,score_type)
        s1 = f2(cbot1)
        s2 = f2(cbot2)
        print("now {}\nbest {}".format(round(s1,5),round(s2,5))) 
        return s1 > s2 

    return f 

def CB_env_run_(num_iter):

    def f(cbot:ControverterBot):
        for _ in range(num_iter): 
            next(cbot)
    
    return f 
