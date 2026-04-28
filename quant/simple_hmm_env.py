from .hmm_agent import * 

"""
Simple HMM environment, consisting of two agents, an offender and defender operating 
on a network. 
"""
class SimpleHMMEnv__TwoAgents: 

    def __init__(self,offendor:HMMBasedOffendor,defender:HMMBasedDefender,open_info_mode:bool):
        assert type(offendor) == HMMBasedOffendor
        assert type(defender) == HMMBasedDefender
        assert type(open_info_mode) == bool 

        self.offendor = offendor 
        self.defender = defender 

    def __next__(self):
        action,hidden_state = next(self.offendor)
        action2,hidden_state2 = self.defender.predict_next_offense(None,None) 

    @staticmethod 
    def generate_instance(num_hidden,num_observed,offendor_prg,defender_prg,\
        initial_offendor_hidden_state,offendor_lcg_delta_pattern_type,offendor_lcgv_range,open_info_mode=False): 

        T,B,hidden,observed = generate_HMM_tables__basic(num_hidden,num_observed,offendor_prg)

        offendor = HMMBasedOffendor(T,B,offendor_prg,initial_offendor_hidden_state,\
            offendor_lcg_delta_pattern_type,offendor_lcgv_range)

        defender = HMMBasedDefender(T,B,defender_prg) 

        return SimpleHMMEnv__TwoAgents(offendor,defender,open_info_mode)  