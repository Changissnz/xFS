from graph_models.micrograph import * 
from .poison_snt import * 

class PoisonPath: 

    def __init__(self): 
        return -1 

class PoisonDeliveryNetwork: 

    def __init__(self,G:defaultdict,source_nodes,poison2source_map,poison_map): 
        self.G = G 
        self.source_nodes = source_nodes 
        self.poison2source_map = poison2source_map 
        self.poison_map = poison_map
        return 

    @staticmethod 
    def generate_instance(num_source_nodes,num_targets,num_poisons,poison2source_variance):  
        return -1