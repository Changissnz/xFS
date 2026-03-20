from quant.controverter_graph import * 

class ControverterBot(ControverterNet): 

    def __init__(self,amap:dict,tmap:dict,N:NodePath,prg,allow_agent_move_knowledge):
        super().__init__(amap,tmap,N,prg,allow_agent_move_knowledge,\
            is_correlation_variable=True)
        return 

    @staticmethod 
    def generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg,allow_agent_move_knowledge=False,\
        is_correlation_variable=True): 
        # bot runs faster with no more than 10
        assert num_agents * path_size <= 10 

        q = ControverterNet.generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg,allow_agent_move_knowledge,\
        is_correlation_variable=True)

        return ControverterBot(q.amap,q.tmap,q.N,q.prg,\
            q.allow_agent_move_knowledge)