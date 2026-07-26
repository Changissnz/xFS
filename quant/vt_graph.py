from .mvec_agent import * 

DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE = [3.0,2000. + 1/7 + 1/6] 

DEFAULT_VECTOR_TRACKING__TRACKER_WEIGHT_RANGE = [\
    DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE[0] / 2,\
    DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE[1] / 2] 

DEFAULT_VECTOR_TARGET__DERIVATIVE_SEGMENT_SIZE_RANGE = [3,13]  

"""
Vector Tracking Network. 

A network comprised of n <MobileVectorAgent>s, (n - 1) of those agents being `tracker`s. 

At every timestamp, all trackers are given partial information of the location where 
target will be next:
[0] current target vector location 
[1] partial vector derivative 
[2] sum of entire vector derivative.  

Each tracker use this partial information to predict the next location of target. Prediction 
mechanism rests on PRNG operating in constraints for the sum of the entire vector derivative. 

There are two objectives for the tracking group: 
- minimize cumulative euclidean distance between the tracker locations and the target. 
- minimize the symmetric imbalance between the members of the tracking group. 
NOTE: symmetry calculation is done in method<MVTrackingGroupTypeSO.calculate_balance>. 
      For additional information, see description for class<MVTrackingGroupTypeSO.calculate_balance>. 
"""
class VectorTrackingNetwork: 

    def __init__(self,target,mt_group,verbose:bool=False): 
        assert type(target) == MobileVectorAgent
        assert type(mt_group) == MVTrackingGroupTypeSO  
        assert type(verbose) == bool 

        self.target = target 
        self.mt_group = mt_group
        self.verbose = verbose 

        self.timestamp = 0 
        self.euclidean_difference = 0 
        return 

    def __str__(self): 
        S = "-- target loc: {}\n".format(vector_to_string(self.target.v))
        S += "\n\n-- tracking group:\n\n{}\n".format(str(self.mt_group)) 
        return S 

    def set_prg(self,prg,for_target:bool): 
        assert type(for_target) == bool 
        if for_target: 
            self.target.set_prg(prg) 
        else: 
            self.mt_group.load_prg_into_agents(prg) 

    def __next__(self): 

        # have target move first 
        prior_loc = deepcopy(self.target.v) 
        total_diff = self.target.next_derivative()
        partial_vecs = np.array(self.target.partial_info_on_derivative()) 
        partial_diff = np.sum(partial_vecs,axis=0)  

        # feed tracking group partial info on target 
        self.mt_group.move_one(prior_loc,\
            partial_diff,total_diff,ext_prg=self.target.prg)

        # register euclidean distance 
        self.timestamp += 1 
        return self.measure_euclidean_distance() 

    def measure_euclidean_distance(self): 
        t = self.target.v 
        d = 0 
        for k,v in self.mt_group.mva_map.items(): 
            t2 = v.v 
            d += euclidean_point_distance(t,t2) 
        self.euclidean_difference += d 
        return d 

    @staticmethod
    def generate_instance(num_chasers,vector_bound_range,\
        tracker_point_dispersal_max_float:float,prg): 

        # generate the target 
        mv_target = MobileVectorAgent.generate_instance__role_target("target",\
            vector_bound_range,DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE,\
            DEFAULT_VECTOR_TARGET__DERIVATIVE_SEGMENT_SIZE_RANGE,deepcopy(prg)) 

        # generate the tracking group 
        tgroup = MVTrackingGroupTypeSO.generate_instance(num_chasers,vector_bound_range,\
            DEFAULT_VECTOR_TRACKING__TRACKER_WEIGHT_RANGE,tracker_point_dispersal_max_float,prg)

        return VectorTrackingNetwork(mv_target,tgroup) 