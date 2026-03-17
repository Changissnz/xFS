from .action_table import * 

"""
table for immediate + long-term payoffs from actions by agents. 
Three <MultiAgentActionTable> instances.
[0] immediate payoff  
[1] cumulative payoff  
[2] duration (number of timestamps) for cumulative payoff to be met 
"""
class FullMultiAgentActionTable(MultiAgentActionTable):

    DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE = [2,20] 

    def __init__(self,agents,agent_action_imap,agent_action_cmap,agent_action_dmap):
        super().__init__(agents,agent_action_imap)

        assert set(self.agent_action_map.keys()) == set(agent_action_cmap.keys()) 
        assert set(self.agent_action_map.keys()) == set(agent_action_dmap.keys()) 

        mt1 = MultiAgentActionTable(agents,agent_action_cmap) 
        mt2 = MultiAgentActionTable(agents,agent_action_dmap) 
        assert mt1.agent2move_map == self.agent2move_map == mt2.agent2move_map

        self.agent_action_cmap = mt1
        self.agent_action_dmap = mt2 

    def __str__(self): 
        S = ""
        keys = sorted(self.agent_action_map.keys())
        for k in keys: 
            S += self.stringize_action_profile(k) 
            S += "-" * 50 + "\n" 
        return S 

    def stringize_action_profile(self,k): 
        m2 = string_to_agent_move_map(k)
        x = self.agent_action_map[k]
        x1 = self.agent_action_cmap[k] 
        x2 = self.agent_action_dmap[k] 
        keys = sorted(m2.keys())

        s = ""
        for k2 in keys: 
            s += "agent {} move {} payoff_i {} payoff_t {} payoff_d {}\n".format(\
                k2,m2[k2],x[k2],x1[k2],x2[k2])  
        return s 

    """
    Generator scheme uses strict percentile scheme @ 
    method<MultiAgentActionTable.generate_instance__type_strict_percentile>.
    """
    @staticmethod 
    def generate_instance(agents,agent2movesize_map,\
        agent_action_value_range,prg,bracket_size_range,move_idn_counter,\
        cumulative_payoff_multiplier_range,\
        duration_range=DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE,\
        ref_is_immediate_payoff:bool=True):

        agent_action_cumulative_value_range = \
            MultiAgentActionTable.format_agent_action_value_range(agents,agent_action_value_range)

        # generate the reference (either immediate or cummulative)
        mt_ref = MultiAgentActionTable.generate_instance__type_strict_percentile(agents,\
            agent2movesize_map,agent_action_value_range,prg,bracket_size_range,\
            move_idn_counter)

        if not ref_is_immediate_payoff: 
            cumulative_payoff_multiplier_range = sorted([\
                zero_div(1,cumulative_payoff_multiplier_range[0],0),\
                zero_div(1,cumulative_payoff_multiplier_range[1],0)])
                
        # generate anti-reference (either immediate or cummulative)
        mt_antiref = FullMultiAgentActionTable.assign_accumulation_to_MultiAgentActionTable(mt_ref,\
            agent_action_cumulative_value_range,cumulative_payoff_multiplier_range,prg)  

        # assign duration
        mtd = FullMultiAgentActionTable.assign_duration_to_MultiAgentActionTable(\
            mt_ref,duration_range,prg) 

        q0,q1 = (mt_ref,mt_antiref) if ref_is_immediate_payoff else (mt_antiref,mt_ref) 
        return FullMultiAgentActionTable(mt_ref.agents,q0.agent_action_map,q1.agent_action_map,\
            mtd.agent_action_map)   

    @staticmethod 
    def assign_accumulation_to_MultiAgentActionTable(mt,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg):  

        agent_action_value_range = MultiAgentActionTable.format_agent_action_value_range(\
            mt.agents,agent_action_value_range)

        t0 = deepcopy(mt.agent_action_map) 

        # calculate 1 multiplier per agent 
        agents = sorted(mt.agents) 

        # multiply each agent's payoff range by a PRNG multiple
        keys = sorted(t0.keys())
        for k in keys: 
            v = t0[k] 
            for a in agents: 
                m = safe_modulo_in_range(prg(),cumulative_payoff_multiplier_range)
                v[a] = v[a] * m  
        
        return MultiAgentActionTable(mt.agents,t0)

    # NOTE: unused method. Every agent assigned 1 float multiple. Multiples are used for deriving 
    #       possible agent cumulative payoff ranges. 
    @staticmethod 
    def agent_to_cumulative_multiplier_map(agents,prg,cumulative_payoff_multiplier_range): 
        mult_map = {}
        agents = sorted(agents) 
        for a in agents: 
            mult_map[a] = safe_modulo_in_range(prg(),cumulative_payoff_multiplier_range) 
        return mult_map

    @staticmethod 
    def assign_duration_to_MultiAgentActionTable(mt,duration_range,prg):  
        assert is_valid_range(duration_range,True,False)

        t0 = deepcopy(mt.agent_action_map) 
        keys = sorted(t0.keys())
        agents = sorted(mt.agents) 

        for k in keys: 
            v = t0[k] 
            for a in agents: 
                v[a] = modulo_in_range(int(prg()),duration_range)
        
        return MultiAgentActionTable(mt.agents,t0)