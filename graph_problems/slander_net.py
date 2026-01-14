from quant.mutable_ce_net import * 

"""
A simulation fixating on vector differentials calculated in a multi-agent 
setting. The multi-agent setting is a network that is a directed graph 
comprised of n agents, connected to each other by a combination of three 
kinds of edges (ports):  
- R-port: reactive port, source agent relays differentials from T-port 
           activity to target agent. 
- S-port: source port, source agent receives information on target agent, 
           represented as a vector for every timestamp. 
- T-port: transmission port, source agent transmits information (vectors) it 
           obtained on its S-ports. These vectors may not be the actual 
           vectors source agent obtained. A vector derivative function 
           is used, in conjunction with a variance value in [0.,1.], to 
           reclassify the vector into a different category. A new vector 
           is formed from this re-classification scheme, one that uses 
           an unsupervised learning procedure called <BallComp>. 

Slander Net is so named because the mathematical functions and network 
design attempt to emulate the effect of transmitting mutable objects, 
specifically vectors. The Game of Telephone is similar in the vein of 
transmitting mutable information. Slander Net has more pre-defined 
structure to it. The word "slander" is used to describe the origin and 
quality of transmitted information. The S-ports that every agent has 
link to a database containing information of the S-port agents' activity. 
Agent activity is one n-vector from one agent at every timestamp, and these 
n-vectors sequentially accumulate into a matrix of n columns. Agent activity is 
'assumed' to be private and known only by the agent. So regardless of 
whether the information an agent retrieves through an S-port on some 
other agent is true or not (the information is, at source), transmitted information 
is slander in the case of violating privatization through S-port retrieval, 
and probably slander (if the agent has a variance measure in range (0,1]) 
in the case of a source agent transmitting a vector derivative,of the 
actual vector from subject agent, to T-port agent. 
------------------------------------------------------------------------------
* Activity phase: 
At every timestamp, every agent produces one n-vector. 
* Source retrieval phase: 
For every agent A, A retrieves vectors on agents listed in its S-ports.
* Transmission phase: 
For every agent A, A calculates a vector derivative V_s' for every vector 
V_s from its S-port agents. A sends this vector derivative to every one of its 
T-port agents. Every T-port recipient A_t sends back a differential d calculated 
as 
    d = || S(A_t) - V_s' ||; 
    S(A_t) is V_s' if agent A_t does not have an S-port to agent s, 
                   otherwise V_s. 
Agent A subtracts its score to every response differential it receives in this 
transmission phase. 

All agents that received vector derivatives V_s'' into a map M, 
    M: subject agent -> accumulated differential. 
The vector derivatives V_s'' are 
    V_s'' = || S(A_t) - V_s' ||    if agent A_t does not have an S-port 
                                   to agent s, 
            ||V_s'||                otherwise.

* Reaction phase: 
For every agent A, A sends M[B] to every R-port. 
------------------------------------------------------------------------------ 

This network was conceptualized using barebones structural units. Every agent 
has, at its disposal, two maps used to make port delta decisions (opening or 
closing ports). These maps are 
- communication delta (response from its T-port activity): 
    source agent -> target agent -> (resistance)::float. 
- execution delta (response from other agents' R-port activity) 
    source agent -> (positive resistance)::float. 

For a network of n agents, there can be at most n autonomous agents. These 
q autonomous agents can, at every timestamp, make exactly one port delta. 
These autonomous agents use function<close_port__max_decision> and 
function<close_port__max_decision> to estimate the best agent to close/open 
port to. These functions are not guaranteed to produce the best ordering 
of candidate ports. These two functions are used by an autonomous agent via 
its pseudo-random number generator for port delta decision. 

Objective #1 for an autonomous agent is to maximize its score over k timestamps. 
"""
class SlanderNetBase(MutableCEAgentNetwork): 

    def __init__(self,cea_map,auto_agents,prg):
        super().__init__(cea_map,prg,True) 
        self.set_auto_agents(auto_agents)  

