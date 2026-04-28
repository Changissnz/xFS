from morebs2.hmm_fb import * 

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

class HMMBasedAgent: 

    def __init__(self,T,B): 
        self.fbward = ForwardBackward(T,B)
        return 

class HMMBasedOffender(HMMBasedAgent):

    def __init__(self,T,B,initial_hidden_state): 
        super().__init__(T,B) 

        assert initial_hidden_state in self.fbward.hidden_states
        self.current_hidden_state = initial_hidden_state
        return 

    def __next__(self): 
        return -1 

    def load_next_LCG_(self,mod_range): 
        return -1 

class HMMBasedDefender(HMMBasedAgent): 

    def __init__(self,T,B): 
        super().__init__(T,B) 
        return
