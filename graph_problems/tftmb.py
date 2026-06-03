from quant.agent_23 import * 

"""
NOTE: 
See description for class<AgentType2F3M> in file<quant.agent_23> for information on the logistics 
of this bot. 

If `variable_comp` is set to True, after every timestamp, bot modifies the agent-to-agent compatibilities 
and agent-to-agent-categorical-label compatibilities. See variable<AgentType2F3MMOContainer.comp_map> 
and variable<AgentType2F3MMOContainer.aa_comp_map> for more information. 
"""
class ThreeFacesTwoMotivesBot(AgentType2F3MTrifecta): 

    def __init__(self,a0,a1,a2,variable_comp:bool,verbose=False): 
        assert type(variable_comp) == bool 
        super().__init__(a0,a1,a2,verbose) 
        self.variable_comp = variable_comp
        return

    def __next__(self): 
        super().__next__() 
        self.alter_compatibilities()

    def alter_compatibilities(self): 
        if not self.variable_comp: return 
        for i in range(3): self.alter_compatibilities_(i) 

    def alter_compatibilities_(self,number):
        if not self.variable_comp: return 

        q = [self.a0,self.a1,self.a2]  
        a = q.pop(number) 
        prg = merge_two_prgs(q[0].prg(),q[1].prg(),add)
        def prg_(): 
            return prg_decimal(prg,[0.,1.])

        a.set_compatibility(prg_,True)
        a.set_compatibility(prg_,False) 
        return

    @staticmethod 
    def generate_instance(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,variable_comp:bool,prg):

        ATT = AgentType2F3MTrifecta.generate_instance(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,prg)
        tbot = ThreeFacesTwoMotivesBot(ATT.a0,ATT.a1,ATT.a2,variable_comp,verbose=False)
        return tbot 
