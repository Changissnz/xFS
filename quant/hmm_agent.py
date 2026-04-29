from morebs2.hmm_fb import * 
from morebs2.pr2label import * 
from morebs2.matrix_methods import cr 
from morebs2.numerical_generator import prg__single_to_decimal,modulo_in_range,prg__LCG,\
    prg_decimal,prg_seqsort_ties
from morebs2.seq_repr import * 
from types import MethodType, FunctionType
from collections import deque 

HMM_OFFENDER_LCG_PATTERN_TYPES = {"constant","multiple"} 

def one_HMM_table(row_labels,col_labels,prg):  

    prg_ = prg__single_to_decimal(prg,[0.,1.])

    x0 = len(row_labels) 
    x1 = len(col_labels) 

    T = dict()
    for i in row_labels: 
        T[i] = dict() 
        # normalize every row 
        x = [] 
        for j in col_labels: 
            x.append(prg_())
        x = np.array(x) 
        denom = np.sum(x)
        x = np.round([zero_div(x_,denom,1/len(col_labels)) \
            for x_ in x],5)
        
        for j in col_labels: 
            T[i][j] = x[j] 
    return T 

def generate_HMM_tables__basic(num_hidden,num_observed,prg):  
    assert 0 < num_hidden
    assert 0 < num_observed
    assert type(prg) in {MethodType,FunctionType}

    hidden_states = [i for i in range(num_hidden)] 
    observed_states = [j for j in range(num_hidden,num_hidden + num_observed)]

    # make hidden-to-hidden table 
    T = one_HMM_table(hidden_states,hidden_states,prg)

    # make observed-to-hidden table 
    B = one_HMM_table(observed_states,hidden_states,prg)

    return T,B,hidden_states,observed_states

class SimpleCyclicalFloatPredictor: 

    def __init__(self,prg):
        assert type(prg) in {MethodType,FunctionType}

        self.prg = prg  
        self.L = None 
        
        self.cycle = [] 
        self.index = 0  

    def __next__(self): 
        
        assert type(self.index) != type(None) 
        assert len(self.cycle) > 0 

        i = self.index %  len(self.cycle)
        self.index = (self.index + 1) % len(self.cycle)
        r = self.cycle[i] 
        return r 
        
    def load_sequence(self,l):
        assert type(l) == list
        self.L = np.array(l,dtype=float)
        self.index = 0 

    """
    chooses the most frequent sequence in `self.L` that is also 
    of the greatest length. PRNG is used in the case of tie-breakers. 
    """
    def choose_sequence(self,L): 
        self.load_sequence(L) 
        m = MCSSearch(self.L,cast_type=cr,is_bfs=True) 
        m.search()

        q = m.mcs() 
        q = [(q_,len(q_)) for q_ in q] 
        q = prg_seqsort_ties(q,self.prg,lambda x:x[1]) 

        self.cycle = q[-1][0] 
        self.index = 0 

#-----------------------------------------------------------

DEFAULT_HMM_OFFENDER_LCGV_RANGE = [1.,7+1/7+1/9+1/11] 
DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE = 150 

class HMMOffendorLCGDelta: 

    def __init__(self,prg,pattern_type,lcgv_range):  
        assert pattern_type in HMM_OFFENDER_LCG_PATTERN_TYPES 
        assert type(prg) in {MethodType,FunctionType} 

        assert is_valid_range(lcgv_range,True,False) or \
            is_valid_range(lcgv_range,False,False)
        
        self.prg = prg 
        self.pattern_type = pattern_type
        self.lcgv_range = lcgv_range
        return

    def __next__(self): 

        X = [] 
        for _ in range(4): 
            x = round(modulo_in_range(self.prg(),self.lcgv_range)) 
            X.append(x) 

        c = 0 
        while X[3] == 0 and c < 10: 
            X[3] = round(modulo_in_range(self.prg(),self.lcgv_range))
            c += 1 

        assert X[3] != 0 

        P = prg__LCG(X[0],X[1],X[2],X[3])

        self.change_lcgv_range() 
        return P 

    def change_lcgv_range(self): 
        if self.pattern_type == "constant": 
            return 

        m = modulo_in_range(self.prg(),DEFAULT_HMM_OFFENDER_LCGV_RANGE) 
        m0 = self.lcgv_range[0] * m 
        m1 = self.lcgv_range[1] * m 
        self.lcgv_range = [m0,m1] 

class HMMBasedAgent: 

    def __init__(self,T,B,prg):
        self.fbward = ForwardBackward(T,B)
        self.prg = None 
        self.set_prg(prg)  
        self.current_hidden_state = None 
        self.hidden_states = [] 
        self.actions = []
        self.hidden_state_probabilities = dict()  
        return 

    def exec(self,H,x): 
        # choose next action 
        action = self.hidden_state_to_next(H,x,next_is_hidden=False)

        # transition hidden state 
        next_hidden_state = self.hidden_state_to_next(H,x,next_is_hidden=True)
        return action,next_hidden_state

    '''
    log action and current hidden state 
    ''' 
    def log_motion(self,action,hidden_state): 
        assert action in self.fbward.B
        assert hidden_state in self.fbward.hidden_states

        self.actions.append(action) 
        self.current_hidden_state = hidden_state
        self.hidden_states.append(hidden_state) 

    def set_prg(self,prg): 
        assert type(prg) in {MethodType,FunctionType} 
        self.prg = prg 

    def hidden_state_to_next(self,hidden_state,pr,next_is_hidden:bool): 
        assert type(next_is_hidden) == bool 

        if next_is_hidden:
            D = self.fbward.T 
            L = self.fbward.hidden_states
            pr_vec = [(D[hidden_state][x],x) for x in L] 
        else:
            D = self.fbward.B 
            L = sorted(self.fbward.B.keys()) 
            pr_vec = [(D[x][hidden_state],x) for x in L] 

        the_next_thing = probability_to_label(pr_vec,pr)
        return the_next_thing  

    # NOTE: the method of calculating probabilities of the hidden 
    #       states is not the same as the original forward-backward 
    #       algorithm. The indexes of the backward step are off, 
    #       since the hidden state probabilities are updated one 
    #       observation at a time. So the smoothed probabilities are 
    #       probably not the same. 
    def update_with_one_observation(self,others_action): 
        self.fbward.add_one_observation(others_action) 

        i = len(self.fbward.obs_seq) - 1 
        self.fbward.forward_at(i,record_value=True) 
        self.fbward.backward_at(i,record_value=True) 
        self.fbward.smooth_at(i,record_value=True) 
        
        q = self.fbward.pr_smoothed[-1] 

        self.hidden_state_probabilities.clear() 
        for (i,h) in enumerate(self.fbward.hidden_states): 
            self.hidden_state_probabilities[h] = q[i] 
        return 

class HMMBasedOffendor(HMMBasedAgent):

    def __init__(self,T,B,prg,initial_hidden_state,lcg_delta_pattern_type,lcgv_range,\
        pattern_max_length=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE):  

        super().__init__(T,B,prg) 

        assert initial_hidden_state in self.fbward.hidden_states
        self.current_hidden_state = initial_hidden_state

        self.lcg_loader = HMMOffendorLCGDelta(prg,lcg_delta_pattern_type,lcgv_range)
        assert pattern_max_length > 5 and type(pattern_max_length) == int 
        self.pattern_max_length = pattern_max_length

        self.lcg0 = None
        self.load_next_LCG_()  

        self.prng_outputs = [] 
        self.hidden_states.append(self.current_hidden_state) 

        self.success_vec = deque() 
        self.success_counter = Counter() 

        self.failure_upper_threshold = min([2 / len(self.fbward.T), 0.5])  
        return 

    def __next__(self): 
        # PRNG moves 
        x = prg_decimal(self.lcg0,[0.,1.]) 
        self.prng_outputs.append(x) 

        H = self.hidden_states[-1]
        action,next_hidden_state = self.exec(H,x) 

        self.log_motion(action,next_hidden_state)
        return action,next_hidden_state

    def load_next_LCG_(self):
        self.lcg0 = next(self.lcg_loader)
        return

    def register_offensive_stat(self,is_successful:bool): 
        assert type(is_successful) == bool 
        
        self.success_counter[is_successful] += 1 
        self.success_vec.append(is_successful) 

        self.update_LCG() 

    def update_LCG(self):

        while len(self.success_vec) > self.pattern_max_length: 
            q = self.success_vec.popleft() 
            self.success_counter[q] -= 1 
        
        c = self.success_counter[True] + self.success_counter[False] 
        
        # enough samples of pass/fail for possibly updating 
        if c >= self.pattern_max_length: 
            f = self.success_counter[False] / c 

            # update b/c of 'high' failure rate 
            if f >= self.failure_upper_threshold: 

                self.load_next_LCG_() 
                self.success_vec.clear() 
                self.success_counter.clear() 

"""
Defender operates with a simple pattern-based predictor. This predictor is an instance 
of <SimpleCyclicalFloatPredictor> that takes the sequence of `offending_agent_prng_output` 
as input. Predictor cyclically outputs float values from one of the most common subsequence 
S from `offending_agent_prng_output` that also happens to be one of the greatest in length. 
These float values help Defender predictor the `observed` state (Offendor action) of the 
HMM. The predictor updates S every [`pattern_recognizer_max_size` * 2 /3] rounds. 
"""
class HMMBasedDefender(HMMBasedAgent): 

    def __init__(self,T,B,prg,pattern_recognizer_max_size=DEFAULT_HMM_DEFENDER_PATTERN_RECOGNIZER_MAX_SIZE): 
        assert type(pattern_recognizer_max_size) == int
        assert pattern_recognizer_max_size >= 5 

        super().__init__(T,B,prg) 

        self.pr_max_size = pattern_recognizer_max_size

        L = self.fbward.hidden_states
        self.hidden_state_probabilities = {h:1/len(L) for h in L} 

        self.fbward.load_new_obs_seq([])
        self.offending_agent_prng_output = deque()  

        self.cyclical_predictor = SimpleCyclicalFloatPredictor(prg) 
        self.num_rounds_since_pupdate = 0  
        return

    def recv_offendor_PRNG_output(self,decimal): 
        assert 0. <= decimal <= 1. 
        self.offending_agent_prng_output.append(decimal) 

        while len(self.offending_agent_prng_output) > self.pr_max_size: 
            self.offending_agent_prng_output.popleft()

    def predict_offendor_cycle(self): 
        if len(self.offending_agent_prng_output) >= self.pr_max_size: 
            self.cyclical_predictor.choose_sequence(list(self.offending_agent_prng_output))
        return 

    def predict_next_offense(self,known_hidden_state=None,known_pr=None,\
        allow_cyclical_prediction:bool=False):

        # case: update most common PRNG cycle of offendor 
        if self.num_rounds_since_pupdate > self.pr_max_size / 3 * 2: 
            self.predict_offendor_cycle()
            self.num_rounds_since_pupdate = 0 

        hidden_state = known_hidden_state
        pr = known_pr 

        # calculate a decimal if there is no known pr provided. 
        if type(pr) == type(None): 
            if allow_cyclical_prediction: 
                try: 
                    pr = next(self.cyclical_predictor) 
                except: 
                    pass 
            
            if type(pr) == type(None): 
                pr = prg_decimal(self.prg,[0.,1]) 

        # choose a hidden state if none provided. 
        if type(hidden_state) == type(None):  
            L = self.fbward.hidden_states
            pr_vec = [(self.hidden_state_probabilities[l],l) for \
                l in L] 
            hidden_state = probability_to_label(pr_vec,pr)

        # choose the next action and hidden state 
        action,next_hidden_state = self.exec(hidden_state,pr) 
        self.log_motion(action,next_hidden_state) 

        self.num_rounds_since_pupdate += 1 
        return action,next_hidden_state