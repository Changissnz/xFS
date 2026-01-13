from .ce_agent import * 

class CEAgentNetwork:

    def __init__(self,cea_map:dict,prg): 
        assert type(cea_map) == dict 
        for k,v in cea_map.items(): 
            assert type(v) == CEAgent 
            assert k == v.idn 
        self.cea_map = cea_map 
        self.prg = prg 

        self.main_db = SimpleAgentDB(np.ndarray) 
        self.bridges = dict() 
        for k,v in cea_map.items(): 
            self.bridges[k] = CEAgentDBBridge(v,self.main_db) 
        return

    @staticmethod 
    def generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,s_conn_range,\
        t_conn_range,s_port_variance_range,prg,cl_num_balls=50,prg_output_range=[-1000,1000],\
        cl_radius_ratio = 0.1): 

        def constrained_prg(prg): 

            def f(): 
                return modulo_in_range(prg(),prg_output_range) 
            return f 

        prg_ = prg__single_to_int(prg)
        agent_idns = [i for i in range(num_agents)] 
        agent_idns = prg_seqsort(agent_idns,prg_)

        cprg = constrained_prg(prg) 
        cea_map = dict() 

        min_point = np.ones((prg_state_shape,)) * prg_output_range[0] 
        max_point = np.ones((prg_state_shape,)) * prg_output_range[1] 
        cl_radius = euclidean_point_distance(min_point,max_point) * cl_radius_ratio
        for a in agent_idns: 
            s = [a2 for a2 in agent_idns if a2 != a] 

            r_conn = modulo_in_range(prg(),r_conn_range) 
            s_conn = modulo_in_range(prg(),s_conn_range) 
            t_conn = modulo_in_range(prg(),t_conn_range) 

            num_r = ceil(r_conn * len(s))
            num_s = ceil(s_conn * len(s))
            num_t = ceil(t_conn * len(s))

            r_nodes = prg_choose_n(deepcopy(s),num_r,prg_,is_unique_picker=True)
            s_nodes = prg_choose_n(deepcopy(s),num_s,prg_,is_unique_picker=True) 
            t_nodes = prg_choose_n(deepcopy(s),num_t,prg_,is_unique_picker=True)

            s_port_variance = dict() 
            for s_ in s_nodes: 
                q = modulo_in_range(prg(),s_port_variance_range)
                s_port_variance[s_] = q 
            
            cagent = CEAgent(a,set(r_nodes),s_port_variance,set(t_nodes),cprg,prg_state_shape,\
                cl_num_balls,cl_radius,deepcopy(s_port_variance_range)) 
            cea_map[a] = cagent 
        return CEAgentNetwork(cea_map,prg)

    """
    main method 
    """
    def move_one_timestamp(self): 
        self.move_agents() 
        self.agent_transmissions() 
        self.agent_reactions() 
        return

    def move_agents(self):

        for k,v in self.cea_map.items(): 
            v.clear_transmission() 
            v.clear_reaction() 
            v.next_act()
            
            # send info to db 
            b = self.bridges[k] 
            b.transmit_agent_state_to_db() 
        
        # update each agent database 
        self.update_bridges() 
        return 

    ############################################ methods to transmit vectors 
    def agent_transmissions(self): 
        # conduct agent transmission 
        for k in self.cea_map.keys(): 
            D,d = self.agent_transmission_(k)
            c = self.cea_map[k]
            c.update_score(-d) 
            c.update_cdelta(D)

    def agent_transmission_(self,idn): 

        def transmit_(subject_idn,target_idn): 
            v = c.current_transmission[subject_idn] 
            b = self.bridges[target_idn]
            return b.accept_transmission(subject_idn,v) 

        c = self.cea_map[idn] 
        d = 0 
        D = defaultdict(defaultdict)  
        for s in c.s_port_variance.keys(): 
            D[s] = defaultdict(float)
            for t in c.t_ports: 
                d_ = transmit_(s,t) 
                d += d_
                D[s][t] = round(d_,5)   
        return D,round(d,5) 

    ############################################ methods for agents to react from transmitted vectors 

    def agent_reactions(self): 
        for k in self.cea_map.keys(): 
            self.agent_reaction_(k) 

    def agent_reaction_(self,idn): 

        def react_(r_idn,d): 
            c2 = self.cea_map[r_idn] 
            c2.update_score(d)
            c2.execution_delta[idn] += d 
            return 

        c = self.cea_map[idn] 
        d = 0 
        D = defaultdict(float)
        for r_,d in c.current_reaction.items(): 
            react_(r_,d)
        return

    def update_bridges(self): 
        for k in self.cea_map.keys(): 
            self.update_bridge(k) 
        return

    def update_bridge(self,idn): 
        c = self.cea_map[idn]
        b = self.bridges[idn]

        S = c.s_port_variance.keys()
        for s in S: 
            b.exec_query(s) 
        return 

    def fetch_agent(self,idn): 
        assert idn in self.cea_map
        return self.cea_map[idn]

    """
    Determines if directed triplet t=(A,B,C) is reactive. 

    B is s_port of A? 
    C is t_port of A? 
    B is r_port of C? 
    """
    def is_reactive_dtriplet(self,triplet):
        A,B,C = self.cea_map[triplet[0]],\
            self.cea_map[triplet[1]],self.cea_map[triplet[2]] 
        
        stat0 = A.is_related(triplet[1],'s')
        stat1 = A.is_related(triplet[2],'t') 
        stat2 = C.is_related(triplet[1],'r')
        return (stat0,stat1,stat2) 

    """
    Three 3 x 3 matrices, one each for R,S,T in triplet, for 
    pairwise directed relations of A,B,C. 
    """
    def triplet_relation(self,triplet): 
        M = [] 
        for x in ['r','s','t']: 
            M2 = self.triplet_relation_(triplet,x)
            M.append(M2)
        return np.array(M) 

    def triplet_relation_(self,triplet,conn_type): 
        assert conn_type in {'r','s','t'} 
        assert len(triplet) == 3 == len(set(triplet)) \
            and type(triple) == list
        M = np.zeros((3,3),dtype=bool) 

        for i in range(3):
            a0 = self.cea_map[triplet[i]]
            for j in range(3): 
                stat = a0.is_related(triplet[j],conn_type)
                M[i,j] = stat 
        return M 