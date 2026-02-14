from quant.hscript_graph import * 

"""
Homo Frame Bot is an automaton that emphasizes the concept of homomorphism, 
structure-preserving map between two spaces. 

There is exactly 1 administrator (an instance of <HomoScriptAdmin>) and n 
agents (<HomoScriptAgent>s). Exactly n requirements, each assigned an integer, 
are assigned for the n agents. Every agent is originally assigned a unique requirement; 
see the variable <HomoScriptAgent.chosen_req>. But an agent can execute a requirement 
different from its assignment. More on this will be explained. 

Every requirement R_i is a sequence S of integers, S[0] = R_i. 

The administrator has a map M_d of demands, 
    M_d: agent idn -> requirement idn -> expected path. 
 
These demands are supposed to be structure-preserving, homomorphic in other words, for some 
unspecified objective of the administrator. Every agent A has a map, 
    M_r: requirement idn -> wanted path. 

        ** Default agent activity ** 
        ---------------------------- 
For an agent A that is supposed to execute requirement R_i, agent A takes path P_i = M_r[R_i]. 
Administrator then uses a sequence metric function F (see function<levenschtein.simple_string_cmp_metric>) 
to calculate the difference D between P_i and Q_i, Q_i = M_d[A][R_i]. Deduct D from the score of 
agent A. This deduction is a penalizing mechanism by administrator to deal with differences between 
its requirement expectations with respect to each agent. The naming of this bot, Homo Frame, is due 
to this penalizing mechanism that is based on administrator demands, M_d. 

        ** Agent role divergence ** 
        ---------------------------
At every timestamp, agent A can attempt to swap its (<chosen_req>,wanted path) with that of another 
agent B. Let C(A),C(B) be the chosen requirements for A and B,respectively. If swap occurs, then 
the agent A executes (requirement C(B), path P0 = B.M_r[C(B)]) and agent B executes 
(requirement C(A), path P1 = B.M_r[C(A)]). Administrator will deduct from A based on its swapped path, 
F(P0,M_d[A][C(B)]) and likewise for B. 

NOTE: in the case where `open_info` mode is set to False, the decision by agents A and B to swap is 
      through arbitrary comparison, that is, comparisons of those agents' PRNG output.
      See function<HomoScriptNetwork.swap_decision> for more details. 

      In the case where `open_info` mode is True, agent A will want to swap if there is a score 
      improvement (decrease in administrator deduction), and likewise for agent B. 

If agent A wants to swap with another agent B, and agent B does not, then agent A can diverge from 
its assigned requirement by 'imitating' agent B. In cases of imitation, administrator will deduct 
from A based on F(B.M_r[C(B)],M_d[A][C(B)]) instead. 

        ** Administrator deductions on imitation **
        -------------------------------------------  
The first kind of deduction, path execution deduction, has just been mentioned. Another kind of 
deduction has to do with 'imitation' deduction. For an imitating agent A of agent B, administrator 
deducts 
    F(B.M_r[C(B)],M_d[A][C(B)]) / 2 
from agent B after agent A imitates B. 

        ** Administrator deductions on missing requirements ** 
        -------------------------------------------------------
Administrator expects for the agents to complete the n requirements every timestamp. This expectation 
remains even when one or more of the original n agents terminate due to score reaching 0 or below. 
The remaining agents are given the opportunity to take up extra roles for each of the terminated 
agents' assigned requirements, a maximum of one remaining agent for one terminated agents' assignment 
requirement. Score deduction proceeds according to F(A_e[R_t],M_d[A_e][R_t]); A_e the agent that 
takes up a terminated agent's role and R_t the terminated role. Additionally, even when none of the 
agents have been terminated, agent imitation of another implies a missing requirement. Deduction also 
occurs in these instances. For every missing requirement R_i, administrator calculates the cumulative 
sum of R_i's path lengths, 
    U =   SUM      |M_d[a][R_i]|. 
       a in agents 
Then administrator deducts |U| / |agents|^2 from every agent. 

______________________________________________________________________________________________________
 
        *Automaton synopsis*
        --------------------
For every active timestamp of Homo Frame Bot, 
- remaining agents decide on the (requirements, paths) to take, via default or swap or imitation. 
- remaining agents decide on taking extra roles to fulfill terminated agents' requirements. 

______________________________________________________________________________________________________

Simulation focuses on the economical decision-making of n agents to fulfill n requirements from an 
administrator. The administrator has a map of demands, expectations for the agents to fulfill those 
requirements. This relates to the theme of homomorphisms. 

NOTE: 
Bot can run in either unweighted or weighted mode. In weighted mode, the deduction process is 
different. For a delta score map, 
    D: agent idn -> delta, 
first have every non-terminated agent output a value from its PRNG. These values are normalized 
to sum up to 1.0, 
    W: agent idn -> weight. 
Sum up the delta from D for float S. Then the weighted delta score map is 
    D_w: agent idn -> W[agent idn] * S. 
"""
class HomoFrameBot(HomoScriptNetwork): 

    def __init__(self,admin,agents,prg,info_mode_is_open:bool=False,verbose:bool=False): 
        super().__init__(admin,agents,prg,info_mode_is_open,verbose) 
        return
        
    @staticmethod
    def generate_instance(num_agents,prg,agent_score,open_info): 
        hsn = HomoScriptNetwork.generate_instance(num_agents,prg,agent_score,open_info) 
        return HomoFrameBot(hsn.admin,hsn.agents,hsn.prg,hsn.open_info,hsn.verbose)