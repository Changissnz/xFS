from quant.simple_hmm_env import * 

"""
Probabilistic Impact Bot. 

Featuring two agents, an offendor and defender operating in opposing states on the same hidden 
Markov model. For every timestamp, offendor moves to an observed state (offending action), a 
decision based on its PRNG decimal output in percentile ranges, specified by the HMM. The defender 
responds to the offendor. Defender objective is to choose the same observed state of offendor, 
thereby providing defense to it. 

NOTE: 
Bot is geared for the vantage point of defender. The offendor operates by a more pre-defined 
automaton process. 

        *Offendor perspective* 

In mathematical terms, the offendor operates like so: 
- offendor outputs a PRNG decimal d.  
- By the offendor's current hidden state H and decimal d, offendor makes a move 
  (observed state) and transitions its hidden state, each of these two changes 
  corresponding to their respective percentile ranges specified by H and d.  

The offendor PRNG is an integer LCG. This integer LCG is variable, and the range of the 
four values of the offendor LCG can be one of the categories, "constant" or "multiple". 
Constant ranges still output LCGs that, in turn, output different sequences of integers. 
The "multiple" category multiplies the current LCG range by a float greater than 1 (by default), 
then rounds that range to the nearest integers. 

By the schematic of integer LCGs, offendor operates by a relatively simple pattern-based 
deciding mechanism, with respect to the hidden Markov model. 

        *Defender perspective* 

There are two variables important for a defender to be accurate in predicting the offendor's next 
move. 
- offendor's PRNG output 
- offendor's current hidden state. 

There are three information modes in this bot, from the vantage point of the defender. They are 
- perfect-full: (EXCLUDED) at every timestamp, variables H and d from offendor are passed to 
                defender, resulting in perfect defense. 
- perfect-partial: variable H is passed to defender. And d is passed to defender if merged PRNG, 
                from defender base PRNG and offender PRNG, outputs a decimal >= 0.5. 
- predictive: variable H is passed to defender. Variable d is not. 
- stochastic: Neither H nor d is passed to defender. 
NOTE: these information modes are assumed to be static, once the environment has been initialized. 

Defender uses a cyclical predictor, complementary to the quality of cyclical output from offendor 
LCG, in the cases where it is not given the offendor PRNG decimal output. If cyclical predictor does 
not have enough samples, the number specified in the next section (Agent update rates), to calculate 
a cycle to base its prediction on, it resorts to decimal outputs from its own PRNG. 

NOTE: Defender is given every offender PRNG decimal output AFTER the timestamp has ended. See 
      variable<HMMBasedDefender.offending_agent_prng_output> (a sequence) for more information. 
      Defender cyclical predictor chooses a float subsequence S in this PRNG output sequence that 
      is both the most common subsequence as well as the longest. Defender cycles through S 
      for predicted PRNG decimal outputs from offendor. 

        *Agent update rates*  

The variable<HMMBasedOffendor.pattern_max_length> is used by offendor to determine the timestamp 
at which it updates its operating LCG to another LCG. If there are c >= `pattern_max_length` 
moves since the last update, and the offendor's number of failures F (moves that are matched + countered 
by the defender) satisfies 
        (F / c) >= min([0.5, 2/ |# of observed states|]), 
offendor updates its LCG. 

The defendor updates its predicted cycle for offendor PRNG output, based on:
- variable<HMMBasedDefendor.pr_max_size> P0
- variable<HMMBasedDefendor.num_rounds_since_pupdate> P1. 

Defendor updates predicted cycle if P1 > 2 * P0 / 3.  

        *Main agent attributes* 
Both operate on cyclical processes, the offendor using an LCG (a PRNG that is cyclical), and the 
defender predicting offendor LCG output based on the most common and longest subsequence of float 
values it stored on offendor LCG output.
"""
class PIBot(SimpleHMMEnv__TwoAgents): 

    def __init__(self,offendor:HMMBasedOffendor,defender:HMMBasedDefender,env_prg,open_info_mode:str):
        super().__init__(offendor,defender,env_prg,open_info_mode) 
        return

    @staticmethod
    def generate_instance(num_hidden,num_observed,offendor_prg,defender_prg,\
        env_prg,initial_offendor_hidden_state,offendor_lcg_delta_pattern_type,\
        offendor_lcgv_range,\
        offendor_pattern_max_length=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE,\
        defender_pattern_recognizer_max_size=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE,\
        open_info_mode="predictive"):   

        she = SimpleHMMEnv__TwoAgents.generate_instance(num_hidden,num_observed,offendor_prg,defender_prg,\
            env_prg,initial_offendor_hidden_state,offendor_lcg_delta_pattern_type,\
            offendor_lcgv_range,offendor_pattern_max_length,defender_pattern_recognizer_max_size,\
            open_info_mode)

        return PIBot(she.offendor,she.defender,she.prg,she.open_info_mode)