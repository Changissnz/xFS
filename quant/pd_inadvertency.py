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

    def __next__(self): 
        if self.ppn.dipn.fin_stat:
            self.fin_stat = True 
        
        if self.fin_stat: return 

        # proaction 
        next(self.ppn)

        # inadvertency 
        c,v = self.ppn.current_extra_value() 
        if type(c) == type(None): 
            return 
        self.inadvertency_on_proaction_node(c,abs(v)) 
        return 

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
        return PRNGProactionInadvertentEffect(dipnh,D) 

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

    def __init__(self): 

        return -1