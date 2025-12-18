from .rnb import * 

# NOTE: planned only for <RNBot> at this time. 
"""
Searches for the best decision sequence an agent can take in a simulation environment. 
Pattern of search is 
    for every PRNG G in `prng_seq`, 
        use G_i for every simulation mode configuration C_j (as given by `sim_mode_shift_function`), 
        producing agent decision sequence S_k (`simsol_fetch_function` retrieves this from `sim_env`)
    Determine the best (G_i,C_j,S_k) triplet from the `simsol_cmp_function`, a function that compares 
    any two decision sequences S_n,S_m. 
"""
class SimulationSolutionSearch:
    
    def __init__(self,sim_env,prng_seq,\
        sim_env_prng_assignment_function,sim_mode_shift_function,\
        simsol_fetch_function,simsol_cmp_function): 

        return  