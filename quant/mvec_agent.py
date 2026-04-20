from morebs2.pa_derivative import * 

MOBILE_VECTOR_AGENT_ROLES = {"chaser","target"}

"""
Given a sequence of PRNGs, 
    S = <p_0,p_1,...,p_{k-1}>, 
forms a new PRNG by adding all PRNGs of S together, like such: 
    P() = p_0() + p_1() + ... + p_{k-1}(). 

"""
class GroupedPRNGDerivativePredictor: 

    def __init__(self,prng_seq): 
        assert len(prng_seq) > 0 

        q = prng_seq.pop(0)
        while len(prng_seq) > 0: 
            q_ = prng_seq.pop(0)
            q = merge_two_prgs(q,q_,add)  
        self.prg = q 

        self.target_loc = None 
        self.partial_derivative = None 
        self.dsum = None 

    def feed_context(self,target_loc,partial_derivative,total_derivative_sum):  
        assert is_vector(target_loc)
        assert is_vector(partial_derivative) 
        assert len(target_loc) == len(partial_derivative) 
        assert is_number(total_derivative_sum) 

        self.target_loc = target_loc
        self.partial_derivative = partial_derivative
        self.dsum = total_derivative_sum 

    def predict_next_location(self): 
        remaining = self.dsum - np.sum(self.partial_derivative) 

        l = len(self.target_loc) 
        partition = prg_partition_for_float__type2(remaining,l,self.prg,m=1) 
        partition = np.array(partition) 
        return np.round(partition + remaining,5) 

"""
Used by <MobileVectorAgent> of role `target`. 
Can be used to generate additive derivatives, as well as partial information 
additive segments for each of those derivatives.

"""
class MVAgentDerivativeGenerator: 

    def __init__(self,vector_length,segment_size_range,prg):  
        assert is_valid_range(segment_size_range,True,False) 

        self.length = vector_length 
        self.segment_size_range = segment_size_range
        self.prg = prg 
        self.cumulative_diff = 0
        self.d_outputter = VectorPiecewiseAdditiveDerivative(self.length,0,self.prg,\
            segment_size=self.segment_size_range[0],record_derivative_info=True)

    def load_sum(cumulative_diff): 
        assert is_number(cumulative_diff)
        seg_size = modulo_in_range(int(self.prg()),self.segment_size_range)
        self.d_outputter.reset(cumulative_diff,seg_size) 
        return

    """
    main method 
    """
    def process_full_derivative(self,cumulative_diff): 
        self.load_sum(cumulative_diff)
        while not self.d_outputter.fin_stat: 
            next(self.d_outputter) 
        return 

    def full_derivative(self): 
        return self.d_outputter.entire_vector_derivative() 

    def partial_info_on_derivative(self): 
        # select between 1 and n sums from partial 
        num_segments = modulo_in_range(int(self.prg()),[1,len(self.d_outputter.record)]) 
        record = deepcopy(self.d_outputter.record) 
        partial = prg_choose_n(record,num_segments,prg__single_to_int(self.prg),\
            is_unique_picker=True)
        return partial 

class MobileVectorAgent: 

    def __init__(self,v,role,prg,cumulative_diff_range=None,segment_size_range=None):   
        assert is_vector(v) 
        assert role in MOBILE_VECTOR_AGENT_ROLES
        if role == "target": 
            assert is_valid_range(segment_size_range,True,False) 
        else: 
            assert type(segment_size_range) == type(None) 

        self.v = v 
        self.role = role 
        self.prg = prg 

        self.cumulative_diff_range = None 
        self.segment_size_range = None 

        self.d_op = None 
        self.init_derivative_op() 

        self.weight = None 
        self.label = None 
        return 

    def init_derivative_op(self): 
        if self.role == "target": 
            self.d_op = MVAgentDerivativeGenerator(len(self.v),self.segment_size_range,self.prg)  
        return

    def set_weight_and_label(self,weight,label): 
        assert is_number(weight) 

        self.weight = weight 
        self.label = label  
        return

    def next_derivative(self,predicted_target_location=None): 
        if self.role == "target": 
            assert type(predicted_target_location) == type(None)
            self.d_op()
        else: 
            assert is_vector(predicted_target_location) 

class MVTrackingGroup: 

    def __init__(self): 
        return -1 

    def predict_next_location(self): 
        assert False 