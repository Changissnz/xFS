from quant.pd_graph import * 

class PTBot(PoisonDeliveryNetwork): 

    def __init__(self,G:defaultdict,source_map,target_map,verbose:bool=False):  
        super().__init__(G,source_map,target_map,verbose)
        return

    @staticmethod 
    def generate_instance(num_source_nodes,num_targets,num_poisons,poison2source_ratio_range,poison_matrix_square_dim,\
        expressive_mode,prg,seed_pair,relays_per_source=2,relay_accuracy_range=[0.75,0.9],verbose:bool=False): 

        random.seed(seed_pair[0]) 
        np.random.seed(seed_pair[1]) 

        pdn = PoisonDeliveryNetwork.generate_instance(num_source_nodes,num_targets,\
            num_poisons,poison2source_ratio_range,poison_matrix_square_dim,\
            expressive_mode,prg,relays_per_source=relays_per_source,\
            relay_accuracy_range=relay_accuracy_range,verbose=verbose) 
        return PTBot(pdn.G,pdn.source_map,pdn.target_map,verbose) 