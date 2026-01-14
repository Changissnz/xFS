from quant.mutable_ce_net import * 

class SlanderNetBase(MutableCEAgentNetwork): 

    def __init__(self,cea_map,auto_agents,prg):
        super().__init__(cea_map,prg,True) 
        self.set_auto_agents(auto_agents)  
