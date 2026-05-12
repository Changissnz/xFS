from .dir_imp_path import * 
from .hypergraph import * 

"""
Objective Path, Type (D)irected (I)mplication. 
"""
class ObjectivePathTypeDI(DirectedImplicationPath):  

    def __init__(self,G,node_value_map,objective_float,relation): 
        super().__init__(G) 
        assert type(objective_float) == float    
        assert type(relation) in {MethodType,FunctionType} 

        assert set(node_value_map.keys()) == set(G.keys())
        numbers = 0 
        ranges = 0 
        for v in node_value_map.values(): 
            if is_valid_range(v): 
                assert v[0] > 0. 
                ranges += 1 
            else: 
                assert is_number(v) 
                numbers += 1 
            assert numbers == 0 or ranges == 0 
        if numbers: 
            self.ptype = "linexp" 
        else: 
            self.ptype = "csum" 
        self.nv_map = node_value_map
        self.obj_float = objective_float
        self.R = relation 