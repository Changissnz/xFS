from graph_models.hg_obj_path_op import * 

DEFAULT_ENDS_FIXATED_BOT_NODESIZE_RANGE = [3,35] 

class EndsFixatedBot(DIPathNavigatorHandler): 

    def __init__(self,optdi,dipn,info_mode,verbose=False): 
        super().__init__(optdi,dipn,info_mode,verbose)

    @staticmethod
    def generate_instance(node_value_range,extra_edge_ratio:float,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,info_mode:int,prg): 

        assert is_valid_range(node_value_range,True,False) or is_valid_range(node_value_range,False,False) 
        assert node_value_range[0] > 0

        num_nodes = modulo_in_range(int(prg()),DEFAULT_ENDS_FIXATED_BOT_NODESIZE_RANGE)
        G = generate_directed_implication_path(num_nodes,extra_edge_ratio,prg,start_node_idn=0)

        node_value_range_map = {} 
        for i in range(num_nodes): 
            r0 = modulo_in_range(prg(),node_value_range) 
            r1 = modulo_in_range(prg(),node_value_range)

            if r0 == r1: 
                r1 = modulo_in_range(r0 + 1,node_value_range)

            r0,r1 = sorted([r0,r1]) 
            node_value_range_map[i] = (r0,r1) 
        
        optdi = ObjectivePathTypeDI.generate_instance(G,node_value_range_map,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,prg)

        dipn = DIPathNavigator.from_PathTypeDI(optdi,prg)
        return EndsFixatedBot(optdi,dipn,info_mode,verbose=False)