from .cee_map import * 
from .levenschtein import simple_string_cmp_metric
from morebs2.numerical_generator import prg_to_prg__LCG_sequence
from collections import Counter 

DEFAULT_DUAL_ENV_HG_NODESIZE_RANGE = [10,24] 
DEFAULT_DUAL_ENV_HG_CONNECTIVITY_RANGE = [0.17,0.37] 
DEFAULT_DUAL_ENV_HG_BASE_NODESIZE_MULTIPLIER = 2.7 
DEFAULT_DUAL_ENV_HG_BASE_NODE2NODESET_SIZE_RANGE = [2,6]

DEFAULT_DUAL_ENV_DEMAND_SIZE_RATIO_RANGE = [0.15,0.5] 
DEFAULT_DUAL_ENV_OPTION_SIZE_RANGE = [4,12] 

def assert_HyperGraph_nodepair_existence(hg,nodepair_seq): 
    assert type(hg) == HyperGraph

    for n in nodepair_seq:
        assert len(n) == 2  
        n0,n1 = n[0],n[1]
        assert hg.nodepair_exists(n0,n1)

"""
Container that stores the costs for a <DualRoleAgent> to fulfill requirements 
for two roles:
- independent (self)
- 3rd path (other).
"""
class DualCostsTypeHL:

    def __init__(self):
        self.independent = 0 
        self.third_party = 0

        self.negative_node_weight_map = Counter() 

    """
    calculates 3rd party path costs and updates `third_party` variable. 
    """
    def register_agent_path__3rd_party_req(self,agent_path:list,expected_path:list):
        assert type(agent_path) == list == type(expected_path)

        s0 = simple_string_cmp_metric(agent_path,expected_path)
        s1 = simple_string_cmp_metric(expected_path,agent_path) 
        self.third_party += (s0 + s1) 
        return

    """ 
    calculates independent path costs, the summation of all associated 
    negative weights for every node of `agent_path`
    """
    def register_agent_path__independent_req(self,agent_path:list):
        assert type(agent_path) == list 

        c = 0 
        for n in agent_path: 
            c += self.negative_node_weight_map[n] 
        self.independent += c
        return

    def update_negative_weights(self,negative_weights:Counter): 
        assert type(negative_weights) == Counter 

        self.negative_node_weight_map = self.negative_node_weight_map + \
            negative_weights
        return 

    def __str__(self): 
        S = "independent: {}\n".format(self.independent)
        S += "third party: {}\n".format(self.third_party) 
        S += "negative weight counter\n\n{}\n".format(self.negative_node_weight_map)
        return S 

"""
A dual role agent that is specially programmed for decision environments that center on 
<PRClassExpectedEffectTypeHL>. The associated <PRClassExpectedEffectTypeHL> instance 
(not contained w/in this agent's code) offers traversal routes for agent to satisfy 
specific requirements, given as variable<independent_demands>. For every i'th 
demand this agent is to conduct, chosen by method<next_move>, it must also conduct 
the i'th 3rd-party demand. 

There are an equal number of 3rd-party demands and independent demands.
"""
class DualRoleAgentTypeHL: 

    def __init__(self,independent_demands,prg):  

        # list, element is (category,label) 
        self.independent_demands = independent_demands
        self.set_prg(prg)

        self.current_demand = None 
        return

    def set_prg(self,prg):
        assert type(prg) in {MethodType,FunctionType}
        self.prg = prg

    def next_move(self): 
        l = len(self.independent_demands)
        if l == 0: return None,None 

        i = int(self.prg()) % l 

        self.current_demand = self.independent_demands[i] 
        return i,self.independent_demands.pop(i)

    def select_option_for_3rd_party_demand(self,actual_label,labels): 
        # case: actual label is that of current demand. Choose it to 
        #       avoid non-zero costs. 
        if actual_label == self.current_demand[1]: 
            return actual_label 

        # case: choose a label using `prg` 
        i = int(self.prg()) % len(labels)  
        return labels[i]

    @staticmethod
    def generate_instance(hg:HyperGraph,num_demands,prg): 
        assert type(hg) == HyperGraph
        assert type(num_demands) == int and num_demands > 0 
        assert type(prg) in {MethodType,FunctionType}

        indep_demands = hg.select_nodepairs_with_PRNG(num_demands,prg)
        return DualRoleAgentTypeHL(indep_demands,prg) 

"""
An environment for a dual role agent (see class<DualRoleAgentTypeHL>) to operate in.
Environment contains a sequence of third-party demands, each demand a 
    (category::(HyperGraph node),label::(HyperGraph base node)). 
There is a <PRClassExpectedEffectTypeHL>, used by this environment, that has the 
associated HyperGraph, as well as the lattice graphs for each of these HyperGraph 
nodes. 

The order-of-operations for every active timestamp can be found in the comments of 
method<move_one>. 

This is the basic gist of the dual role problem the agent is forced to contend with. 
- At an active timestamp, agent chooses its i'th independent demand to conduct. 
- Agent must also conduct the i'th third-party demand that timestamp, as well. 
- If independent demand is the same label as the third-party demand, there is 0 cost. 
- Otherwise, agent must choose a route through the HyperGraph-Lattice to satisfy the 
  third-party demand. This route is not the expected route, so there are penalties 
  associated with conduct through that route; see 
  method<DualCostsTypeHL.register_agent_path__3rd_party_req> for more information 
  on the penalty mechanism. 

  After the third-party demand, still at the same timestamp, agent goes ahead to 
  conducting its own independent demand, travelling the expected route of the HyperGraph-Lattice 
  for that demand's (category,label). The cost associated with this route for independent 
  demand is equal to the sum of the node weights (see variable<negative_node_weight_map>) for 
  that route's node sequence. See method<DualCostsTypeHL.register_agent_path__independent_req> 
  for more information. Node weights are non-constant, increasing in relation to every alternative 
  route R taken to achieve a third-party demand, of expected route R1, R != R1. 
"""
class DualEnvTypeHL: 

    def __init__(self,dual_agent,ce_effect,third_party_demands,option_size_range,prg): 
        assert type(dual_agent) == DualRoleAgentTypeHL
        assert type(ce_effect) == PRClassExpectedEffectTypeHL
        assert type(prg) in {MethodType,FunctionType}
        
        assert len(dual_agent.independent_demands) == len(third_party_demands) 
        assert is_valid_range(option_size_range,True,False)
        assert option_size_range[0] > 0 

        self.dual_agent = dual_agent
        self.ce_effect = ce_effect 
        # list, element is (category,label) 
        self.third_party_demands = third_party_demands

        self.check_requirements() 
        
        self.option_size_range = option_size_range 
        self.prg = prg 
        
        self.cost_record = DualCostsTypeHL() 
        self.fin_stat = False 
        return

    def running_score(self): 
        print(self.cost_record) 

    def check_requirements(self): 
        D = self.dual_agent.independent_demands
        assert_HyperGraph_nodepair_existence(self.ce_effect.hg,D) 
        assert_HyperGraph_nodepair_existence(self.ce_effect.hg,self.third_party_demands) 

    def move_one(self): 
        if self.fin_stat: return 

        # dual agent chooses next index and associated independent demand 
        index,indep_demand = self.dual_agent.next_move() 

        if type(index) == type(None):
            self.fin_stat = True  
            return 

        # environment chooses 3rd-party demand of equal index 
        demand_3rd = self.third_party_demands.pop(index)

        # environment offers n nodepairs for dual agent to choose one
        labels = self.choose_n_labels()

        # dual agent chooses 
        actual_label = demand_3rd[1] 
        chosen_label_for_demand_3rd = self.dual_agent.select_option_for_3rd_party_demand(actual_label,labels)

        # dual agent calculates a path to satisfy third party demand 
        expected_path,chosen_path = self.pathpair_from_third_party_demand(chosen_label_for_demand_3rd,demand_3rd) 

        # register the 3rd party demand difference 
        self.cost_record.register_agent_path__3rd_party_req(chosen_path,expected_path)

        # environment updates node negative weights for nodes N = chosen_path - expected_path
        self.negative_weights_for_agent_3rd_party_demand_path(expected_path,chosen_path)

        # register the agent's demanded independent path
        independent_path = self.path_for_independent_demand(indep_demand)
        self.cost_record.register_agent_path__independent_req(independent_path)


    def choose_n_labels(self): 
        hg = self.ce_effect.hg
        nodeseq = sorted(hg.base_nodeset())

        R = self.option_size_range

        # case: nodeseq size falls below lower bound of option size range
        l = len(nodeseq)
        if l < self.option_size_range[0]:
            r0 = ceil(l * 0.25) 
            r1 = ceil(l * 0.75) 
            if r0 == r1: r1 += 1 
            R = [r0,r1] 
        # case: upper bound of option size range falls above nodeseq size
        elif self.option_size_range[1] > l + 1: 
            r1 = l + 1 
            R = [self.option_size_range[0],r1]

        num_labels = modulo_in_range(int(self.prg()),R) 
        return prg_choose_n(nodeseq,num_labels,prg__single_to_int(self.prg),\
            is_unique_picker=True)

    """
    return:
    - expected path (list of <NodePath>s), agent chosen path (list of <NodePath>s)
    """
    def pathpair_from_third_party_demand(self,agent_chosen_label,demand_3rd):

        l1 = demand_3rd[1]
        l1_cat = demand_3rd[0] 
        ext_prg = self.dual_agent.prg 
        
        expected_path = self.ce_effect.categorical_label2label_path(\
            l1,l1,l1_cat,self.prg) 

        agent_chosen_path = self.ce_effect.categorical_label2label_path(\
            agent_chosen_label,l1,l1_cat,ext_prg) 

        expected_path = NodePath_sequence_to_1d_sequence(expected_path)
        agent_chosen_path = NodePath_sequence_to_1d_sequence(agent_chosen_path)

        return expected_path,agent_chosen_path

    def negative_weights_for_agent_3rd_party_demand_path(self,expected_path,agent_chosen_path):
        print("E")
        print(expected_path)
        print()
        print("C")
        print(agent_chosen_path)
        print() 

        F = filter(lambda x: x not in expected_path,agent_chosen_path)
        chosen_seq_ = list(F) 

        neg_weights = Counter() 
        for c in chosen_seq_: 
            neg_weights[c] += prg_decimal(self.prg,[0.,1.]) 

        self.cost_record.update_negative_weights(neg_weights) 

    def path_for_independent_demand(self,indep_demand):
        indep_cat = indep_demand[0]
        indep_label = indep_demand[1]  
        ext_prg = self.dual_agent.prg 
        independent_path = self.ce_effect.categorical_label2label_path(\
            indep_label,indep_label,indep_cat,ext_prg) 
        independent_path = NodePath_sequence_to_1d_sequence(independent_path)
        return independent_path

    @staticmethod 
    def generate_instance(prg):
        # generate the HyperGraph 
        hg = DualEnvTypeHL.generate_default_HyperGraph(prg) 

        # get the number of demands 
        total_base_nodes = len(hg.base_nodeset()) 
        d = modulo_in_range(prg(),DEFAULT_DUAL_ENV_DEMAND_SIZE_RATIO_RANGE)
        num_demands = ceil(d * total_base_nodes) 

        prgs = prg_to_prg__LCG_sequence(prg,2,4/3+9/7) 
        prg0,prg1 = prgs[0],prgs[1] 

        # generate the agent 
        agent = DualRoleAgentTypeHL.generate_instance(hg,num_demands,prg0)

        # declare a class expected effects 
        cee = PRClassExpectedEffectTypeHL(hg,prg1)  

        # generate 3rd-party demands 
        demands_3rd = hg.select_nodepairs_with_PRNG(num_demands,prg)

        return DualEnvTypeHL(agent,cee,demands_3rd,DEFAULT_DUAL_ENV_OPTION_SIZE_RANGE,prg)

    @staticmethod 
    def generate_default_HyperGraph(prg): 
        hg_nodesize = modulo_in_range(int(prg()),DEFAULT_DUAL_ENV_HG_NODESIZE_RANGE) 
        hg_connectivity = modulo_in_range(prg(),DEFAULT_DUAL_ENV_HG_CONNECTIVITY_RANGE)
        is_directed = False 
        base_nodesize = ceil(hg_nodesize * DEFAULT_DUAL_ENV_HG_BASE_NODESIZE_MULTIPLIER) 
        node2nodeset_sizerange = DEFAULT_DUAL_ENV_HG_BASE_NODE2NODESET_SIZE_RANGE

        hg = HyperGraph.generate_instance(hg_nodesize,\
            hg_connectivity,is_directed,base_nodesize,\
            node2nodeset_sizerange,prg)
        return hg 