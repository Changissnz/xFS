from quant.dual_obj import * 

"""
NOTE: 
See file<quant.dual_obj> for more information on bot details. 

Bot is a subclass of class<DualEnvTypeHL>. Centers around a dual agent 
A with a sequence S of demands. Every demand is comprised of two 
subdemands: 
- independent subdemand (belonging to A) 
- third-party subdemand (belonging to environment [external] of A). 

Every subdemand is a ('category','label'). 

For a sequence S of length n = |S|, agent A is to complete S in any order. 
The procedure goes like so, until all demands of S are completed: 
- agent A chooses an i'th element s_i of S to complete at timestamp t.  
- At timestamp t, agent A conducts third-party subdemand of s_i. Agent A 
  then conducts its independent subdemand of s_i. 

Agent A operates in an environment that is essentially a Hypergraph, with each 
node being a lattice graph of more than 1 node. Suppose there are c categories, 
each category a Hypergraph node. Every one of these categories c_i is associated 
with x labels L_i = {l_i1,l_i2,...,l_ix}. These x labels are 'heads' for x paths 
in a two-dimensional square lattice graph. Every one of these paths has a 'head' 
(the label) and a tail (the label objective). All lattice graphs are disjoint from 
each other. This implies that if a label l is part of two or more categories, 
a path for that label, w.r.t. category c, is a disjoint path from the lattice graph 
of the other categories. 

Here are specifics (copied from the comments of method<DualEnvTypeHL.move_one>) on 
agent A's decision-making process: 
[0] dual agent chooses next index and associated independent demand 
[1] environment chooses 3rd-party demand of equal index 
[2] Environment offers n 'labels' for dual agent to choose one. Every label is a 
  Hypergraph subnode (a node on a lattice graph). 
[3] dual agent chooses one of these 'labels' l, and proceeds to traveling the Hyper-Lattice 
  graph, from l to that third-party demand's subnode. This path the agent takes is its 
  chosen path. 
NOTE: the dual agent's chosen path and the expected path can be different. A non-zero difference is 
      usually the case, given the PRNG generation scheme. The expected path for a label l of category c 
      (a category is synonymously a Hypergraph node) is simply a path P from the 'head' to the 'tail' 
      of that label]. The dual agent's chosen path does not have to start at that expected path's head. 
      It starts at a 'head' of one of the `labels` it is given by the environment. Agent traverses 
      Hyper-Lattice graph from that lattice node, through the smallest number of Hypergraph nodes between 
      that lattice node and the third-party demand's label, to the Hypergraph node (category) of the 
      third-party demand's category. Then agent proceeds to travelling a path in that category to meet 
      the label objective. 
      
      Negative weights are accumulated onto the nodes of difference between the expected and chosen path.  
      For an independent demand, agent simply takes the label objective of the demand's category. 
[4] Register the node difference of that 3rd party demand. Environment updates node negative weights 
    for nodes N = chosen_path - expected_path. 
[5] agent conducts independent demand. 
"""
class DualRoleBot(DualEnvTypeHL): 

    def __init__(self,dual_agent,ce_effect,third_party_demands,option_size_range,prg): 
        super().__init__(dual_agent,ce_effect,third_party_demands,option_size_range,prg) 

    def __next__(self): 
        return self.move_one()

    @staticmethod 
    def generate_instance(prg):
        D = DualEnvTypeHL.generate_instance(prg) 
        return DualRoleBot(D.dual_agent,D.ce_effect,D.third_party_demands,D.option_size_range,D.prg) 