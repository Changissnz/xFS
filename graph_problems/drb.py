from quant.dual_obj import * 

class DualRoleBot: 

    def __init__(self,dual_agent,ce_effect,third_party_demands,option_size_range,prg): 
        super().__init__(dual_agent,ce_effect,third_party_demands,option_size_range,prg) 

    @staticmethod 
    def generate_instance(prg):
        D = DualEnvTypeHL.generate_instance(prg) 
        return DualRoleBot(D.dual_agent,D.ce_effect,D.third_party_demands,D.option_size_range,D.prg) 