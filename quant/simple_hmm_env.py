from .hmm_agent import * 

SIMPLE_HMM_ENVIRONMENT_INFO_MODES = {"perfect-full","perfect-partial","predictive","stochastic"} 

"""
Simple HMM environment, consisting of two agents, an offender and defender operating 
on a network. 
"""
class SimpleHMMEnv__TwoAgents: 

    def __init__(self,offendor:HMMBasedOffendor,defender:HMMBasedDefender,env_prg,open_info_mode:str):
        assert type(offendor) == HMMBasedOffendor
        assert type(defender) == HMMBasedDefender
        assert type(env_prg) in {FunctionType,MethodType} 
        assert open_info_mode in SIMPLE_HMM_ENVIRONMENT_INFO_MODES 

        self.offendor = offendor 
        self.defender = defender 
        self.prg = env_prg
        self.open_info_mode = open_info_mode
        self.diff = 0 

    def __next__(self):

        action,hidden_state = next(self.offendor)
        action2,hidden_state2 = self.defender_move() 

        d = self.offendor.prng_outputs[-1] 

        self.defender.update_with_one_observation(action)
        self.defender.recv_offendor_PRNG_output(d) 
        self.diff += (action != action2) 

    def defender_move(self):
        known_hidden_state = self.offendor.hidden_states[-2] 

        if self.open_info_mode == "perfect-full": 
            d = self.offendor.prng_outputs[-1] 
            return self.defender.predict_next_offense(known_hidden_state,d,allow_cyclical_prediction=True) 
        elif self.open_info_mode == "perfect-partial": 

            if prg_decimal(self.prg,[0.,1.]) >= 0.5: 
                d = self.offendor.prng_outputs[-1] 
            else: 
                d = None 
            return self.defender.predict_next_offense(known_hidden_state,d,allow_cyclical_prediction=True) 
        elif self.open_info_mode == "predictive": 
            return self.defender.predict_next_offense(known_hidden_state,None,allow_cyclical_prediction=True) 
        else: 
            return self.defender.predict_next_offense(None,None,allow_cyclical_prediction=True) 
        return

    @staticmethod 
    def generate_instance(num_hidden,num_observed,offendor_prg,defender_prg,\
        env_prg,initial_offendor_hidden_state,offendor_lcg_delta_pattern_type,\
        offendor_lcgv_range,open_info_mode="predictive"):  

        T,B,hidden,observed = generate_HMM_tables__basic(num_hidden,num_observed,offendor_prg)

        offendor = HMMBasedOffendor(T,B,offendor_prg,initial_offendor_hidden_state,\
            offendor_lcg_delta_pattern_type,offendor_lcgv_range)

        defender = HMMBasedDefender(T,B,defender_prg) 

        return SimpleHMMEnv__TwoAgents(offendor,defender,env_prg,open_info_mode)  