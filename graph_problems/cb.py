from quant.controverter_graph import * 

"""
Controverter Bot. 

An automaton consisting of n agents in a multi-agent setting, S. S consists of a unidirectional 
chain of decision junctions. Each decision junction is a node that is a <GameControverter> 
instance; see file<graph_models.controverter> for more details. 

Every <GameControverter> consists of 3 payoff matrices. These matrices are virtually identical to 
the ones found in game theory, and these 3 payoff matrices contain the same moveset for each agent. 
The payoff matrices are for immediate payoff, cumulative payoff, and duration (number of timestamps) 
for the cumulative payoff to be distributed to its respective agent. The name of <*Controverter> is 
given to this data structure because of the possible great discrepancy between immediate and cumulative 
payoffs, as well as the effect these agent decisions have on the broad trajectory of their payoff matrices 
over the course of time. These discrepancies comprise an important factor in agents determining what the 
"best" move to take for a <GameControverter>. By default in <ControverterBot>, an automated agent will 
choose the move with the greatest average cumulative payoff. Recall that in a multi-agent setting with 
agents a_1,...,a_n, every agent a_i has m_i available moves to take, for a total of 
    t = (m_1 * m_2 * ... * m_n) possible agent action profiles. 
For an agent a_i that chooses a move dx out of its possible m_i moves, there are 
    t / m_i
possible outcomes (unique outcomes not guaranteed). 

In <ControverterBot>, a non-automated agent chooses its move in a <GameControverter> by a scheme in the 
function<ControverterNet.agent_decision(agent identity,node identity,other agent moves)>. The agent could 
make a move based on one of these 12 objective functions: 
- MAX MIN (payoff of agent move) 
- MAX MAX (payoff of agent move) 
- MAX MEAN (payoff of agent move) 
- MIN  (MIN  MIN (every other agent's payoff w.r.t. agent move))
- MIN  (MIN  MAX (every other agent's payoff w.r.t. agent move))
- MIN  (MIN  MEAN (every other agent's payoff w.r.t. agent move))
- MIN  (MAX  MIN (every other agent's payoff w.r.t. agent move))
- MIN  (MAX  MAX (every other agent's payoff w.r.t. agent move))
- MIN  (MAX  MEAN (every other agent's payoff w.r.t. agent move))
- MIN  (MEAN  MIN (every other agent's payoff w.r.t. agent move))
- MIN  (MEAN  MAX (every other agent's payoff w.r.t. agent move))
- MIN  (MEAN  MEAN (every other agent's payoff w.r.t. agent move))

Additionally, each of these 12 objective functions can consider either the immediate or the cumulative 
payoff values. 

The multi-agent setting, S, is practically a chain of q decision junctions. At every timestamp, every agent 
makes q moves, one at every node in this chain. At every node during a timestamp, all agents make their 
move for that node's <GameControverter>, and the <GameControverter> generates another instance, with different 
possible agent moves and payoffs. This multi-agent setting S is continually variable: there is a strong 
probability that at two different timestamps, the same node n_i will be a <GameControverter> with much different 
payoff ranges for the agents. 

The objective of <ControverterBot> is for one of its non-automated agents A to use a PRNG that yields it the 
highest value, in terms of accumulated value from its payoffs, with respect to the other agents. 
"""
class ControverterBot(ControverterNet): 

    def __init__(self,amap:dict,tmap:dict,N:NodePath,prg,allow_agent_move_knowledge):
        super().__init__(amap,tmap,N,prg,allow_agent_move_knowledge,\
            is_correlation_variable=True)
        return 

    @staticmethod 
    def generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg,allow_agent_move_knowledge=False,\
        is_correlation_variable=True): 
        # bot runs faster with no more than 10
        assert num_agents * path_size <= 10 

        q = ControverterNet.generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg,allow_agent_move_knowledge,\
        is_correlation_variable=True)

        return ControverterBot(q.amap,q.tmap,q.N,q.prg,\
            q.allow_agent_move_knowledge)