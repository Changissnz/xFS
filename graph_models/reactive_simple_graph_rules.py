from .analog_schemes_aux import * 

class PRNGGraphProductRule: 

    def __init__(self,node_change:int,edge_change:int):
        assert type(node_change) == int 
        assert type(edge_change) == int 
        
        self.node_change = node_change
        self.edge_change = edge_change
        return

    def graph_delta(self,G,is_dsg:bool,node_ctr,prg): 
        if self.node_change: 
            G = node_changes_to_graph(G,is_dsg,self.node_change,prg,node_ctr) 

        add_edge = self.edge_change > 0 

        q = abs(self.edge_change) 

        while q > 0: 
            one_edge_change(G,is_dsg,add_edge,prg) 
            q -= 1 
        return

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

    def register(self,G,is_dsg:bool,node_ctr,prg): 

        self.c += 1 

        # case: process rule 
        if self.c >= self.period: 
            self.product_rule.graph_delta(G,is_dsg,node_ctr,prg) 
            self.c = 0 
            return True 

        return False  

    @staticmethod
    def generate_instance(reactant,is_node_rule:bool,\
        nodechange_range,edgechange_range,period_range,prg):

        node_change = modulo_in_range(int(prg()),nodechange_range) 
        edge_change = modulo_in_range(int(prg()),edgechange_range) 
        period_change = modulo_in_range(int(prg()),period_range) 

        prule = PRNGGraphProductRule(node_change,edge_change)
        return PRNGReactiveGraphRule(reactant,product_rule,is_node_rule:bool,period:int): 

class RealtimeReactiveGraphRuleOperatorTypeS:  

    def __init__(self,graph_nodeset,is_dsg:bool,nodechange_range,edgechange_range,period_range,maintain_connectivity:bool,\
        is_rule_constant:bool,prg):   
        assert type(graph_nodeset) == set 
        assert type(is_dsg) == bool 

        assert is_valid_range(nodechange_range,True,False) 
        assert nodechange_range[0] > 0 

        assert is_valid_range(edgechange_range,True,False) 
        assert edgechange_range[0] > 0 

        assert is_valid_range(period_range,True,False) 
        assert period_range[0] > 0 
        assert type(maintain_connectivity) == bool 
        assert type(is_rule_constant) == bool 

        assert type(prg) in {MethodType,FunctionType}

        max_node = max(graph_nodeset) + 1 
        self.ctr = SimpleCounter(max_node) 

        self.nc_range = nodechange_range
        self.ec_range = edgechange_range
        self.p_range = period_range

        self.maintain_connectivity = maintain_connectivity
        self.is_rule_constant = is_rule_constant
        self.prg = prg 

        self.node_rules = dict() 
        self.edge_rules = dict() 
        return

    def react(self,G,edgeseq): 
        assert type(edgeseq) == list 

        # react the nodes first 
        nodes = [edge[1] for edge in edgeseq] 
        node_deltas = [] 
        for n in nodes: 
            stat = self.react_one(G,n,True) 
            if stat:
                node_deltas.append(n)

        for n in node_deltas: 
            self.new_rule(G,n,is_node=True) 

        # now react the edges 
        edge_deltas = [] 
        for ex in edgeseq: 
            stat = self.react_one(G,ex,False) 
            if stat: 
                edge_deltas.append(ex) 

        # change deltas 
        for ex in edge_deltas:
            self.new_rule(G,ex,is_node=False)
        return

    def react_one(self,G,x,is_node:bool): 

        Q = self.node_rules if is_node else self.edge_rules 

        if x not in Q: 
            self.new_rule(G,x,is_node) 

        R = Q[x] 
        return R.register(G,self.is_dsg,self.ctr,self.prg) 

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