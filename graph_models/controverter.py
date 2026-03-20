from .game_table import * 
from morebs2.point_sorter import median_swap

def adjust_range_by_multiplier(r,m): 
    assert is_valid_range(r,True,True) or is_valid_range(r,False,True) 
    d = r[1] - r[0]
    r0 = r[0]  * m 
    return tuple(np.round((r0,r0+d),5))

"""
A structure used to produce payoff matrices for a set of n agents. At every 
timestamp t after the first, each agent p_i is given q_i new moves for the new 
payoff matrix (the agent situation). The quality of each agent situation is 
determined by the previous agent action profile (the map of each agent's move), 
in conjunction with other parameters. 

Generation of new payoff matrices relies on principles of correlation that 
use variables `pcorrelation_payoff` and `pcorrelation_upturn`. 

At timestamp t after the first, <GameControverter> receives agent action 
profile, via function<recv_agent_move_map>. <GameControverter> then adjusts 
every agent's possible cumulative payoff range (variable<agent2payoff_range>). 
This variable determines each agent's possible cumulative payoff range for the next 
<FullMultiAgentActionTable>. 

The adjustment process considers one of two categories, used to rank each agent's 
move in the agent's possible moveset: 
- immediate payoff
- cumulative payoff. 

Agent move is ranked according to the degree of positive correlation (1 is entirely 
positively correlated to the agent move with greatest mean payoff), 
variable<pcorrelation_payoff>. The agent a_i's rank r_i then is converted to a float f in [0.,1.], by 
    (r_i + 1) / (r_t + 1); r_t the total number of ranks starting at integer 0 (minumum rank). 
If 
    f <= variable<pcorrelation_upturn>, 
then the agent cumulative payoff range is on an "upturn". 
Otherwise, it is on a "downturn". The boolean for upturn is stored in variable<payoff_trend_map>. 

In a payoff upturn, the current possible cumulative payoff range r0 is adjusted by a float f in 
variable<cpayoff_multiplier_range>, via method<adjust_range_by_multiplier>, to produce r1, a 
range with a positive minumum. In a payoff downturn, r1 would have a negative maximum. 

The rank r_i for each agent a_i is then used to assign a bracket, in other words, a subrange 
of the possible cumulative payoff range for the agent a_i, to the agent a_i; see 
variable<next_agent_bracket>. This bracket is the agent's actual cumulative payoff range. No 
move of the agent in the next situation can be out of bounds of this bracket. When an agent 
chooses the "best" move (highest-ranking according to immediate XOR cumulative payoff), its 
rank is the highest when variable<pcorrelation_payoff> is 0, and lowest when variable<next_agent_bracket>
is 1. This rank corresponds to the bracket in the partition of the possible cumulative payoff 
range. 

To summarize, the rank of an agent's move bears effects in two dimensions. The primary dimension, 
by programmed design, is that of the trend (upturn or downturn). The secondary dimension is the 
bracket, the actual cumulative payoff range, a subrange in the possible cumulative payoff 
range. 

The two ranges, variable<agent_move_size_range> and variable<agent_payoff_bracket_range>, 
determine the possible number of moves every new situation allows an agent and the number 
of possible brackets for partitioning an agent's cumulative payoff range, respectively. 
------------------------------------------------------------------------------------------------

The class is named `GameControverter` because its programming controls agent situations, of moves and 
payoffs, for every timestamp after the first. 

`Controverter` is the acting noun for `controversy`. Similar to how controversies defy expectations, 
`Controverter` generates agent situations based on non-transparent correlations from every agent's 
move. Defiance of expectations and differences between predictions cause controversy. An agent that 
decides on "best" moves, calculated through some process, may find these "best" moves do not yield 
a satisfactory outcome.

NOTE: the correlations mentioned in this description are linearly independent. One agent B's move does 
      not affect another agent A's next moveset and possible cumulative payoff range. 
"""
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
        self.previous_agent_move_rank = {} 

        self.correlate_to_immediate_payoff = False 
        return  

    """
    main method 
    """
    def __next__(self): 
        assert type(self.agent_action_profile) != type(None) 
        self.derive_next()
        self.generate_next_table()
        self.agent_action_profile = None 
        return  

    """
    pre-main method 
    """
    def recv_agent_move_map(self,amap):  
        assert set(amap.keys()) == self.ftable.agents 
        self.agent_action_profile = amap 
        return

    def switch_correlation(self): 
        self.correlate_to_immediate_payoff = not self.correlate_to_immediate_payoff

    def derive_next(self):
        self.previous_agent_move_rank.clear()
        # get the action rankings 
        for a_idn in self.ftable.agents: 
            self.agent_derivative_proc(a_idn)
        return 

    def agent_derivative_proc(self,a_idn): 
        corr_rank,num_ranks = self.assign_agent_payoff_to_bracket(a_idn,\
            not self.correlate_to_immediate_payoff)  
        self.update_payoff_trend_for_agent(a_idn,corr_rank,num_ranks)
        self.previous_agent_move_rank[a_idn] = (corr_rank,num_ranks)

    def generate_next_table(self): 
        agent2movesize_map = {} 
        for a in self.ftable.agents: 
            agent2movesize_map[a] = modulo_in_range(int(self.prg()),self.agent_move_size_range)

        self.ftable = FullMultiAgentActionTable.generate_instance(\
            self.ftable.agents,agent2movesize_map,self.next_agent_bracket,\
            self.prg,self.agent_payoff_bracket_range,\
            self.move_idn_counter,self.cpayoff_multiplier_range,\
            duration_range=FullMultiAgentActionTable.DEFAULT_CUMULATIVE_PAYOFF_DURATION_RANGE,\
            ref_is_immediate_payoff=False) 

    """
    """
    def assign_agent_payoff_to_bracket(self,a_idn,is_cumulative_payoff:bool=True):
        ranked_moves = self.rank_agent_moves(a_idn,is_cumulative_payoff)
        a_move = self.agent_action_profile[a_idn] 

        move_rank = np.where(np.array(ranked_moves)[:,0] == a_move)[0][0] 
        move_rank = ranked_moves[move_rank][1]  

        ix = [i for i in range(ranked_moves[-1][1]+1)] 
        ix = median_swap(ix,self.pcorrelation_payoff)[::-1] 
        index = ix.index(move_rank)
        self.adjust_agent_payoff_range(a_idn) 

        num_brackets = ranked_moves[-1][1] + 1 
        a_range = self.agent2payoff_range[a_idn]
        brackets = n_partition_for_range(a_range,num_brackets)
        bracket = np.round(brackets[index:index+2],5)
        #print("a_range: ",a_range)
        #print("rank: ",move_rank)
        #print("bracket: ",index)  
        self.next_agent_bracket[a_idn] = tuple(bracket) 
        return index,num_brackets - 1 

    def rank_agent_moves(self,a_idn,is_cumulative_payoff:bool=True):
        if is_cumulative_payoff:  
            sorted_moves = self.ftable.agent_action_cmap.sort_agent_moves(a_idn,2)
        else: 
            sorted_moves = self.ftable.sort_agent_moves(a_idn,2)
        ranked_moves = rank_sequence(sorted_moves,vf=lambda x:x[1],\
            element_output_function=lambda x:x[0],output_type=list)  
        
        ranked_moves = prg_seqsort_ties(ranked_moves,self.prg,vf=lambda x:x[1])         
        return ranked_moves

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
        q0 = self.adjust_agent_payoff_range_(q0)
        self.agent2payoff_range[agent_idn] = q0 
        return q0

    def adjust_agent_payoff_range_(self,q0): 
        if q0[0] < GameControverter.DEFAULT_GAME_MIN_PAYOFF: 
            q0[0] = GameControverter.DEFAULT_GAME_MIN_PAYOFF
        if q0[1] < GameControverter.DEFAULT_GAME_MIN_PAYOFF: 
            q0[1] = GameControverter.DEFAULT_GAME_MIN_PAYOFF

        if q0[0] > GameControverter.DEFAULT_GAME_MAX_PAYOFF: 
            q0[0] = GameControverter.DEFAULT_GAME_MAX_PAYOFF
        if q0[1] > GameControverter.DEFAULT_GAME_MAX_PAYOFF: 
            q0[1] = GameControverter.DEFAULT_GAME_MAX_PAYOFF
        return q0 

    def update_payoff_trend_for_agent(self,agent_idn,correlation_rank,num_ranks):
        assert num_ranks > 0 
        r = (1 + correlation_rank) / (1 + num_ranks)
        pos_trend =  r <= self.pcorrelation_upturn 
        t = 1 if pos_trend else -1 
        self.payoff_trend_map[agent_idn] = t 
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