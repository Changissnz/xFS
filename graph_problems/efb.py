from graph_models.hg_obj_path_op import * 

DEFAULT_ENDS_FIXATED_BOT_NODESIZE_RANGE = [3,35] 

"""
Ends-Fixated Bot. 

Built on top of class<DIPathNavigatorHandler>, comprised of an 
<ObjectivePathTypeDI> (Objective Path, Type Directed Implication) and a 
<DIPathNavigator> (Directed Implication Path Navigator). 

            ** The Path **

A directed implication path is a directed graph with at least two nodes, a start 
node s (in-degree 0) and an end node t. 

The objective for the navigator is to make a sequence of decisions, comprised 
of a combination of 'support values' and node-to-node travel, to travel from 
start s to end t. 

The objective path is comprised of nodes, each associated with a float value 
used for "activation", allowance of navigator to pass through the node. 

NOTE: all node-associated values are positive real numbers. 

There are two kinds of activations: 
- single value 
- linear expression 

Both kinds present themselves as minimum-value threshold functions. 

Given a node n_i, its activation function F is for a nodeset N, s.t. 
n_i in N: 

- single: 
    U(n_j) >= v_j; S(n_j), v_j are real numbers, n_j in N. 
- linear expression: 
    U(n_j1) * v_j1 + ... + U(n_jk) * v_jk >= L;   S(n_jq),v_jq,L are real numbers, n_jq in N. 

U := positive support value from navigator for node n_j*. 

Every node n_i of objective path is also associated with an activation node n_a. Node n_a 
could be node n_i or another node n_j closer in spine-distance to end node t. 

NOTE: See file<graph_models.dir_imp_path> for a definition on what the spine for a 
      directed implication path is. 

Function F contains the values v_* and, in the case of linear expressions, L. 

            ** The Navigator ** 

The navigator operates by exactly one of open or closed info. In the case of open info., 
navigator is given the map M_q
    M_q: depended node of n_q -> (weight (if `linexp`) | minimum threshold value 
AND 
    float (if `linexp`) | None)
upon making contact with node n_q. This information allows for navigator to calculate 
minimal support values to pass activation function of n_q; in other words, the support 
values it provides is most cost-efficient. 

If navigator operates by closed info., navigator will have to rely on its history of 
failed support values it provides to n_q. For every subsequent attempt to pass n_q, 
navigator chooses a float greater than its latest maximum failed support value it 
previously provided. If navigator has never encountered n_q, it simply chooses a PRNG 
value in the node-value range specified during instantiation. 

Navigator, throughout its course of travel, has a map 
    M: node n that it traveled on -> navigator's support value for n. 
Map M is equivalently an ordered sequence S (node,node support value). This ordered sequence 
S allows navigator to backtrack to a previous node during its traversal. 

At a timestamp t, navigator can choose to move forward from the node it is at, n_c, to a node 
n_q that is closer in spine-distance than n_c to end node t. If it does choose to move forward, 
it moves to node n_q that is one of the nodes of n_c's out-neighbors. 

Upon contacting n_q, navigator must provide support value s_q to n_q. The activation function F_q 
of n_q determines if navigator, by this support value s_q, and its node-support sequence S, 
passes. S does not have to contain support values for all depended nodes of F_q. If n_x is a 
depended node in F_q and S does not have a support value for it, support it gives is 0 for 
function F_q to process. 

If navigator fails, one of two things occurs, 
- immediate effect of failure: navigator does not proceed to n_q. Navigator is pushed back 
    to the node where it came from. 
- pending effect of failure: navigator proceeds to n_q. If navigator tries to pass through another 
    node n_a (activation node for n_q) with any support value and node-support sequence S, navigator 
    is denied entry and pushed back to node n_q. 

NOTE: The pending effect requires the activation node n_a of node n_q to not be identical. 

            ** Decision Pipeline ** 

The simplified pipeline of navigator decision-making:
- Navigator can choose to move forward to the next node, the head node if it is currently outside 
  of the path or out-neighbor n_q from its current node of location n_c. 
- If navigator moves backward, it goes to the most recent node it previously traveled, the node before 
  n_c. There is no activation function involved and thus no support value from navigator required for 
  moving backward. 
- If navigator moves forward, it provides support value U(n_q) and its node-support sequence S to F_q 
  of n_q. Navigator can fail (pending or immediate failure) or pass. 

Navigator is associated with two probability values for moving backward: P_b and P_f. These two probability 
values are used in conjunction with navigator PRNG decimal values in [0.,1.]. 
P_b := maximum threshold value for navigator to travel backwards. 
P_f := maximum threshold value for navigator to travel completely backwards to outside the path, 
       before start node s, once navigator travels backwards once. 

The decision pipeline for moving backward, with PRNG R: 
- R outputs decimal d0. 
- If d0 < P_b, navigator travels backwards. 
    - R outputs decimal d1. 
    - If d1 < P_f, navigator will travel backward for the next q timestamps to outside the 
        path (before start node s).  
"""
class EndsFixatedBot(DIPathNavigatorHandler): 

    def __init__(self,optdi,dipn,info_mode,verbose=False): 
        super().__init__(optdi,dipn,info_mode,verbose)

    @staticmethod
    def generate_instance(node_value_range,extra_edge_ratio:float,ratio_indirect_activation:float,\
        prior_dependency_ratio:float,activation_type:str,info_mode:int,prg): 

        assert is_valid_range(node_value_range,True,False) or is_valid_range(node_value_range,False,False) 
        assert node_value_range[0] > 0

        num_nodes = modulo_in_range(int(prg()),DEFAULT_ENDS_FIXATED_BOT_NODESIZE_RANGE)
        G = generate_directed_implication_path(num_nodes,extra_edge_ratio,prg,start_node_idn=0)

        node_value_range_map = {} 
        for i in range(num_nodes): 
            r0 = modulo_in_range(prg(),node_value_range) 
            r1 = modulo_in_range(prg(),node_value_range)

            if r0 == r1: 
                r1 = modulo_in_range(r0 + 1,node_value_range)

            r0,r1 = sorted([r0,r1]) 
            node_value_range_map[i] = (r0,r1) 
        
        optdi = ObjectivePathTypeDI.generate_instance(G,node_value_range_map,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,prg)

        dipn = DIPathNavigator.from_PathTypeDI(optdi,prg)
        return EndsFixatedBot(optdi,dipn,info_mode,verbose=False)