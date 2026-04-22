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
        return 

    @staticmethod
    def generate_instance(num_chasers,vector_bound_range,\
        tracker_point_dispersal_max_float:float,prg): 

        # generate the target 
        mv_target = MobileVectorAgent.generate_instance__role_target("target",\
            vector_bound_range,DEFAULT_VECTOR_TRACKING__TARGET_CUMULATIVE_DIFF_RANGE,\
            DEFAULT_VECTOR_TARGET__DERIVATIVE_SEGMENT_SIZE_RANGE,deepcopy(prg)) 

        # generate the tracking group 
        tgroup = MVTrackingGroupTypeSO.generate_instance(num_chasers,vector_bound_range,\
            prg,DEFAULT_VECTOR_TRACKING__TRACKER_WEIGHT_RANGE,tracker_point_dispersal_max_float)