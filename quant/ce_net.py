from .ce_agent import * 

class CEAgentNetwork:

    def __init__(self,cea_map:dict,prg): 
        assert type(cea_map) == dict 
        for k,v in cea_map.items(): 
            assert type(v) == CEAgent 
            assert k == v.idn 
        self.cea_map = cea_map 
        self.prg = prg 
        return

    @staticmethod 
    def generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,s_conn_range,\
        t_conn_range,s_port_variance_range,prg): 

        prg_ = prg__single_to_int(prg)
        agent_idns = [i for i in range(num_agents)] 
        agent_idns = prg_seqsort(agent_idns,prg_)

        cea_map = dict() 
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
            
            cagent = CEAgent(a,set(r_nodes),s_port_variance,set(t_nodes),prg,prg_state_shape,\
                deepcopy(s_port_variance_range)) 
            cea_map[a] = cagent 
        return CEAgentNetwork(cea_map,prg)

    """
    main method 
    """
    def move_one_timestamp(self): 
        return -1 

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