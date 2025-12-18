# file contains additional functions for <RNBot> in <SimulationSolutionSearch>. 
from .rnb import * 

def RNB_env_prng_assignment_function(rnbot:RNBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    rnbot.qstruct.prg = prg 
    return

"""
starting NFA should be NFA#1. Function shift 
is
NFA#1 -> NFA#2
NFA#2 -> None. 
"""
def RNB_env_mode_shift_function(rnbot:RNBot): 
    if rnbot.qstruct.nfa_type == 1: 
        rnbot.qstruct.nfa_type = 2 
        return rnbot 
    elif rnbot.qstruct.nfa_type == 2: 
        return None 

def RNB_env_solution_fetch_function(rnbot:RNBot): 
    return rnbot.qstruct.qsm_log

def cumulative_nonzero_sum(D): 
    S = 0 
    for v in D.values(): 
        v_ = 0 if v <= 0 else v 
        S += v_ 
    return S 

def RNB_cumulative_nonzero_RStruct_resistance(rnbot:RNBot): 
    rdict = rnbot.rstruct_node_resistances()
    return cumulative_nonzero_sum(rdict)

"""
Type #1 observes only the cumulative non-zero resistance 
of <RStruct> nodes. 

Objective: minimize 

return: 
- 0 if `rnbot1` has better solution else 1. 
"""
def RNB_env_cmp_solution__type_1(rnbot1:RNBot,rnbot2:RNBot,verbose=True): 
    S1 = RNB_cumulative_nonzero_RStruct_resistance(rnbot1)
    S2 = RNB_cumulative_nonzero_RStruct_resistance(rnbot2)
    if verbose: 
        print("best {} now {}".format(S2,S1)) 
    return S1 <= S2

"""
Type #2 observes weighted sum,  
(cumulative non-zero resistance of <RStruct> nodes) * m_0 
+ (- <QStruct>.energy if energy > 0 else 0) * m_1 

m_0,m_1 are positive scalars. 

Objective: minimize
"""
def RNB_env_cmp_solution__type_2_function(m_0:float=1.,m_1:float=1.0,verbose=True): 
    assert m_0 > 0 and m_1 > 0 

    def p(rnbot:RNBot,m): 
        E1 = -rnbot.qstruct.energy if rnbot.qstruct.energy > 0 else 0 
        return E1 * m 

    def fx(rnbot1:RNBot,rnbot2:RNBot): 
        x00 = p(rnbot1,m_0) 
        x01 = RNB_cumulative_nonzero_RStruct_resistance(rnbot1) * m_1 
        x0 = x00 + x01 

        x10 = p(rnbot2,m_0) 
        x11 = RNB_cumulative_nonzero_RStruct_resistance(rnbot2) * m_1 
        x1 = x10 + x11

        if verbose: 
            print("best {} now {}".format(x1,x0)) 

        return x0 <= x1 

    return fx

def RNB_env_run(rnbot:RNBot): 
    while not rnbot.fin_stat:
        next(rnbot) 