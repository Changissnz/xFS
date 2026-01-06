from .hte import * 
from morebs2.search_space_iterator import * 

def HTE_env_prng_assignment_function(hteb:HTEBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    hteb.hte_nav.prg = prg  
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

    f() 
    return f 

class HTEBotModeShifter: 

    def __init__(self): 
        self.ssi = HTE_env_mode_shift_function__iterator() 

    def shift_HTEBot(self,hteb:HTEBot): 
        q = self.ssi() 
        if type(q) == type(None): return None 
        hteb.set_bot_mode(q)
        hteb.clear_logs() 
        return hteb

def HTE_env_solution_fetch_function(hteb:HTEBot): 
    navigators = hteb.terminated_navigators 
    ##print("# of navigators: ",len(navigators))
    return [(n.path_log,n.success_stat) for n in navigators]
    
def HTE_env_cmp_function_type_1_(hteb,success_multiplier=-100.0): 
    ps0 = HTE_env_solution_fetch_function(hteb)
    s0 = 0 

    for p in ps0: 
        p0,p1 = p 
        s0 = s0 + (len(p0) + float(p1) * success_multiplier) 
    return s0 

def HTE_env_cmp_function_type_2_(hteb,num_isos,success_multiplier=-100.0): 
    assert num_isos > 0 
    ps0 = HTE_env_solution_fetch_function(hteb)
    s0 = 0 

    part_size = len(ps0) / (num_isos + 1) 
    assert int(part_size) == part_size 

    q = [] 
    for x in range(num_isos + 1): 
        q.append(HTE_env_cmp_function_type_1_(hteb,success_multiplier)) 
    
    d = 0 
    for i in range(len(q)): 
        d += q[i+1] - q[i] 
    return d 

def HTE_env_cmp_solution(function_type,num_isos=None,success_multiplier= -100.0): 
    assert function_type in {1,2} 
    if function_type == 1: 
        assert type(num_isos) == type(None) 
    else: 
        assert type(num_isos) == int and num_isos > 1 
    assert success_multiplier < 0 

    def f(hteb:HTEBot,hteb1:HTEBot):
        s0,s1 = None,None 

        if function_type == 1: 
            s0 = HTE_env_cmp_function_type_1_(hteb,success_multiplier=-100.0)
            s1 = HTE_env_cmp_function_type_1_(hteb1,success_multiplier=-100.0)
        else: 
            s0 = HTE_env_cmp_function_type_2_(hteb,num_isos,success_multiplier=-100.0)
            s1 = HTE_env_cmp_function_type_2_(hteb1,num_isos,success_multiplier=-100.0)        
        return s0 <= s1 

    return f 

def HTE_env_run_(num_navigators=100,num_iso_surfaces=1):

    def f(hteb:HTEBot): 
        for _ in range(num_navigators):  
            hteb.run_navigator() 
            hteb.reproduce_terminated_navigator() 
        
        for _ in range(num_iso_surfaces): 
            hteb.reproduce_surface(False)  
            for i in range(num_navigators):  
                hteb.run_navigator() 
                hteb.reproduce_terminated_navigator() 
        return 

    return f 

