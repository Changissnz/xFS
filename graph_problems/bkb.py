from quant.bull_graph import * 

"""
Bull Killer Bot. 

See file<quant.bull_graph> for details on logistics. 
"""
class BKBot(BullNetwork): 

    def __init__(self,G,edge_cost_function,entry_points,bull,agents,visual_radius,\
        c2c_distance,prg,open_info_mode,bull_is_2nd_premover:float):   
        super().__init__(G,edge_cost_function,entry_points,bull,agents,visual_radius,\
            c2c_distance,prg,open_info_mode,bull_is_2nd_premover)
        return

    def set_LCG_prng_derivatives_for_agents(self,prg): 
        l = len(self.agents) 
        prngs = prg_to_prg__LCG_sequence(prg,l,2.997+3/11) 
        keys = sorted(self.agents.keys()) 

        for (i,k) in enumerate(keys): 
            self.set_prng_for_agent(k,prngs[i])

    def set_prng_for_agent(self,agent_idn,prg): 
        assert type(prg) in {MethodType,FunctionType} 
        self.agents[agent_idn].prg = prg 

    @staticmethod 
    def generate_instance(num_nodes,growth_type,num_entry_points,\
        num_agents,visual_radius,c2c_distance,prg,open_info_mode,\
        bull_is_2nd_premover,bull_energy,chaser_energy,\
        weight_range=[1,10]):

        bn = BullNetwork.generate_instance(num_nodes,growth_type,\
            num_entry_points,num_agents,visual_radius,c2c_distance,\
            prg,open_info_mode,bull_is_2nd_premover,bull_energy,chaser_energy,\
            weight_range=[1,10])

        bk = BKBot(bn.G,bn.edge_cost_function,bn.entry_points,\
            bn.bull,bn.agents,bn.visual_radius,bn.c2c_distance,bn.prg,bn.oi_mode,\
            bn.bull_is_2nd_premover)
        bk.load_shortest_paths_approx(bn.spa) 
        return bk 