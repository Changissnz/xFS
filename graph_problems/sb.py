from quant.strangle_graph import * 

"""
Strangle Bot. 

Featuring two agents competing with each other for control over a connected graph G. 
The two agents are <StrangleForm> and <StrangleSubject>. <StrangleForm> has an attribute, 
variable<force_per_node_range>, that is the possible range of force it can apply to every 
node that it is strangling. <StrangleSubject> has knowledge of this variable<force_per_node_range>, 
helping it make hypotheses on breaking force to free nodes in strangleholds. 

At every timestamp, <StrangleForm> moves first. <StrangleForm> is given an 
arbitrary k node entry points into G. <StrangleForm> then conducts its move: 
- if <StrangleForm> is not currently strangling any nodes, <StrangleForm> 
  enters into the k node entry points. Those k nodes are strangled by <StrangleForm>, 
  and constitute a strangling body by the <StrangleForm>.
* A strangling body is initialized with k nodes, each of these nodes part of a depth-first 
  search (DFS) process. At every timestamp, every one of these DFS processes move 1 node. 
  The DFS processes uses <USGController> as the operator. And the operator is set to 
  `no_duplicate_touch_nodes=True` for each process, as well as the combined processes. 
  This means that when a DFS process P1 touches a node that another process P0 has already 
  touched, P1 terminates. This is a technicality of this bot's strangling agent, <StrangleForm>.
  See variable<StrangleForm.usgcs> for the map of all of its strangling bodies. 
- if at the end of the previous move, <StrangleSubject> breaks stranglehold of at least one 
  node, <StrangleForm> also enters into the k node entry points, this entry another strangling 
  body. 
- For every strangling body B that <StrangleForm> is currently operating, <StrangleForm> 
  moves all of its active DFS processes, yielding it some arbitrary b >= 0 new nodes of G 
  it now strangles. 
- If <StrangleForm> has strangled all nodes of G after its move, then bot terminates in victory 
  of <StrangleForm>. 
* For every node n_i that <StrangleForm> has placed a stranglehold on, <StrangleForm> uses a force 
  f_i on it; force_per_node_range[0] <= f_i <= force_per_node_range[1]. Force f_i is deducted from 
  the <StrangleForm>'s energy store. If node n_i is broken by <StrangleSubject>, <StrangleForm> 
  would have to calculate a new force f_j if it ever places a stranglehold on it. 
- Additionally, if mode `enable_consumption` is set to True, <StrangleBot> would consume some arbitrary 
  ratio r of nodes N it is currently strangling. Every one of the nodes in N must have been put in at 
  least DEFAULT_STRANGLER_HOLD_FREQUENCY_CONSUMPTION_MIN_THRESHOLD strangleholds. 
  * This requirement was implemented because a node that has been put in at least that many strangleholds 
    is considered a "hot" node of contention, oscillating between being put in a stranglehold and being 
    freed by the <StrangleSubject>, thus its candidacy to be consumed so that there would be no more 
    contention over the "hot" node.  
  These consumed nodes N_c would be subtracted from G to produce G_, and if G_ is not a connected graph 
  (graph with <= 1 component), then edges are arbitrarily drawn to connect G_ into one component. The 
  new graph of contention is G_.  

Then <StrangleSubject> moves. <StrangleSubject> first calculates some k communities, each a nodeset 
of nodes typically connected to each other; k <= |G|. <StrangleSubject> is then relayed information 
from <StrangleEnv>, based on the `info_mode`; see description for class<StrangleFormInfo> for more 
details. Using this information, <StrangleSubject> chooses a community C out of the k communities 
and attempts to calculate an appropriate total breaking force F used to break all nodes of C out 
of strangleholds. 
* Information modes 0-3 correspond to information that positively correlates in 
  accuracy to the mode's absolute value (0 the lowest quality information). 
<StrangleSubject> applies force F onto community C, by the schematic of 
function<default_strangle_breaking_function>. Force F is deducted from <StrangleSubject>'s energy 
store. 

At every timestamp, if the energy of agent <StrangleForm> or <StrangleSubject> falls below a positive 
float, agent loses. If both agents' energy falls below positive, simulation ends with tie. Otherwise, 
the remaining agent wins. 
"""
class StrangleBot:  

    def __init__(self,strangler,strangle_subject,node_weights,info_mode,prg,\
        enable_consumption:bool=False,verbose=False): 
        super().__init__(strangler,strangle_subject,node_weights,info_mode,prg,\
        enable_consumption=enable_consumption)

    @staticmethod
    def generate_instance(strangler_force_assignment_type,info_mode,prg,strangler_energy=10**6,\
        strangle_subject_energy=10**6,enable_consumption=False): 

        senv = StrangleEnv.generate_instance(strangler_force_assignment_type,info_mode,prg,\
            strangler_energy=strangle_energy,strangle_subject_energy=strangle_subject_energy,\
            enable_consumption=enable_consumption)
        return StrangleBot(senv.strangler,senv.strangle_subject,senv.node_weights,\
            senv.info_mode,senv.prg,enable_consumption)