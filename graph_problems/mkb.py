from quant.mob_graph import * 

class MobKillerBot(MobNetwork): 

    def __init__(self,G,antimob:AntiMobUnit,mob_agent_map:dict,prg,mutable_weight_function,\
        verbose=False):
        super().__init__(G,antimob,mob_agent_map,prg,mutable_weight_function,\
            verbose=False)

    @staticmethod
    def generate_instance(num_agents,prg,antimob_score,mob_agent_uniform_score,\
        mob_agent_weight_range=[1,200],mutable_weight_function = lambda x: x + 0): 

        mn = MobNetwork(num_agents,prg,antimob_score,mob_agent_uniform_score,\
            mob_agent_weight_range,mutable_weight_function) 

        return MobKillerBot(mn.G,mn.antimob,mn.mob_agent_map,mn.prg,\
            mn.mutable_weight_function,mn.verbose)