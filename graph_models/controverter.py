from .game_table import * 
from morebs2.point_sorter import median_swap

def adjust_range_by_multiplier(r,m): 
    assert is_valid_range(r,True,True) or is_valid_range(r,False,True) 
    d = r[1] - r[0]
    r0 = r[0]  * m 
    return (r0,r0+d)

class GameControverter:


    DEFAULT_GAME_MIN_PAYOFF = - (10 ** 7) 
    DEFAULT_GAME_MAX_PAYOFF = 10 ** 7
    DEFAULT_GAME_AGENT_MOVE_SIZE_RANGE = [2,8]
    DEFAULT_GAME_AGENT_PAYOFF_MOVE_BRACKET_RANGE = [2,6]

    """

    """
    def __init__(self,ftable:FullMultiAgentActionTable,agent2payoff_range,\
        cumulative_payoff_multiplier_range,pcorrelation_payoff:float,pcorrelation_upturn:float,prg,\
        move_idn_counter,agent_move_size_range = DEFAULT_GAME_AGENT_MOVE_SIZE_RANGE,\
        agent_payoff_bracket_range = DEFAULT_GAME_AGENT_PAYOFF_MOVE_BRACKET_RANGE): 

        assert cumulative_payoff_multiplier_range[0] < 0 and cumulative_payoff_multiplier_range[1] > 0 
        assert 0. <= pcorrelation_payoff <= 1.0 
        assert 0. <= pcorrelation_upturn <= 1.0 
        assert is_valid_range(agent_move_size_range,True,False) 
        assert is_valid_range(agent_payoff_bracket_range,True,False) 

        self.ftable = ftable 
        # cumulative payoff 
        self.agent2payoff_range = agent2payoff_range
        self.cpayoff_multiplier_range = cumulative_payoff_multiplier_range 
        self.pcorrelation_payoff = pcorrelation_payoff
        self.pcorrelation_upturn = pcorrelation_upturn
        self.prg = prg 
        self.move_idn_counter = move_idn_counter
        self.agent_move_size_range = agent_move_size_range
        self.agent_payoff_bracket_range = agent_payoff_bracket_range 

        self.agent_action_profile = None 

        self.payoff_trend_map = {a:0 for a in self.ftable.agents}
        self.next_agent_bracket = {} 
        return    

    def recv_agent_move_map(self,amap):  
        assert set(amap.keys()) == self.ftable.agents 
        self.agent_action_profile = amap 
        return

    def derive_next(self):
        # get the action rankings 
        for a_idn in self.ftable.agents: 
            self.agent_derivative_proc(a_idn)
        return 

    def agent_derivative_proc(self,a_idn): 
        corr_rank,num_ranks = self.assign_agent_payoff_to_bracket(a_idn) 
        self.update_payoff_trend_for_agent(a_idn,corr_rank,num_ranks)

    def generate_next_table(self): 
        agent2movesize_map = {} 
        for a in self.ftable.agents: 
            agent2movesize_map[a] = modulo_in_range(int(self.prg()),self.agent_move_size_range)

        self.ftable = FullMultiAgentActionTable.generate_instance(\
            self.ftable.agents,agent2movesize_map,self.agent2payoff_range,\
            self.prg,self.agent_payoff_bracket_range,\
            self.move_idn_counter,self.cpayoff_multiplier_range,\
            duration_range=FullMultiAgentActionTable.DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE,\
            ref_is_immediate_payoff=False) 

    """
    """
    def assign_agent_payoff_to_bracket(self,a_idn,is_cumulative_payoff:bool=True):
        if is_cumulative_payoff:  
            sorted_moves = self.ftable.agent_action_cmap.sort_agent_moves(a_idn,2)
        else: 
            sorted_moves = self.ftable.sort_agent_moves(a_idn,2)

        ranked_moves = rank_sequence(sorted_moves,vf=lambda x:x[1],\
            element_output_function=lambda x:x[0],output_type=list)  
        a_move = self.agent_action_profile[a_idn] 

        move_rank = np.where(np.array(ranked_moves)[:,0] == a_move)[0][0] 

        ix = [i for i in range(ranked_moves[-1][1]+1)] 
        ix = median_swap(ix,self.pcorrelation_payoff)[::-1] 
        index = ix.index(move_rank)
        self.adjust_agent_payoff_range(a_idn) 

        num_brackets = ranked_moves[-1][1] + 1 
        a_range = self.agent2payoff_range[a_idn]
        brackets = n_partition_for_range(a_range,num_brackets)
        bracket = brackets[index:index+2]
        self.next_agent_bracket[a_idn] = bracket 
        return index,num_brackets - 1 

    # TODO 
    def adjust_agent_payoff_range(self,agent_idn): 
        q0 = self.agent2payoff_range[agent_idn]
        # no change 
        if self.payoff_trend_map[agent_idn] == 0: 
            return q0  
                
        upturn_range = [0.,self.cpayoff_multiplier_range[1]]
        downturn_range = [-self.cpayoff_multiplier_range[1],0]#-self.cpayoff_multiplier_range[0]] 

        # upturn 
        if self.payoff_trend_map[agent_idn] == 1: 
            # bottom range is neg, switch to conventional downturn 
            if q0[0] < 0: 
                q = downturn_range
            else: 
                q = upturn_range
        else: 
            # bottom range is neg, switch to conventional upturn  
            if q0[0] < 0: 
                q = upturn_range 
            else: 
                q = downturn_range

        m = safe_modulo_in_range(self.prg(),q) 
        q0 = adjust_range_by_multiplier(q0,m)
        self.agent2payoff_range[agent_idn] = q0 
        return q0

    def update_payoff_trend_for_agent(self,agent_idn,correlation_rank,num_ranks):
        assert num_ranks > 0 
        r = (1 + correlation_rank) / (1 + num_ranks)
        pos_trend =  r <= self.pcorrelation_upturn 
        t = 1 if pos_trend else -1 
        self.payoff_trend_map[agent_idn] = t 
        return 

    def __next__(self): 
        assert type(self.agent_action_profile) != type(None) 
        self.derive_next()
        self.generate_next_table()
        return

    ########################################

    @staticmethod 
    def generate_instance(agents,agent2movesize_map,\
        agent_action_value_range,prg,bracket_size_range,move_idn_counter,\
        cumulative_payoff_multiplier_range,pcorrelation_payoff,\
        pcorrelation_upturn):

        move_idn_counter = SimpleCounter(0).__next__

        ft = FullMultiAgentActionTable.generate_instance(agents,agent2movesize_map,\
        agent_action_value_range,prg,bracket_size_range,move_idn_counter,\
        cumulative_payoff_multiplier_range,\
        duration_range=FullMultiAgentActionTable.DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE,\
        ref_is_immediate_payoff=True)

        agent_action_value_range = MultiAgentActionTable.format_agent_action_value_range(\
            agents,agent_action_value_range) 

        agent2payoff_range = {} 
        agents_ = sorted(agents)
        for a in agents_: 
            r = agent_action_value_range[a] 
            m = safe_modulo_in_range(prg(),cumulative_payoff_multiplier_range) 
            agent2payoff_range[a] = adjust_range_by_multiplier(r,m)  

        return GameControverter(ft,agent2payoff_range,cumulative_payoff_multiplier_range,\
            pcorrelation_payoff,pcorrelation_upturn,prg,move_idn_counter)