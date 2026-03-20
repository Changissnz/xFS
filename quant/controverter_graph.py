from quant.gt_agent import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg_decimal,prg_to_prg__LCG_sequence

class ControverterNet: 

    def __init__(self,amap:dict,tmap:dict,G:defaultdict): 

        for v in amap.values(): assert type(v) == GTAgent
        assert len(amap) > 1 

        for v in tmap.values(): assert type(v) == GameControverter
        assert set(tmap.keys()) == set(G.keys())

        self.amap = amap 
        self.tmap = tmap 
        self.G = G
        return

    def set_non_auto_agent(self,a_idn): 
        return -1 

    @staticmethod 
    def generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg): 
        assert type(path_size) == int and path_size > 1 

        G = generate_graph__path(path_size,starting_node_idn=0,is_dsg=False)
        tmap = {} 
        for i in range(path_size): 
            print("-- controverter for node {}".format(i))
            n = ControverterNet.generate_one_node(num_agents,\
                agent_action_value_range,\
                cumulative_payoff_multiplier_range,prg)
            tmap[i] = n 

        agents = {} 
        prg_seq = prg_to_prg__LCG_sequence(prg,num_agents,45.5+67.7) 
        for i in range(num_agents): 
            agents[i] = GTAgent(i,"self",2,prg_seq[i]) 

        return ControverterNet(agents,tmap,G) 

    @staticmethod
    def generate_one_node(num_agents,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg): 

        agents = {i for i in range(num_agents)}
        agent2movesize_map = {i:\
            modulo_in_range(int(prg()),GameControverter.DEFAULT_GAME_AGENT_MOVE_SIZE_RANGE) \
            for i in range(num_agents)} 
        move_idn_counter = SimpleCounter(0).__next__ 
        pcorrelation_payoff = prg_decimal(prg,[0.,1.]) 
        pcorrelation_upturn = prg_decimal(prg,[0.,1.]) 

        T = GameControverter.generate_instance(agents,agent2movesize_map,agent_action_value_range,\
            prg,GameControverter.DEFAULT_GAME_AGENT_PAYOFF_MOVE_BRACKET_RANGE,move_idn_counter,\
            cumulative_payoff_multiplier_range,pcorrelation_payoff,pcorrelation_upturn)
        return T