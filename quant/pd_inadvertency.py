from graph_models.hg_obj_path_op import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence

class PRNGProactionInadvertentEffect: 

    def __init__(self,proaction_path_navigator,proaction_node_to_inadvertent_path_navigators): 
        assert type(proaction_path_navigator) == DIPathNavigatorHandler
        
        nodeset = proaction_path_navigator.path_nodeset() 
        assert type(proaction_node_to_inadvertent_path_navigators) == dict 
        assert nodeset == set(proaction_node_to_inadvertent_path_navigators.keys()) 

        for v in proaction_node_to_inadvertent_path_navigators.values(): 
            for v_ in v: 
                assert type(v_.dipn) == InadvertentDIPathNavigator

        self.ppn = proaction_path_navigator
        self.n2ipn_map = proaction_node_to_inadvertent_path_navigators
        self.fin_stat = False 
        self.imap = defaultdict(int)
        return

    def set_prg(self,prg): 
        assert type(prg) in {FunctionType,MethodType}

        self.ppn.set_prg(prg) 

        for v in self.n2ipn_map.values(): 
            for v_ in v: 
                v_.set_prg(prg) 
        return 

    def __next__(self): 
        if self.ppn.dipn.fin_stat:
            self.fin_stat = True 
        
        if self.fin_stat: return None,0. 

        # proaction 
        next(self.ppn)

        # inadvertency 
        c,v = self.ppn.current_extra_value() 
        if type(c) == type(None): 
            return c,0.  

        self.inadvertency_on_proaction_node(c,abs(v)) 
        return c,v 

    def inadvertency_on_proaction_node(self,n,v): 
        q = self.n2ipn_map[n] 
        for (i,q_) in enumerate(q): 
            q_.add_support(abs(v)) 
            while not q_.dipn.fin_stat: 
                next(q_) 
            self.imap[(n,i)] += q_.dipn.at_tail() 

    @staticmethod 
    def generate_instance(start_node_idn,inadvertency_ratio_range,node_value_range,\
        inadvertency_size_range,info_mode,prg):

        # generate proaction 
        dipnh = PRNGProactionInadvertentEffect.generate_one_DIPathNavigatorHandler(\
            start_node_idn,node_value_range,info_mode,is_inadvertent=False,prg=prg)

        start_node_idn += 3 

        # generate inadvertent effects 
        nodeseq = sorted(dipnh.path_nodeset())
        D = dict() 
        for n in nodeseq: 
            inadvertencies = modulo_in_range(int(prg()),inadvertency_size_range)
            D[n] = [] 
            for i in range(inadvertencies): 
                prg0 = prg_to_prg__LCG_sequence(prg,1,modulo_in_range(prg(),[1,5.]))[0]
                d0,d1 = prg_decimal(prg,inadvertency_ratio_range),prg_decimal(prg,inadvertency_ratio_range) 
                d2 = sorted([d0,d1]) 
                m = modulo_in_range(prg(),node_value_range)
                d3 = [d2[0] * m,d2[1] * m] 
                ieffect = PRNGProactionInadvertentEffect.generate_one_DIPathNavigatorHandler(\
                    start_node_idn,d3,info_mode,is_inadvertent=True,prg=prg0) 
                D[n].append(ieffect) 
                start_node_idn += 3 
        return PRNGProactionInadvertentEffect(dipnh,D),start_node_idn

    @staticmethod 
    def generate_one_DIPathNavigatorHandler(start_node_idn,node_value_range,\
        info_mode,is_inadvertent:bool,prg): 
 
        # generate pro-action path 
        extra_edge_ratio = prg_decimal(prg,[0.,1.]) 
        ratio_indirect_activation = prg_decimal(prg,[0.,1.])
        prior_dependency_ratio = prg_decimal(prg,[0.,1.])
        activation_type = "linexp" if prg_decimal(prg,[0.,1.]) >= 0.5 else "single"

        G = generate_directed_implication_path(3,extra_edge_ratio,prg,start_node_idn=start_node_idn)
        nv_map = generate_nv_map_from_nv_range([i for i in range(start_node_idn,start_node_idn+3)],\
            node_value_range,prg)

        optdi = ObjectivePathTypeDI.generate_instance(G,nv_map,\
            ratio_indirect_activation,prior_dependency_ratio,activation_type,prg)
    
        if not is_inadvertent:
            dipn = DIPathNavigator.from_PathTypeDI(optdi,prg)
        else: 
            dipn = InadvertentDIPathNavigator.from_PathTypeDI(optdi,prg)

        return DIPathNavigatorHandler(optdi,dipn,info_mode=info_mode,verbose=False)

class PRNGProactionInadvertentEffectChain: 

    def __init__(self,prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
        inadvertency_size_range,info_mode,chain_prg,solver_prg):   

        assert 0. <= prior_connectivity_pr <= 1. 
        assert info_mode in {0,1}
        assert type(chain_prg) in {MethodType,FunctionType}
        assert type(solver_prg) in {MethodType,FunctionType}

        self.pc_pr = prior_connectivity_pr 
        self.ir_range = inadvertency_ratio_range
        self.nv_range = node_value_range
        self.is_range = inadvertency_size_range
        self.info_mode = info_mode 
        self.chain_prg = chain_prg
        self.solver_prg = solver_prg 

        self.start_node_idn = 0 

        self.current_pie = None
        # current PIE node -> prior PIE index -> prior PIE nodeseq 
        self.current_to_prior_links = None  
        self.previous_pie = [] 

    def __next__(self): 
        if type(self.current_pie) == type(None): 
            self.next_PIE() 

        c,v = next(self.current_pie) 
        if type(c) != type(None): 
            self.activate_links(c,v) 
        
        if self.current_pie.fin_stat: 
            self.current_pie = None 
            self.current_to_prior_links = None 

    def next_PIE(self): 
        assert type(self.current_pie) == type(None) == type(self.current_to_prior_links) 
        
        self.current_pie, self.start_node_idn = PRNGProactionInadvertentEffect.generate_instance(\
            self.start_node_idn,self.ir_range,self.nv_range,self.is_range,\
            self.info_mode,self.chain_prg)
        self.current_pie.set_prg(self.solver_prg) 
        self.link_current_to_prior_PIE()
        return

    def activate_links(self,c,v): 
        if c not in self.current_to_prior_links: return 

        V = self.current_to_prior_links[c] 
        for prior_index,prior_nodeseq in V.items(): 
            P = self.previous_pie[prior_index]
            for pn in prior_nodeseq: 
                P.inadvertency_on_proaction_node(pn,v) 

    def link_current_to_prior_PIE(self): 
        self.current_to_prior_links = dict() 
        nodeseq = sorted(self.current_pie.ppn.path_nodeset()) 
        for n in nodeseq: 
            self.select_linking_nodes_for_PIE_(n) 

    def select_linking_nodes_for_PIE_(self,current_pie_node):
        for i in range(len(self.previous_pie)): 
            self.select_linking_nodes_for_PIE__(current_pie_node,i) 

    # current PIE node -> prior PIE index -> prior PIE nodeseq 
    def select_linking_nodes_for_PIE__(self,current_pie_node,i):
        assert len(self.previous_pie) > i >= 0 

        P = self.previous_pie[i] 
        K = sorted(P.n2ipn_map.keys())
        S = [] 
        for k in K: 
            d = prg_decimal(self.chain_prg,[0.,1.]) 
            if d <= self.pc_pr: 
                S.append(k) 
        
        if current_pie_node not in self.current_to_prior_links: 
            self.current_to_prior_links[current_pie_node] = dict() 
        self.current_to_prior_links[current_pie_node][i] = S 
        return
        