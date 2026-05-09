from .ib import * 
from quant.levenschtein import * 

def IB_env_prng_assignment_function(ibot:IntrospectionBot,prg):
    assert type(prg) in {MethodType,FunctionType} 
    ibot.set_prg(prg) 
    return

def IB_env_mode_shift_function(ibot:IntrospectionBot): 
    return None 

def IB_env_solution_fetch_function(ibot:IntrospectionBot): 
    return ibot.ilog,ibot.rlog 

def IB_node_cycle_output_difference(ibot:IntrospectionBot): 
    I,R = IB_env_solution_fetch_function(ibot) 

    L = max([len(I[0]),len(R[0])]) 
    d = 0 
    for i in range(L): 
        ii = I[0][i] 
        rr = R[0][i]
        D = contiguous_cyclical_difference_(ii,rr,diff_type="bool")
        d += D 
    return d 

"""
pathsize difference + (node,cycle output) sequence difference 
"""
def IB_env_solution_score(ibot:IntrospectionBot): 
    I,R = IB_env_solution_fetch_function(ibot) 

    path_size0 = sum([len(v) for v in I[1].values()]) 
    path_size1 = sum([len(v) for v in R[1].values()]) 
    D0 = abs(path_size0 - path_size1) 

    return D0 + IB_node_cycle_output_difference(ibot)

def IB_env_solution_score__type_2(ibot1:IntrospectionBot):

    I,R = IB_env_solution_fetch_function(ibot1) 

    K = sorted(set(I[1].keys()) | set(R[1].keys())) 
    
    ipaths = [I[1][k] if k in I[1] else [] for k in K] 
    rpaths = [R[1][k] if k in R[1] else [] for k in K] 

    D0 = pairwise_shortest_paths_sequence_difference(ipaths,rpaths) 
    return D0 + IB_node_cycle_output_difference(ibot1)

def IB_env_cmp_solution_(F): 
    assert F in {IB_env_solution_score,IB_env_solution_score__type_2}

    def f(ibot1:IntrospectionBot,ibot2:IntrospectionBot): 

        b0 = F(ibot1)
        b1 = F(ibot2)

        print("now {}\nbest {}".format(round(b0,5),round(b1,5))) 
        return b0 < b1 

    return f 

def IB_env_run(ibot:IntrospectionBot):
    ibot.run(is_ref=False)