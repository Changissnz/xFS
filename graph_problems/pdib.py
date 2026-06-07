from quant.

from quant.pd_inadvertency import * 

class PDIBot(PRNGProactionInadvertentEffectChain): 

    def __init__(self,num_moves,prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
        inadvertency_size_range,info_mode,chain_prg,solver_prg): 

        assert type(num_moves) == int and num_moves > 0 
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