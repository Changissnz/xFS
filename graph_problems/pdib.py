from quant.pd_inadvertency import * 

inadvertency_ratio_range = [0.05,0.15]
node_value_range = [30.,350.]

DEFAULT_PDIBOT_NODE_VALUE_MINIMUM = 15. 
DEFAULT_PDIBOT_INADVERTENCY_MIN_RATIO = 0.025  

"""
Proaction-Driven Inadvertency Bot. 

Built on top of class<PRNGProactionInadvertentEffectChain>. The variable<num_moves> 
determines how many 3-noded Directed Implication Paths the `solver_prg` must solve 
before termination. 

Bot is observant of the number of inadvertencies activated by the `solver_prg` in its 
attempt to solve the `num_moves` number of <PRNGProactionInadvertentEffect>s. 
"""
class PDIBot(PRNGProactionInadvertentEffectChain): 

    def __init__(self,num_moves,prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
        inadvertency_size_range,info_mode,chain_prg,solver_prg): 

        assert type(num_moves) == int and num_moves > 0
        assert inadvertency_ratio_range[0] >= DEFAULT_PDIBOT_INADVERTENCY_MIN_RATIO
        assert node_value_range[0] >= DEFAULT_PDIBOT_NODE_VALUE_MINIMUM 

        self.num_moves = num_moves
        super().__init__(prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
            inadvertency_size_range,info_mode,chain_prg,solver_prg) 

        self.fin_stat = False 
        return

    def __next__(self): 
        if type(self.current_pie) == type(None): 
            self.fin_stat = len(self) >= self.num_moves 
        
        if self.fin_stat: return 

        super().__next__() 