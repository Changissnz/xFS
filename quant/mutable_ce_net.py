from .ce_net import * 

class MutableCEAgentNetwork: 

    def __init__(self,can:CEAgentNetwork,auto_agents:set):
        assert type(can) == CEAgentNetwork
        assert auto_agents.issubset(set(can.cea_map.keys())) 
        self.can = can 
        self.auto_agents = auto_agents 
        return

    def __next__(self): 

        return -1 

    def auto_agent_decision(self,idn): 

        return -1 