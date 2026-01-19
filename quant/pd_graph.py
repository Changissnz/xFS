from graph_models.micrograph import * 
from .poison_snt import * 

class PoisonDeliveryNetwork: 

    def __init__(self,G:defaultdict,source_nodes,poison2source_map,poison_map): 
        self.G = G 
        self.source_nodes = source_nodes 
        self.poison2source_map = poison2source_map 
        self.poison_map = poison_map
        return 

    