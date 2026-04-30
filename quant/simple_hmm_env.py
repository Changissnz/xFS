from .hmm_agent import * 
from morebs2.numerical_generator import merge_two_prgs

SIMPLE_HMM_ENVIRONMENT_INFO_MODES = {"perfect-full","perfect-partial","predictive","stochastic"} 

"""
logging of offendor hidden + observed state frequency and 
corresponding defender correct hidden + observed state frequency. 

Used by class<SimpleHMMEnv__TwoAgents>. 
"""
class HMMLog__TwoAgents: 

    def __init__(self): 
        # perspective: defender         
        self.correct_observed_state_ctr = Counter() 
        self.correct_hidden_state_ctr = Counter() 

        # perspective: offendor 
        self.observed_state_ctr = Counter() 
        self.hidden_state_ctr =  Counter() 

    def __str__(self): 

        keys0 = sorted(self.hidden_state_ctr.keys())

        S = "HIDDEN\n" 
        for k in keys0: 
            q = "*\tstate {}, offendor frequency {}, defense frequency {}\n".format(\
                k,self.hidden_state_ctr[k],self.correct_hidden_state_ctr[k]) 
            S += q 
        S += "\n"
        S += "OBSERVED\n"

        keys1 = sorted(self.observed_state_ctr.keys())
        for k in keys1: 
            q = "*\tstate {}, offendor frequency {}, defense frequency {}\n".format(\
                k,self.observed_state_ctr[k],self.correct_observed_state_ctr[k]) 
            S += q 

        S += "\n"
        return S 

    def update(self,offendor_action,offendor_hidden,\
        defender_action,defender_hidden): 

        self.observed_state_ctr[offendor_action] += 1 
        self.hidden_state_ctr[offendor_hidden] += 1 

        stat0 = int(offendor_action == defender_action) 
        stat1 = int(offendor_hidden == defender_hidden) 

        self.correct_observed_state_ctr[offendor_action] += stat0 
        self.correct_hidden_state_ctr[offendor_hidden] += stat1 
        return


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

        self.hmm_log = HMMLog__TwoAgents() 

    def __next__(self):

        action,hidden_state = next(self.offendor)
        action2,hidden_state2 = self.defender_move() 

        d = self.offendor.prng_outputs[-1] 

        self.defender.update_with_one_observation(action)
        self.defender.recv_offendor_PRNG_output(d) 

        stat = action != action2
        self.diff += stat 

        self.offendor.register_offensive_stat(stat)

        self.hmm_log.update(action,hidden_state,action2,hidden_state2) 
        return action,action2 

    def defender_move(self):
        known_hidden_state = self.offendor.hidden_states[-2] 

        if self.open_info_mode == "perfect-full": 
            d = self.offendor.prng_outputs[-1] 
            return self.defender.predict_next_offense(known_hidden_state,d,allow_cyclical_prediction=True) 
        elif self.open_info_mode == "perfect-partial": 
            prg_ = merge_two_prgs(self.prg,self.offendor.prg,add) 
            if prg_decimal(prg_,[0.,1.]) >= 0.5: 
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
        offendor_lcgv_range,\
        offendor_pattern_max_length=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE,\
        defender_pattern_recognizer_max_size=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE,\
        open_info_mode="predictive"):  

        T,B,hidden,observed = generate_HMM_tables__basic(num_hidden,num_observed,offendor_prg)

        offendor = HMMBasedOffendor(T,B,offendor_prg,initial_offendor_hidden_state,\
            offendor_lcg_delta_pattern_type,offendor_lcgv_range,pattern_max_length=\
            offendor_pattern_max_length)

        defender = HMMBasedDefender(T,B,defender_prg,\
            pattern_recognizer_max_size=defender_pattern_recognizer_max_size) 

        return SimpleHMMEnv__TwoAgents(offendor,defender,env_prg,open_info_mode)  