from .analog_schemes_aux import * 

"""
The specification of products (+/- # of nodes/edges), used by a 
<PRNGReactiveGraphRule> instance. 
"""
class PRNGGraphProductRule: 

    def __init__(self,node_change:int,edge_change:int):
        assert type(node_change) == int 
        assert type(edge_change) == int 
        
        self.node_change = node_change
        self.edge_change = edge_change
        return

    def graph_delta(self,G,is_dsg:bool,node_ctr,prg,verbose=False): 
        node_deltas = None 
        if self.node_change != 0: 
            prg_ = prg__single_to_int(prg)
            G,node_deltas = node_changes_to_graph(G,is_dsg,self.node_change,prg_,node_ctr) 

        add_edge = self.edge_change > 0 

        q = abs(self.edge_change) 
        edge_deltas = [] 
        while q > 0: 
            edelta = one_edge_change(G,is_dsg,add_edge,prg) 
            edge_deltas.extend(edelta)
            q -= 1 
        return G,node_deltas,edge_deltas

"""
A rule for a graph, designed for simple graphs. 

Rule activates when the periodic number of encounters a graph traversal process has with 
the `reactant` (a node or edge) hits the `period`. 

Activation produces change, specified by a <PRNGGraphProductRule>, on a parameter graph.
"""
class PRNGReactiveGraphRule: 

    def __init__(self,reactant,product_rule,is_node_rule:bool,period:int): 
        assert type(is_node_rule) == bool 
        assert type(product_rule) == PRNGGraphProductRule
        assert type(period) == int and period > 0 
        
        self.reactant = reactant 
        self.product_rule = product_rule 
        self.is_node_rule = is_node_rule
        self.period = period 

        self.c = 0 
        return

    def register(self,G,is_dsg:bool,node_ctr,prg,verbose=False): 

        self.c += 1 

        # case: process rule 
        if self.c >= self.period: 
            G,node_deltas,edge_deltas = self.product_rule.graph_delta(G,is_dsg,node_ctr,prg,verbose) 
            self.c = 0 
            return True,G,node_deltas,edge_deltas 

        return False,G,None,None 

    def product_rule_values(self): 
        return self.product_rule.node_change,self.product_rule.edge_change

    @staticmethod
    def generate_instance(reactant,is_node_rule:bool,\
        nodechange_range,edgechange_range,period_range,prg):

        node_change = modulo_in_range(int(prg()),nodechange_range) 
        edge_change = modulo_in_range(int(prg()),edgechange_range) 
        period = modulo_in_range(int(prg()),period_range) 

        prule = PRNGGraphProductRule(node_change,edge_change)
        return PRNGReactiveGraphRule(reactant,prule,is_node_rule,period)

"""
Realtime Reactive Graph Rule Operator, Type (S)tochastic. 

An operator that stores a set of node and edge rules for use during graph traversal. 
When a node or edge has been encountered by the traversal process, operator either 
fetches a rule R that is already stored in its memory, or generates a new rule, 
hence the naming of `realtime`. 

Using a PRNG, Rule R the parameter graph `G` by adding/subtracting the appropriate 
number of nodes and edges at the appropriate periodic timestamp. After that periodic 
timestamp has activated, the parameter `is_rule_constant` determines if a new rule 
should be generated to replace R, or to maintain rule R for the possible next periodic 
timestamp of activation. 
"""
class RealtimeReactiveGraphRuleOperatorTypeS:  

    def __init__(self,graph_nodeset,is_dsg:bool,nodechange_range,edgechange_range,period_range,maintain_connectivity:bool,\
        is_rule_constant:bool,prg):   
        assert type(graph_nodeset) == set 
        assert type(is_dsg) == bool 

        assert is_valid_range(nodechange_range,True,False) 
        assert is_valid_range(edgechange_range,True,False) 
        assert is_valid_range(period_range,True,False) 
        assert period_range[0] > 0 

        assert type(maintain_connectivity) == bool 
        assert type(is_rule_constant) == bool 

        assert type(prg) in {MethodType,FunctionType}

        max_node = max(graph_nodeset) + 1 
        self.ctr = SimpleCounter(max_node).__next__ 
        self.is_dsg = is_dsg 

        self.nc_range = nodechange_range
        self.ec_range = edgechange_range
        self.p_range = period_range

        self.maintain_connectivity = maintain_connectivity
        self.is_rule_constant = is_rule_constant
        self.prg = prg 

        self.node_rules = dict() 
        self.edge_rules = dict() 
        return

    def react(self,G,edgeseq,verbose): 
        assert type(edgeseq) == list 

        # react the nodes first 
        nodes = [edge[1] for edge in edgeseq] 
        node_deltas = []

        node_delta_map,edge_delta_map = dict(),dict()

        for n in nodes: 
            stat,G,nds,eds,num_nodes,num_edges = self.react_one(G,n,True,verbose) 
            if stat:
                node_deltas.append(n)
                node_delta_map[n] = (nds,eds,num_nodes > 0,num_edges > 0)  

        if not self.is_rule_constant: 
            for n in node_deltas: 
                self.new_rule(G,n,is_node=True) 

        # now react the edges 
        edge_deltas = [] 
        for ex in edgeseq: 
            stat,G,nds,eds,num_nodes,num_edges = self.react_one(G,ex,False,verbose) 
            if stat: 
                edge_deltas.append(ex) 
                edge_delta_map[ex] = (nds,eds,num_nodes > 0,num_edges > 0)

        # change deltas 
        if not self.is_rule_constant: 
            for ex in edge_deltas:
                self.new_rule(G,ex,is_node=False)

        if self.maintain_connectivity:
            G = graph_to_one_component(G,self.prg)
        return G 

    def react_one(self,G,x,is_node:bool,verbose:bool): 

        Q = self.node_rules if is_node else self.edge_rules 

        if x not in Q: 
            self.new_rule(G,x,is_node) 

        R = Q[x] 
        stat,G,node_delta,edge_delta = R.register(G,self.is_dsg,self.ctr,self.prg) 
        num_node,num_edge = R.product_rule_values() 

        if stat and verbose:  
            print("NN: ",node_delta,num_node)
            print("EE: ",edge_delta,num_edge) 
            print()
        return stat,G,node_delta,edge_delta,num_node,num_edge 

    def new_rule(self,G,x,is_node:bool):
        Q = self.node_rules if is_node else self.edge_rules 

        R = PRNGReactiveGraphRule.generate_instance(\
            x,is_node,self.nc_range,self.ec_range,self.p_range,self.prg)
        Q[x] = R 

    def clean_up_rules(self,G):

        # clean up nodes 
        dead_nodes = set() 
        for k,v in self.node_rules.items(): 
            if k not in G: 
                dead_nodes |= {k} 

        for k in dead_nodes: del self.node_rules[k] 
        
        # clean up edges 
        dead_edges = set()
        for k,v in self.edge_rules.items(): 
            q0,q1 = k[0],k[1] 
            if q0 not in G: 
                dead_edges |= {k} 
                continue 
            if q1 not in G[q0]: 
                dead_edges |= {k}

        for k in dead_edges: del self.edge_rules[k] 
        return 