from .cee_map import * 

def assert_HyperGraph_nodepair_existence(hg,nodepair_seq): 
    assert type(hg) == HyperGraph

    for n in nodepair_seq:
        assert len(n) == 2  
        n0,n1 = n[0],n[1]
        assert hg.nodepair_exists(n0,n1)

def NodePath_sequence_to_1d_sequence(nseq): 
    assert type(nseq) == list 

    S = [] 
    for seq in nseq: 
        q = seq.p
        S.extend(q) 
    return S 

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
        return

    def set_prg(self,prg):
        assert type(prg) in {MethodType,FunctionType}
        self.prg = prg

    def next_move(self): 
        l = len(self.independent_demands)
        if l == 0: return None,None 

        i = int(self.prg()) % l 
        return i,self.independent_demands.pop(i)

    def select_option_for_3rd_party_demand(self,labels): 
        i = int(self.prg()) % len(labels)  
        return labels[i]

# TODO: write description 
class DualEnvTypeHL: 

    def __init__(self,dual_agent,ce_effect,third_party_demands,option_size_range,prg): 
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
        chosen_label_for_demand_3rd = self.dual_agent.select_option_for_3rd_party_demand(labels)

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

        expected_seq = NodePath_sequence_to_1d_sequence(expected_path)
        agent_chosen_path = NodePath_sequence_to_1d_sequence(agent_chosen_path)

        return expected_path,agent_chosen_path

    def negative_weights_for_agent_3rd_party_demand_path(self,expected_path,agent_chosen_path):

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