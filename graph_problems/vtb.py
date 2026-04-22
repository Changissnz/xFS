from quant.vt_graph import * 

class VTBot(VectorTrackingNetwork): 

    def __init__(self,target,mt_group): 
        super().__init__(target,mt_group) 

    @staticmethod
    def generate_instance(num_chasers,vector_bound_range,\
        tracker_point_dispersal_max_float:float,prg): 
        vtn = VectorTrackingNetwork.generate_instance(num_chasers,\
            vector_bound_range,tracker_point_dispersal_max_float,prg) 
        return VTBot(vtn.target,vtn.mt_group)