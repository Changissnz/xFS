from .mvec_agent import * 

DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE = [3.0,2000. + 1/7 + 1/6] 

DEFAULT_VECTOR_TRACKING__TRACKER_WEIGHT_RANGE = [\
    DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE[0] / 2,\
    DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE[1] / 2] 

DEFAULT_VECTOR_TARGET__DERIVATIVE_SEGMENT_SIZE_RANGE = [3,13]  

"""
Vector Tracking Network. 

A network comprised of n <MobileVectorAgent>s, (n - 1) of those agents being `chaser`s. 
"""
class VectorTrackingNetwork: 

    def __init__(self,target,mt_group): 
        assert type(target) == MobileVectorAgent
        assert type(mt_group) == MVTrackingGroupTypeSO  

        self.target = target 
        self.mt_group = mt_group

        self.euclidean_difference = 0 
        return 

    def __str__(self): 
        S = "-- target loc: {}\n".format(vector_to_string(self.target.v))
        S += "\n\n-- tracking group:\n\n{}\n".format(str(self.mt_group)) 
        return S 

    def load_prg(self,prg,for_target:bool): 
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