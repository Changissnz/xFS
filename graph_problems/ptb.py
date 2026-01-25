from quant.pd_graph import * 

"""
Poison Trace Bot. 

Poison Trace Bot is a construct with rather simple rules, outside of the computation 
necessary to transform a <PoisonModelSNT> n x n square matrix through its n^2 reactions. 

These simple rules do not grant any <PoisonTarget> the potential to calculate with 
certainty and ahead of time the <PoisonSource>s that deliver poison to it through a 
network T, a multi-rooted tree. The roots are the <PoisonSource>s instances, and the 
leaves are the <PoisonTarget>s. 

At any single point in time, a <PoisonTarget> can be poisoned by exactly one <PoisonSource>. 
A <PoisonSource> S_i has access to k_i poisons. S_i delivers poison through T to a 
<PoisonTarget>. For a target T_j, S_i will also use the same path P_ij to deliver poison 
to T_j. This path is computed before the start of the simulation. 

The steps a <PoisonSource> S_i takes to poison a <PoisonTarget> T_j: 
- <PoisonSource> chooses a poison p_i out of its k_i poisons. 
- For every timestamp until poison p_i reaches node of T_j, p_i travels one node along 
  path P_ij. 
- Once p_i reaches node of T_j, p_i is registered by T_j. T_j recognizes its state of 
  being poisoned. 
- For every timestamp afterwards with regards to p_i poisoning T_j, p_i `reacts` in T_j. 
  A poison of square matrix n x n will take n^2 reactions, one reaction per timestamp, 
  until completion, such that T_j is terminated. 

  During the course of these reactions, for timestamp t_q, if T_j is able to predict the 
  reaction, a square n x n matrix, from the previous (q -1) reactions and the initial 
  poison state matrix M, then T_j is able to halt the poison from terminating it. 
- A <PoisonSource> uses a <PoisonPath> instance to deliver a poison to and react it in a 
  target. At any single point in time, a <PoisonSource> can have at most one <PoisonPath> 
  instance active. 
---------------------------------------------------------------------------------------------

The steps a <PoisonTarget> T_j takes when a poison p_k hits it: 
- T_j can attempt to guess the poison by iterating through its database, a map of 
   poison idn -> source idn -> PRNG used by source to execute poisoning (reaction chain)
  through a trial-and-error process. 
- This trial-and-error process goes as such: 
    - at a timestamp, T_j chooses a (poison identifier, source identifier) hypothesis from 
      its database. The hypothesis selection process is this iteration design: 
      * T_j chooses a source identifier from its <PoisonDB>. 
      * T_j iterates through every poison associated with the source identifier, before moving 
        on to another source identifier. 
    - T_j refers to its `poison_reaction_log` of square matrices (initial poison and subsequent 
      reactions). T_j attempts to replicate the same reaction chain, starting with initial poison 
      matrix M, using the PRNG associated with (poison identifier, source identifier). 

      * there are two variants in this guessing, due to the two types of poisonings that a 
      <PoisonSource> can conduct: `expressive` or `inexpressive`. If poison is expressive, 
      all elements of `poison_reaction_log` will be matrices. If poison is inexpressive, 
      only the first element of the log is a matrix (initial poison), and the remaining are 
      categorically None. If poisoning is expressive, T_j will sequentially calculate a replication 
      of each reaction, and if a replication R' does not equal a reaction R at some index 
      in the `poison_reaction_log`, quits computing on hypothesis (poison identifier source identifier). 
      However, with inexpressive poisons, T_j calculates every replication, that is, the length of 
      the `poison_reaction_log` to output the predicted reaction M_x for the current timestamp.  

      In technical terms, `expressive` poisons will yield less cost to a <PoisonTarget>. Every 
      replication of a reaction a <PoisonTarget> calculates is 1 additional guess (a negative value). 
      So a <PoisonTarget> would not have to calculate all replications of a hypothesis 
      (poison identifier, source identifier) in order to determine if the hypothesis is true. 
      Rather, it would move on to another hypothesis. 

- In this iteration of hypotheses, (poison identifier, source identifier), T_j could decide to 
  stop guessing and conduct a `backtracking` operation using a <PoisonBacktracker>. A 
  <PoisonBackTracker> does these two things upon successful completion of traveling the 
  path P_ij. 
1. It records half of the nodes of path P_ij, specifically the latter half of P_ij that includes 
  node of T_j. 
2. It replicates the PRNG used by source S_i for poison p_k to react.   

Item 2 is used by the target T_j's successors to accurately predict poison p_k from source S_i. 
Item 1 is used by target's successors to implement pseudo-accurate predictive capabilities. Successors 
can place a <PoisonRelay> onto a node in the nodeset. When a <PoisonPath> crosses this <PoisonRelay>, 
this <PoisonRelay> outputs a set of suspected <PoisonSource>s. This set contains the actual source, as 
well as other sources in cases in inaccurate <PoisonRelay> (see code for specifics). The information 
that <PoisonRelay> communicates to its <PoisonTarget> owner is advantageous for a <PoisonTarget> to 
more quickly narrow down possible <PoisonSource> candidates, in cases where it has to make a hypothesis 
on (poison identifier, source identifier). 

When a <PoisonTarget> decides to backtrack, it is guaranteed to be terminated, via poison. The 
relevant information gets passed to its successor. Thus, the decision to backtrack is a last resort. 
In the beginning of every simulation, <PoisonTarget> does not have any information on 
(poison identifier, source identifier, corresponding PRNG) triplets. It will have to backtrack for 
every novel one it encounters. 

In the general sense, a <PoisonTarget> follows principles of evolutionary algorithms, using the 
knowledge of its predecessor's <PoisonDB>s. 

Decision-making pipeline for <PoisonTarget>
------------------------------------------- 
At every timestamp, a <PoisonTarget> takes these actions: 
- if poisoned, <PoisonTarget> can 
    - attempt to guess the current reaction through the guessing procedure 
    described above (possible termination) 
    - backtrack for information on (poison identifier, source identifier, corresponding PRNG) 
      (guaranteed termination) 
- add relay (if number of relays has not exceeded maximum allowance) or move relay from one 
  node to another. 
----------------------------------------------------------------------------------------------------

Simulation was designed to test the pre-emptive defensive mechanisms of a <PoisonTarget> that can 
use some r number of relays to anticipate sources of poison. After a <PoisonTarget> has acquired 
knowledge of all (poison identifiers, source identifiers, corresponding PRNG) triplets, its only 
real objective is to position its <PoisonRelay>s in formations that yield the greatest predictive 
accuracy on sources of incoming poison. 
"""
class PTBot(PoisonDeliveryNetwork): 

    def __init__(self,G:defaultdict,source_map,target_map,verbose:bool=False):  
        super().__init__(G,source_map,target_map,verbose)
        self.auto_agent = None 

    """
    used in <SimulationSolutionSearch> to search for best PRNG solution 
    """
    def set_one_auto(self,q): 
        assert q in self.target_map  
        self.auto_agent = q  
        return

    @staticmethod 
    def generate_instance(num_source_nodes,num_targets,num_poisons,poison2source_ratio_range,poison_matrix_square_dim,\
        expressive_mode,prg,seed_pair,relays_per_source=2,relay_accuracy_range=[0.75,0.9],verbose:bool=False): 

        random.seed(seed_pair[0]) 
        np.random.seed(seed_pair[1]) 

        pdn = PoisonDeliveryNetwork.generate_instance(num_source_nodes,num_targets,\
            num_poisons,poison2source_ratio_range,poison_matrix_square_dim,\
            expressive_mode,prg,relays_per_source=relays_per_source,\
            relay_accuracy_range=relay_accuracy_range,verbose=verbose) 
        return PTBot(pdn.G,pdn.source_map,pdn.target_map,verbose) 