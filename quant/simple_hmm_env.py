from .hmm_agent import * 

"""
Simple HMM environment, consisting of two agents, an offender and defender operating 
on a network. 
"""
class SimpleHMMEnv__TwoAgents: 

    def __init__(self,offendor:HMMBasedOffendor,defender:HMMBasedDefender):
        assert type(offendor) == HMMBasedOffendor
        assert type(defender) == HMMBasedDefender

        self.offendor = offendor 
        self.defender = defender 

    @staticmethod 
    def generate_instance(num_hidden,num_observed,offendor_prg,defender_prg,\
        initial_offendor_hidden_state,offendor_lcg_delta_pattern_type,offendor_lcgv_range): 

        T,B,hidden,observed = generate_HMM_tables__basic(num_hidden,num_observed,offendor_prg)

        offendor = HMMBasedOffendor(T,B,offendor_prg,initial_offendor_hidden_state,\
            offendor_lcg_delta_pattern_type,offendor_lcgv_range)

        defender = HMMBasedDefender(T,B,defender_prg) 

        return SimpleHMMEnv__TwoAgents(offendor,defender) 