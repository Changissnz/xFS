from .hte import * 

def HTE_env_prng_assignment_function(hteb:HTEBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    hte.hte_nav.prg = prg  
    return

'''
Four mode classes: 
- navigator_remembers_past_encounters (size 2)
- navigator_uses_isomorphic_prediction (size 2)
- memory_less navigator (size 2)
- contra_risk (size 11) 
''' 
def HTE_env_mode_shift_function__iterator(): 

    bounds = np.array([[0,2],\
                    [0,2],\
                    [0,2],\
                    [0,1.1]])

    start_point = np.array([0,0,0,0]) 
    column_order = [0,1,2,3] 
    ssi_hop = np.array([2,2,2,11] )
    cycle_on = False 
    cycle_is = 0 

    ssi = SearchSpaceIterator(bounds, start_point, column_order, SSIHop = ssi_hop,\
        cycleOn = cycle_on, cycleIs = cycle_is)

    def f(): 
        if ssi.finished(): 
            return None 
        return next(ssi) 

    return f 

class HTEBotModeShifter: 

    def __init__(self): 
        self.ssi = HTE_env_mode_shift_function__iterator() 

    def shift_HTEBot(self,hteb:HTEBot): 
        q = next(self.ssi) 
        if type(q) == type(None): return None 
        hteb.set_bot_mode(q)
        return hteb

def HTE_env_solution_fetch_function(hteb:HTEBot,num_navigators):  
    navigators = hteb.terminated_navigators[-num_navigators:] 
    return [(n.path_log,n.success_stat) for n in navigators]

def HTE_env_cmp_solution__type_1(num_navigators=100,success_multiplier= -100.0): 

    assert success_multiplier < 0 

    def f(hteb:HTEBot,hteb1:HTEBot):
        ps0 = HTE_env_solution_fetch_function(hteb,num_navigators) 
        ps1 = HTE_env_solution_fetch_function(hteb1,num_navigators) 

        s0,s1 = 0,0
        for p,q in zip(ps0,ps1): 
            p0,p1 = p 
            s0 = s0 + (len(p0) + float(p1) * success_multiplier) 

            q0,q1 = q 
            s1 = s1 + (len(q0) + float(q1) * success_multiplier) 
        
        return s0 <= s1 

    return f 

def HTE_env_run(hteb:HTEBot,num_navigators=100):
    for i in range(num_navigators):  
        hteb.run_navigator() 
        hteb.reproduce_terminated_navigator() 
    
    hteb.reproduce_surface() 
    for i in range(num_navigators):  
        hteb.run_navigator() 
        hteb.reproduce_terminated_navigator() 

