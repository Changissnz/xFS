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
- contra_risk (size 5) 
''' 
def HTE_env_mode_shift_function__iterator(num_contra_risk=4,zero_case_head=0.0): 
    assert type(num_contra_risk) == int and num_contra_risk >= 0 

    if num_contra_risk == 0: 
        assert zero_case_head in {0,1}
        R = [zero_case_head,zero_case_head] 
        start_point = np.array([0,0,0,zero_case_head]) 
    else: 
        x = 1. / num_contra_risk 
        R = [0.,1. + x] 
        start_point = np.array([0,0,0,0]) 

    print("RR: ",R)
    bounds = np.array([[0,2],\
                    [0,2],\
                    [0,2],\
                    R])

    column_order = [0,1,2,3] 
    ssi_hop = np.array([2,2,2,num_contra_risk + 1])   
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

    def __init__(self,num_contra_risk=4,zero_case_head=0.): 
        self.ssi = HTE_env_mode_shift_function__iterator(num_contra_risk=num_contra_risk,\
            zero_case_head=zero_case_head) 

    def shift_HTEBot(self,hteb:HTEBot): 
        q = self.ssi() 
        if type(q) == type(None): return None 
        hteb.set_bot_mode(q)
        hteb.clear_logs() 
        return hteb

def HTE_env_solution_fetch_function(hteb:HTEBot,navigator_range=None):
    if type(navigator_range) == type(None):  
        navigators = hteb.terminated_navigators 
    else: 
        assert is_valid_range(navigator_range,True,False)
        n0,n1 = navigator_range[0],navigator_range[1] 
        navigators = hteb.terminated_navigators[n0:n1] 

    ##print("# of navigators: ",len(navigators))
    return [(n.path_log,n.success_stat) for n in navigators]
    
def HTE_env_cmp_function_type_1_(hteb,success_multiplier=-100.0,navigator_range=None): 
    ps0 = HTE_env_solution_fetch_function(hteb,navigator_range) 
    s0 = 0 

    for p in ps0: 
        p0,p1 = p 
        s0 = s0 + (len(p0) + float(p1) * success_multiplier) 
    return s0 

"""
measurement function of <HTEBot> navigator performance focuses on 
the differences in performances between every contiguous pair of 
navigators, respectively for two separate <HTESurfaces>, the former 
being the source for the isomorphic derivation to the latter. 

For a pair of navigators (N0,N1) with their travel records (P0,P1), 
        <(path_j,status_j) in sequence P_i>, 
function<HTE_env_cmp_function_type_1_> is used to calculate the scores  
of P0 and P1 for differences. 

Output is cumulative sum of [(n-1)=`num_isos`] differences. 
"""
def HTE_env_cmp_function_type_2_(hteb,num_isos,success_multiplier=-100.0): 
    assert num_isos > 0 
    ps0 = HTE_env_solution_fetch_function(hteb)
    s0 = 0 

    part_size = len(ps0) / (num_isos + 1) 
    assert int(part_size) == part_size 
    part_size = int(part_size)

    q = [] 
    for x in range(num_isos + 1):
        navigator_range = (x * part_size,(x + 1) * part_size)
        q.append(HTE_env_cmp_function_type_1_(\
            hteb,success_multiplier,navigator_range)) 
    
    d = 0 
    for i in range(len(q)-1): 
        d += q[i+1] - q[i] 
    return d 

"""
function_type := 1|2 
num_isos := int if `function_type` == 2 else None 
success_multiplier := negative real number. 
"""
def HTE_env_cmp_solution(function_type,num_isos=None,success_multiplier= -100.0): 
    assert function_type in {1,2} 
    if function_type == 1: 
        assert type(num_isos) == type(None) 
    else: 
        assert type(num_isos) == int and num_isos > 0 
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

