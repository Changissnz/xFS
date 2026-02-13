from quant.hscript_graph import * 

class HomoFrameBot: 

    def __init__(self,admin,agents,prg,info_mode_is_open:bool=False,verbose:bool=False): 
        super().__init__(admin,agents,prg,info_mode_is_open,verbose) 
        return
        
    @staticmethod
    def generate_instance(num_agents,prg,agent_score,open_info): 
        hsn = HomoScriptNetwork.generate_instance(num_agents,prg,agent_score,open_info) 
        return HomoFrameBot(hsn.admin,hsn.agents,hsn.prg,hsn.open_info,hsn.verbose)