from .rnb_ext import * 

# NOTE: planned only for <RNBot> at this time. 
"""
Searches for the best decision sequence an agent can take in a simulation environment. 
Pattern of search is 
    for every PRNG G_i in `prng_seq`, 
        use G_i for every simulation mode configuration C_j (as given by `sim_mode_shift_function`), 
        producing agent decision sequence S_k (`simsol_fetch_function` retrieves this from `sim_env`)
    Determine the best (G_i,C_j,S_k) triplet from the `simsol_cmp_function`, a function that compares 
    any two decision sequences S_n,S_m. 
"""
class SimulationSolutionSearch:
    
    # CAUTION: no error-checking of parameters 
    def __init__(self,sim_env,sim_env_run_function,prng_seq,\
        sim_env_prng_assignment_function,sim_mode_shift_function,\
        simsol_fetch_function,simsol_cmp_function): 

        self.sim_env = sim_env 
        # copy of sim_env for mode shift
        self.sim_env2 = deepcopy(self.sim_env) 
        self.sim_env_run_function = sim_env_run_function
        self.prng_seq = prng_seq 
        self.sim_env_prng_assignment_function = sim_env_prng_assignment_function
        self.sim_mode_shift_function = sim_mode_shift_function
        self.simsol_fetch_function = simsol_fetch_function
        self.simsol_cmp_function = simsol_cmp_function

        self.active_prng = self.prng_seq.pop(0) 

        self.best = [None,None,None] 
        self.fin_stat = False 
        return  

    def process_one(self): 
        if self.fin_stat: return 

        if type(self.active_prng) == type(None): 
            self.fin_stat = True 
            return 

        prng = deepcopy(self.active_prng)

        self.sim_env_prng_assignment_function(self.sim_env2,prng) 

        G = self.active_prng 
        C_ = deepcopy(self.sim_env2) 
        self.sim_env_run_function(self.sim_env2)
        C = deepcopy(self.sim_env2) 
        S = self.simsol_fetch_function(self.sim_env2)

        if type(self.best[0]) == type(None): 
            self.best = [G,C,S] 
        else: 
            stat = self.simsol_cmp_function(C,self.best[1]) 
            if stat: 
                self.best = [G,C,S] 
        
        # shift to the next environment config 
        C_ = self.sim_mode_shift_function(C_)

        # case: no more config, switch prngs 
        if type(C_) == type(None): 
            self.active_prng = None 
            if len(self.prng_seq) > 0:
                self.active_prng = self.prng_seq.pop(0) 

            # reset to original sim_env 
            self.sim_env2 = deepcopy(self.sim_env)
            return 

        self.sim_env2 = C_ 
