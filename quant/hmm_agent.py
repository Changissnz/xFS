from morebs2.hmm_fb import * 
from morebs2.pr2label import * 

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
        x = np.round([zero_div_(x_,denom,1/num_hidden) \
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

    # make hidden-to-observed table 
    B = one_HMM_table(hidden_states,observed_states,prg)

    return T,B,hidden_states,observed_states

#-----------------------------------------------------------

DEFAULT_HMM_OFFENDER_LCGV_RANGE = [1.,7+1/7+1/9+1/11] 

class HMMOffenderLCGDelta: 

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
        return 

    def set_prg(self,prg): 
        assert type(prg) in {MethodType,FunctionType} 
        self.prg = prg 

class HMMBasedOffender(HMMBasedAgent):

    def __init__(self,T,B,prg,initial_hidden_state,lcg_delta_pattern_type,lcgv_range):  
        super().__init__(T,B,prg) 

        assert initial_hidden_state in self.fbward.hidden_states
        self.current_hidden_state = initial_hidden_state

        self.lcg_loader = HMMOffenderLCGDelta(prg,pattern_type,lcgv_range)
        self.lcg0 = next(self.lcg_loader) 

        self.prng_outputs = [] 
        self.hidden_states.append(self.current_hidden_state) 
        return 

    def __next__(self): 

        x = prg_decimal(self.lcg0,[0,1]) 
        self.prng_outputs.append(x) 

        # choose next action 
        H = self.hidden_states[-1]
        pr_vec = [(self.fbward.B[H][o],o) for o in self.fbward.observed_states] 
        action = probability_to_label(pr_vec,x)

        # transition hidden state 
        pr_vec2 = [(self.fbward.T[H][h],h) for h in self.fbward.hidden_states] 
        self.current_hidden_state = probability_to_label(pr_vec2,x)
        self.hidden_states.append(self.current_hidden_state) 

        return     

    def load_next_LCG_(self,mod_range): 
        return -1 

class HMMBasedDefender(HMMBasedAgent): 

    def __init__(self,T,B,prg): 
        super().__init__(T,B,prg)  
        return

    def recv_hidden_state(self,h): 
        assert h in self.fbward.hidden_states
        self.current_hidden_state = h 

    def guess_hidden_state(self): 