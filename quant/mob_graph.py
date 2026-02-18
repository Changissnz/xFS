from quant.usg_controller import * 
from morebs2.numerical_generator import modulo_in_range,prg_to_prg__LCG_sequence,\
    merge_two_prgs_into_LCG_sequence,prg_decimal
from graph_models.graph_gen import * 

"""
the anti-mob faction in simulation Mob Killer Bot 
"""
class AntiMobUnit: 

    def __init__(self,score,prg): 
        assert score > 0 
        self.score = score 
        self.prg = prg  

        self.current_vector = None 
        return 

    def choose_first_mob_agent(self,mob_agent_seq): 
        i = int(self.prg()) % len(mob_agent_seq)
        return mob_agent_seq[i] 

    def transmit_vector(self): 
        boolie = bool(int(self.prg()) % 2) 
        q = self.prg() 
        self.current_vector = (boolie,q) 
        return (boolie,q)

    def delta_score(self,delta): 
        self.score += delta  

    def output_decimal(self): 
        return prg_decimal(self.prg,[0.,1.])

    def output(self): 
        return self.prg()     

"""
member of the mob faction in simulation Mob Killer Bot 
"""
class MobAgent: 

    def __init__(self,idn,score,prg,weight=1): 
        assert score > 0 
        assert type(prg) in {MethodType,FunctionType}

        self.idn = idn 
        self.score = score 
        self.prg = prg 
        self.weight = weight  
        self.boolie = None  
        return

    def output_decimal(self): 
        return prg_decimal(self.prg,[0.,1.])

    def output(self): 
        return self.prg() 

    def output_bool(self): 
        return int(self.prg()) % 2 

    def receive_bool(self,boolie,accept_stat): 
        assert type(accept_stat) == bool == type(boolie)
        if accept_stat: 
            self.boolie = boolie 
        else: 
            self.boolie = not boolie 
        return

    def delta_score(self,delta): 
        self.score += delta  

"""
the network used for simulation Mob Killer Bot 
"""
class MobNetwork: 

    def __init__(self,G,antimob:AntiMobUnit,mob_agent_map:dict,prg,mutable_weight_function,\
        verbose=False):
        assert type(G) == defaultdict, "got {}".format(type(G))
        assert set(G.keys()) == set(mob_agent_map.keys())
        assert type(antimob) == AntiMobUnit
        for k,v in mob_agent_map.items(): 
            assert k == v.idn 
        assert type(prg) in {MethodType,FunctionType}
        assert type(mutable_weight_function) in {MethodType,FunctionType}

        self.G = G 
        self.antimob = antimob 
        self.mob_agent_map = mob_agent_map
        self.prg = prg 
        self.mutable_weight_function = mutable_weight_function
        self.verbose = verbose 
        self.tmob_map = dict() 
        self.graphtrav = None 
        self.fin_stat = False 
        self.result_stat = None 
        return 

    ##################################### weight and PRNG assignment 

    def assign_prng_to_antimob(self,prg): 
        self.antimob.prg = prg  

    def assign_prngs_to_mob_agents(self,d): 
        for k,v in d.items(): 
            assert k in self.mob_agent_map
            assert type(v) in {MethodType,FunctionType}
            self.mob_agent_map[k].prg = v 
        return 

    def assign_uniform_mob_agent_weight(self,w=1): 
        for v in self.mob_agent_map.values(): 
            v.weight = w 
        return 

    """
    assigns every i'th mob agent in iteration a weight of 
        w * i 
    """
    def assign_mscaled_mob_agent_weight(self,w=1): 
        A = prg_seqsort(sorted(self.mob_agent_map.keys()),prg__single_to_int(self.prg)) 

        for (i,a) in enumerate(A): 
            w_ = (i+1) * w 
            #print("assigning {}'th agent {} weight {}".format(i+1,a,w_))
            m = self.mob_agent_map[a] 
            m.weight = w_ 
        return 

    def agent_scores(self,neg_to_zero:bool=False): 
        s = self.antimob.score 
        if neg_to_zero and s < 0.: 
            s = 0. 

        d = {} 
        for k,v in self.mob_agent_map.items(): 
            s2 = v.score 
            d[k] = s2 

        for k,v in self.tmob_map.items(): 
            s2 = v.score 
            if neg_to_zero and s2 < 0.: 
                s2 = 0 
            d[k] = s2 
        return s,d 
        
    ############################################################################## 

    """
    main function 
    """
    def __next__(self): 
        if self.fin_stat: return 

        a = self.antimob.choose_first_mob_agent(sorted(self.mob_agent_map.keys())) 
        boolie,q = self.antimob.transmit_vector() 
        self.distribute_vector(a,boolie,q)
        mob_vote = self.majority_vote() 

        stat = mob_vote == self.antimob.current_vector[0]
        W = self.agent_bool_weight(mob_vote)  

        # penalize unit 
        if stat: 
            if self.verbose: print("-- penalizing anti-mob")
            self.antimob.delta_score(-W) 
        # penalize mob 
        else: 
            if self.verbose: print("-- penalizing mob") 
            is_inversely_prop = self.antimob.output_decimal() >= 0.5
            self.distribute_delta_to_mob_agents(W,mob_vote,is_inversely_prop) 

        # NOTE: there is never a tie 
        if self.antimob.score <= 0.: 
            self.fin_stat = True 
            self.result_stat = "mob win" 
        elif len(self.mob_agent_map) == 0: 
            self.fin_stat = True 
            self.result_stat = "anti-mob win" 

        if self.verbose: 
            print("anti-mob: ",self.antimob.score) 
            print("number of mob agents: ",len(self.mob_agent_map)) 
            q = self.top_n_agent_attr(len(self.mob_agent_map),True)  

            print("\n* top 5 weights: ",q[:5]) 
            print("* bottom 5 weights: ",q[-5:]) 

            q = self.top_n_agent_attr(len(self.mob_agent_map),False)  
        
            print("\n* top 5 scores: ",q[:5]) 
            print("* bottom 5 scores: ",q[-5:]) 
            print() 

        return 

    def majority_vote(self): 
        c = 0 
        for a in self.mob_agent_map.values(): 
            c += int(a.boolie)
        if self.verbose: print("mob vote: +  {},  -  {}".format(c,len(self.mob_agent_map) - c)) 
        return c >= len(self.mob_agent_map) / 2 

    ############################### anti-mob vector distribution to mob agents 

    def distribute_vector(self,a,b,q): 
        # start with first agent 
        agent = self.mob_agent_map[a]
        agent.weight = self.mutable_weight_function(agent.weight) 
        accept_stat = bool(ceil(agent.output() + q) % 2) 
        agent.receive_bool(b,accept_stat)

        # iterate through other agents until finish 
        cumulative_weight = agent.weight 

        self.graphtrav = USGController() 
        self.graphtrav.set_new_search(is_dfs=True,start_node=a,d=self.G,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
            nextnode_priority_function=\
            DEFAULT_PRNG_TO_NEXTNODE_PRIORITY_FUNCTION__DFS(self.antimob.prg),\
            no_duplicate_touch_nodes=True) 

        prev_bool = agent.boolie 
        agent_index = 1
        while type(cumulative_weight) != type(None): 
            prev_bool,cumulative_weight = self.distribute_to_next_agent(prev_bool,cumulative_weight,agent_index)
            agent_index += 1 
        return

    def distribute_to_next_agent(self,prev_bool,cumulative_weight,agent_index): 
        
        while True: 
            _,not_finished,_ = self.graphtrav.move_search(0)

            if not not_finished: 
                return None,None 

            x = self.graphtrav.recent_edges(0)
            if len(x) > 0: 
                x = x[0] 
                break 
        r = x[1] 

        w = sum(self.top_n_agent_attr(agent_index,True)) 
        f_t = cumulative_weight / w 
        agent = self.mob_agent_map[r]
        f = agent.output_decimal()
        accept_stat = f <= f_t 
        #print("-- prev bool {}, {}'th agent response {}, output {}, threshold {}".format(prev_bool,\
        #    agent_index,accept_stat,f,f_t))
        agent.receive_bool(prev_bool,accept_stat)  
        return agent.boolie,cumulative_weight+agent.weight 

    def top_n_agent_attr(self,n,is_weight:bool,include_idn:bool=False):
        def ret(agent): 
            return agent.weight if is_weight else agent.score 

        if include_idn: 
            rx = sorted([(v.idn,ret(v)) for v in self.mob_agent_map.values()],\
                key=lambda x:x[1],reverse=True)
        else: 
            rx = sorted([ret(v) for v in self.mob_agent_map.values()],reverse=True) 
        return rx[:n] 

    def agent_bool_weight(self,boolie):
        w = 0 
        for a in self.mob_agent_map.values(): 
            if a.boolie == boolie: 
                w += a.weight 
        return w  

    ################################# distribution of negative delta to mob agents 

    def distribute_delta_to_mob_agents(self,delta,mob_vote,is_inversely_prop:bool): 
        if len(self.mob_agent_map) == 0: 
            return 
        
        #S = sum([v.weight for v in self.mob_agent_map.values()]) 
        S = self.agent_bool_weight(mob_vote) 
        terminated = set() 
        for v in self.mob_agent_map.values(): 
            if v.boolie != mob_vote: continue 

            f = v.weight / S 
            if is_inversely_prop: 
                f = 1 - f 

            delta_ = f * delta 
            v.delta_score(-delta_) 

            if v.score <= 0.: 
                terminated |= {v.idn}

        for t in terminated: 
            self.tmob_map[t] = self.mob_agent_map[t] 
            del self.mob_agent_map[t]

        if len(terminated) > 0: 
            g = MicroGraph(self.G) 
            g.subgraph_nodeset_exclusion(terminated)
            self.G = g.dg 
            self.G = graph_to_one_component(self.G,self.prg) 

    @staticmethod 
    def generate_instance(num_agents,prg,antimob_score,mob_agent_uniform_score,mob_agent_weight_range=[1,200],\
        mutable_weight_function = lambda x: x + 0):   

        if num_agents < 100: 
            connectivity_range = [0.005,0.2] 
        else: 
            connectivity_range = [0.0009,0.005] 

        is_realtime_gen = bool(int(prg()) % 2) 
        edge_connectivity = modulo_in_range(prg(),connectivity_range)
        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
                vertex_degree=num_agents,edge_connectivity=edge_connectivity,\
                verbose=False)
        gg.full_run() 
        G = graph_to_one_component(gg.d,prg)

        mob_agent_map = dict() 
        prg2 = prg_to_prg__LCG_sequence(prg,1,3.141414)[0] 
        lcg_seq = merge_two_prgs_into_LCG_sequence(prg,prg2,num_agents,[1.010101,5.55555]) 

        for i in range(num_agents): 
            prg_ = lcg_seq[i] 
            ma = MobAgent(i,mob_agent_uniform_score,prg_,modulo_in_range(prg(),mob_agent_weight_range)) 
            mob_agent_map[i] = ma 

        amu = AntiMobUnit(antimob_score,prg) 
        return MobNetwork(G,amu,mob_agent_map,prg,mutable_weight_function)