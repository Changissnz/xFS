from morebs2.pa_derivative import * 
from morebs2.numerical_generator import vector_modulo_in_bounds 
from collections import deque 

MOBILE_VECTOR_AGENT_ROLES = {"chaser","target"}

# method used for parameter in function<morebs2.prg_to_prg__LCG_sequence> 
DEFAULT_MV_TRACKING_GROUP_LCG_INIT_MODULO_MULTIPLIER = [1.,5 + 18/19]

"""
Used by class<MVTrackingGroupTypeSO> to predict mobile vector 
target, an instance of class<MobileVectorAgent>. 

Given a sequence of PRNGs, 
    S = <p_0,p_1,...,p_{k-1}>, 
forms a new PRNG P by adding all PRNGs of S together, like such: 
    P() = p_0() + p_1() + ... + p_{k-1}(). 

Uses P to predict the next location, given input parameters 
[0] current target location (a vector)  
[1] partial derivative d0 
[2] total derivative sum 
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
of additive segments for each of those derivatives.
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

"""
An agent that is essentially a mutable vector in dimension n. Agent 
is exactly one of two roles: `chaser` or `target`. 

Method<next_derivative> allows the agent to 'move', according to the 
programmed logistics of its role. 

Specifically, if agent is a `target`, it uses an <MVAgentDerivativeGenerator> 
to calculate every next derivative. If agent is a `chaser`, it is given a 
derivative that is calculated from a <GroupedPRNGDerivativePredictor>. 
This <GroupedPRNGDerivativePredictor> operates using this agent's PRNG, as 
well as all other <MobileVectorAgent>s that are part of the same group. 
"""
class MobileVectorAgent: 

    def __init__(self,idn,v,role,prg,cumulative_diff_range=None,segment_size_range=None,\
        derivative_log_length=200):   
        assert is_vector(v) 
        assert role in MOBILE_VECTOR_AGENT_ROLES
        if role == "target": 
            assert is_valid_range(cumulative_diff_range,False,False) or \
                is_valid_range(cumulative_diff_range,True,False) 
            assert cumulative_diff_range[0] > 0 

            assert is_valid_range(segment_size_range,True,False) 
            assert segment_size_range[0] > 0 
        else: 
            assert type(cumulative_diff_range) == type(None) 
            assert type(segment_size_range) == type(None) 

        self.idn = idn 
        self.v = v 
        self.role = role 
        self.prg = None 
        self.set_prg(prg) 

        self.cumulative_diff_range = cumulative_diff_range 
        self.segment_size_range = segment_size_range

        self.d_op = None 
        self.init_derivative_op() 

        self.derivative_log_length = derivative_log_length
        self.derivative_log = deque() 

        self.weight = None 
        self.label = None 
        return 

    def set_prg(self,prg): 
        assert type(prg) in {MethodType,FunctionType} 
        self.prg = prg 

    def init_derivative_op(self): 
        if self.role == "target": 
            self.d_op = MVAgentDerivativeGenerator(len(self.v),self.segment_size_range,self.prg)  
        return

    def set_weight_and_label(self,weight,label): 
        assert is_number(weight) 

        self.weight = weight 
        self.label = label  
        return

    def next_derivative(self,calculated_derivative=None): 
        if self.role == "target": 
            assert type(calculated_derivative) == type(None)
            diff = modulo_in_range(self.prg(),self.cumulative_diff_range) 
            self.d_op.process_full_derivative(diff) 
            q = self.d_op.full_derivative()

            self.update_dlog(q) 
            self.v += q 
        else: 
            assert is_vector(calculated_derivative) 
            self.update_dlog(calculated_derivative) 
            self.v += calculated_derivative

    def update_dlog(self,derivative): 
        self.derivative_log.append(derivative) 

        while len(self.derivative_log) > self.derivative_log_length: 
            self.derivative_log.pop()

"""
Mobile Vector Tracking Group, Type Symmetric Objective. 

Container for a group of n <MobileVectorAgent>s, `chaser` role.

This structure is used in class<MobileVectorNetwork>, and represents the 
`chaser` faction. 

The acronym SO (Symmetric Objective) is given for this structure because 
of the objective of 'symmetric' formation of the group members around 
an external target <MobileVectorAgent>. 

Every time the group moves, via 1 different vector per agent, to the next 
timestamp to track a target <MobileVectorAgent>, every agent A_i is assigned 
a weight w_i and binary label l_i. For m = |<MobileVectorAgents>|, there are 
floor(m / 2) agents with 0 label, the remaining with 1 label (roughly equal 
in set size). 

A classification structure, that is, <morebs2.RecursiveOneDimClassifier> C is 
used to classify the agent vectors V and their labels L. Classifier classifies 
V into two sets, 1 label and 0 label. Then the score of symmetric balance of 
the agent vectors is 

 |  [ sum       W(C(v_i)) ]  -  [ sum       W(C(v_j)) ]   |;  
    C(v_i) = 0                  C(v_j) = 0            

    v_i,v_j in V. 

In natural language, this would be the absolute difference in weighted sum of 
the agents labeled 0 and the agents labeled 1. 

"""
class MVTrackingGroupTypeSO: 

    def __init__(self,mva_map,weight_range,point_dispersal_max_float:float):
        assert type(mva_map) == dict 

        dimension = set() 
        for k,v in mva_map.items(): 
            dimension |= {len(v.v)} 

            assert k == v.idn 
            assert v.role == "chaser"
            assert len(dimension) == 1 

        assert len(mva_map) > 1 

        assert is_valid_range(weight_range,False,False) or is_valid_range(weight_range,True,False)
        assert weight_range[0] > 0 
        assert is_number(point_dispersal_max_float) 
        assert point_dispersal_max_float > 0 

        self.mva_map = mva_map 
        self.weight_range = weight_range
        self.point_dispersal_max_float = point_dispersal_max_float

        self.predictor = None 
        self.init_predictor()
        self.predicted_next_location = None 

        self.vdim = dimension 

        self.cumulative_balance = 0 
        self.balance_log = deque() 
        return

    """
    uses 1 PRNG `prg` to create |`mva_map`| LCGs. Every i'th 
    agent is set with the i'th LCG. 
    """
    def load_prg_into_agents(self,prg): 

        keys = sorted(self.mva_map.keys())
        prng_seq = prg_to_prg__LCG_sequence__v2(prg,len(keys),\
            mod_scale_range=\
            DEFAULT_MV_TRACKING_GROUP_LCG_INIT_MODULO_MULTIPLIER)

        for (i,k) in enumerate(keys): 
            p = prng_seq[i] 
            self.mva_map[k].set_prg(p)
        return

    def init_predictor(self): 
        keys = sorted(self.mva_map.keys())
        prng_seq = [] 
        for k in keys:
            prng_seq.append(self.mva_map[k])  
        self.predictor = GroupedPRNGDerivativePredictor(prng_seq) 

    #--------------------------------- target location prediction 

    def predict_next_location(self,target_loc,partial_derivative,\
        total_derivative_sum): 

        self.predictor.feed_context(target_loc,partial_derivative,\
            total_derivative_sum) 
        p = self.predictor.predict_next_location()
        self.predicted_next_location = p 
        return deepcopy(p)

    #---------------------------------- symmetric balance 

    def assign_weights_and_labels(self): 
        prg = self.predictor.prg 

        keys = sorted(self.mva_map.keys())

        num_zeros = len(keys) // 2 
        prg_ = prg__single_to_int(prg) 

        keys2 = deepcopy(keys)
        zeros = prg_choose_n(keys2,num_zeros,prg_,is_unique_picker=True) 
        ones = keys2 
        labels = [0] * len(keys) 
        for o in ones: 
            labels[o] = 1

        for k in keys: 
            w = modulo_in_range(self.prg(),self.weight_range)
            A = self.mva_map[k] 
            A.set_weight_and_label(w,l) 
        return 

    """
    return: 
    - list(vector),list(weight),list(label)
    """
    def agent_info(self): 

        keys = sorted(self.mva_map.keys())        
        V,W,L = [],[],[] 
        for k in keys: 
            A = self.mva_map[k] 
            V.append(deepcopy(A.v)) 
            W.append(A.weight)
            L.append(A.label)
        return np.array(V),np.array(W),np.array(L) 

    def calculate_balance(self):
        V,W,L = self.agent_info() 
        rodc = self.classifier_from_points(V,L)

        pos_weights = 0 
        neg_weights = 0 

        l = len(V) 
        for i in range(l): 
            v = V[i] 
            w = W[i] 

            b = rodc.classify(v)
            if b: 
                pos_weights += w 
            else: 
                neg_weights += w 
        return abs(pos_weights - neg_weights)

    def classifier_from_points(self,V,L):  
        prg = self.predictor.prg 
        rodc = RecursiveOneDimClassifier(V,L,prg,pscheme=0,verbose=False)
        rodc.fit()
        return rodc

    #----------------------------- moving agents 

    """
    main method 
    """
    def move_one(self,target_loc,partial_derivative,\
        total_derivative_sum,ext_prg=prg__constant(x=0)):  

        self.move_MVAgents(target_loc,partial_derivative,\
            total_derivative_sum,ext_prg)
        self.assign_weights_and_labels()
        self.calculate_balance() 

    def move_MVAgents(self,target_loc,partial_derivative,\
        total_derivative_sum,ext_prg=prg__constant(x=0)): 

        self.predict_next_location(target_loc,partial_derivative,\
            total_derivative_sum) 
        self.move_each_MVAgent_(ext_prg) 
        return 

    def move_each_MVAgent_(self,ext_prg=prg__constant(x=0)): 
        keys = sorted(self.mva_map.keys()) 
        l = len(self.predicted_next_location) 
        for k in keys: 
            A = self.mva_map[k] 
            self.move_MVAgent(k,ext_prg) 
        return 

    def move_MVAgent(self,k,ext_prg=prg__constant(x=0)): 

        l = len(self.predicted_next_location) 

        A = self.mva_map[k]
        combined_prg = merge_two_prgs(ext_prg,A.prg,add)
        
        pdisp_vec = prg_partition_for_float__type2(self.point_dispersal_max_float,l,\
            combined_prg,m=1) 

        destination = self.predictor.predicted_next_location + pdisp_vec

        derivative = destination - A.v 
        A.next_derivative(derivative) 
        return derivative    

    @staticmethod
    def generate_instance(num_agents,vector_bound_range,prg,weight_range,point_dispersal_max_float:float):  
        assert is_bounds_vector(vector_bound_range) 

        # generate vectors 
        prgv = prg__single_to_nvec(prg,vector_bound_range.shape[0])
        agent_vectors = [vector_modulo_in_bounds(prgv(),vector_bound_range) \
            for _ in range(num_agents)] 

        # generate the PRNG-LCGs for each agent 
        prng_seq = prg_to_prg__LCG_sequence__v2(prg,num_agents,\
            mod_scale_range=\
            DEFAULT_MV_TRACKING_GROUP_LCG_INIT_MODULO_MULTIPLIER)

        # instantiate each Chaser 
        mva_map = dict() 
        role = "chaser"
        for i in range(num_agents): 
            idn = i 
            v = agent_vectors[i] 
            prg = prng_seq[i] 

            C = MobileVectorAgent(idn,v,role,prg,None,None) 
            mva_map[i] = C 

        return MVTrackingGroupTypeSO(mva_map,weight_range,point_dispersal_max_float)