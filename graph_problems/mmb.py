from quant.middleman_graph import * 

"""
A network featuring one buying agent, one original selling agent, and 
a variably increasing and decreasing number of middle agents between the 
buying and original selling agents. 

    *Buying Agent Objective* 
The buying agent is to purchase x units of a product from the selling network, 
each unit coming from either the original selling agent or any one of its 
middle agents. 

    *Relevant Network Variables* 
Network middle agents are programmed to be terminal. The relevant variables  
are listed below. 
- original unit price of original seller 
- unit shelf life 
    - the number of timestamps a seller has to sell a unit, before it 
      is disposed as a loss. 
- reproduction rate of a seller
    - the number of units a seller S directly sells to the buyer before 
      another middle agent spawns as an intermediate seller for S. 
- seller lifespan 
    - the number of units that can be disposed before seller is terminated 
      from bankruptcy. 

    *Seller Spawning Process* 
The spawning process, where a seller S 'reproduces' an additional seller, produces a 
<MiddleAgentSeller> S1 instance that bases its unit price on the original unit price 
P of a seller. The original unit price of S1 is, by default, P * m, m a float 
in the range [1+0.02,1+0.15). Agent S1 is assigned a PRNG that is an LCG, based on 
four output values from its source seller's PRNG. 

By default, network starts off with one original seller and x number of middle 
agent sellers spawned from that original. The integer x is in the range of 
DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE. 

    *Seller Selling Unit Price* 
A seller's unit price is subject to a downward fluctuation, depending on the 
seller's selling performance. This rule of downward fluctuation is essentially 
a trait of price wars. Specifically, after a timestamp where the buyer buys a 
unit specifically from seller S_k, all members of the product chain to seller S_k 
benefit. The product chain of seller S_k consists of <MiddleAgentSeller>s,
    <S_k,S_{k-1},S_{k-2},...,S_0>, 
such that S_{k-1} spawned S_k, S_{k-2} spawned S_{k-1}, and so on, up through 
S_0, the original selling agent. 

Selling agents not part of the product chain lose one timestamp of their shelf 
life. This loss of a timestamp does NOT reset to full for any agent if that agent 
were to sell a unit at a future timestamp. For example, consider this sequence of 
sells and no-sells, each pertaining to a timestamp in a contiguous time range. 

    <SELL,NO,SELL,NO,NO,NO,SELL>. 
    - The unit shelf life is four. There are four no-sells, so pertaining seller 
    loses one unit during this time range. 

When a seller does not sell for a timestamp, seller deducts a percentage r 
from its current price P, for an updated price P * (1 + r). Default percentage range 
is DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE = [-0.1,-0.02]. A seller can deduct the 
price of a unit x times, x the unit shelf life. If a seller dumps a specific unit, 
it sets the initial price of the next unit at the initial price of all units it sold 
or dumped before that timestamp.  

    *Buyer Mechanics* 
At every timestamp, buyer moves through the network from the constant starting node, 
edge by edge through the <MiddleManNetwork>, until at least one of these conditions are 
satisfied: 
- buyer reaches every node of graph. 
- buyer has reached the maximum number of seller candidates.  
- buyer has travelled a number of edges equal to the number of edges of the graph, 
  uniqueness not required. 

Buyer chooses to buy from the seller, out of the candidates it reached, with the 
cheapest price for the unit. 

    *Seller Termination* 
The original seller can never be terminated since the buying agent must always 
purchase from either it or a middle agent seller connected to the original. A 
seller can be terminated if it goes bankrupt, as already mentioned. 

In order for the network to maintain a fresh set of sellers such that no seller 
becomes indeterminately dominant, the network 'spontaneously terminates sellers 
that have sold some q units, q in the range R. By default, R is based on 
DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE. R is the range 
    [DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE[1] * 1.5,DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE * 2) = 
    [16+8,16+16) = [24,32). 


    *Important Aspects* 
The <MiddleManNetwork> is based on class<JammingGraph>. Every seller is assigned a node in 
this graph. The farthest seller from the buyer, at any given time, is the original seller. 
Every time a seller spawns another <MiddleAgentSeller> S', the <JammingGraph> adds a subgraph 
to the existing network. Seller S' is assigned a node of this subgraph. This alteration is 
a positive change in network size. When a seller is terminated due to bankruptcy or selling 
dominance, its assigned node is also deleted from the graph. The <MiddleManNetwork> is always 
a connected graph; every node of the graph is reachable by any other node. Method<JammingGraph.one_jam> 
of adds a subgraph to the network, in a way that does not disconnect any of its nodes. Similarly, 
when a seller node is deleted from the graph, the network uses its assigned PRNG to reconnect any 
node disconnected because of that deletion.  
""" 
class MiddleManBot(MiddleManNetwork): 

    def __init__(self,buying_agent:MiddleAgentBuyer,unit_price,unit_shelf_life,\
        reprod_rate,seller_lifespan:int,jg:JammingGraph,prg,verbose:bool=False):

        super().__init__(buying_agent,unit_price,unit_shelf_life,reprod_rate,\
            seller_lifespan,jg,prg,verbose) 
        return 

    @staticmethod 
    def generate_instance(jamming_graph_type,unit_price,\
        allow_buyer_memoryless_navigation:bool,prg1,prg2):
        
        mm = MiddleManNetwork.generate_instance(\
            jamming_graph_type,unit_price,\
            allow_buyer_memoryless_navigation,\
            prg1=prg1,prg2=prg2)

        return MiddleManBot(mm.buying_agent,mm.unit_price,mm.unit_shelf_life,\
            mm.reprod_rate,mm.seller_lifespan,mm.jg,mm.prg,mm.verbose)