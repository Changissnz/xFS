from graph_models.agent_database import * 
from .ul_vec_classifier import * 

"""
communication/execution agent 

A port-based agent. There are three types of ports belonging to this agent: 
- R-port: port that relays the 'reaction' (typically a numerical vector) about 
          a <CEAgent> A, information received through the T-port, 
          from this agent to that agent A. 
- S-port: port that receives information on other <CEAgent>s.
- T-port: port that transmits information about one <CEAgent> to another <CEAgent>. 
"""
class CEAgent: 

    def __init__(self,idn,r_ports,s_port_variance,t_ports,prg,prg_state_shape,\
        cl_num_balls,cl_radius,new_s_port_var_range = [0.,1.],negative_reaction_allowed:bool=False):   
        assert type(idn) == int
        assert type(r_ports) == type(t_ports) == set 
        assert type(s_port_variance) == dict 
        assert type(prg_state_shape) == int and prg_state_shape > 0 
        assert type(negative_reaction_allowed) == bool 
        self.idn = idn 
        self.r_ports = r_ports 
        self.s_port_variance = s_port_variance
        self.t_ports = t_ports  
        self.prg = prg
        self.prg_state_shape = prg_state_shape
        self.new_s_port_var_range = new_s_port_var_range  
        self.negative_reaction_allowed = negative_reaction_allowed
        self.dbq = SimpleAgentDB(np.ndarray) 

        self.premeditated = []
        self.activity = [] 
        self.prev_act = None 
        self.current_query_idn = None 

        self.current_transmission = {}  
        self.current_reaction = defaultdict(float) 
        self.bc = VecClassifierTypeBC(cl_num_balls,cl_radius)

        self.score = 0 
        # source agent -> target agent -> (resistance)::float  
        #   map shows the resistance  values, absolute difference of 
        #   instance's variation on source agent's vector and target 
        #   agent's knowledge of source agent's vector. 
        #   aka source delta (sender end). Non-negative values. 
        self.communication_delta = defaultdict(defaultdict)  
        # source agent -> (positive resistance)::float 
        #   map is for cumulative values from source agent transmitted from agent connected to source 
        #   aka reaction delta (receiver end). -&0&+.
        self.execution_delta = defaultdict(float)  
        self.pdelta_log = [] 
        return

    def update_score(self,diff): 
        self.score += diff 

    def update_cdelta(self,d): 
        for s_port,t_ports in d.items(): 
            if s_port not in self.communication_delta: 
                self.communication_delta[s_port] = defaultdict(float) 
            for t,f in t_ports.items(): 
                self.communication_delta[s_port][t] += f 
        return 

    def __str__(self): 
        S = "Agent {}".format(self.idn) 
        S += "\n\tR-ports:\n{}\n".format(self.r_ports) 
        S += "\n\tS-ports:\n"
        for k,v in self.s_port_variance.items(): 
            S += "* agent {}, variance {}\n".format(k,v) 
        S += "\n\tT-ports:\n{}\n".format(self.t_ports) 
        return S 

    """
    latest vector from source connection 
    """    
    def receive_query_response(self,idn,r):   
        assert idn in self.s_port_variance
        self.dbq.update_info(idn,r) 

        # calculate the alternative point for 
        # transmitting to t-port agents 
        v = self.s_port_variance[idn]
        c = self.bc.contra_classify(r,v) 
        b = self.bc.bc.balls[c]
        r = modulo_in_range(self.prg(),[0.,b.radius])
        
        np_state = np.random.get_state()
        np.random.seed(abs(int(self.prg())))
        p2 = random_npoint_from_point(b.center,r) 
        np.random.set_state(np_state) 

        # load up the point 
        self.current_transmission[idn] = p2 
        return

    def clear_transmission(self): 
        self.current_transmission.clear()

    def clear_reaction(self): 
        self.current_reaction.clear() 
    
    def alter_port(self,idn,port_type,add_port:bool):  
        q = self.fetch_ports(port_type) 

        if port_type == "s": 
            if add_port: 
                assert idn not in q 
                q[idn] = modulo_in_range(self.prg(),self.new_s_port_var_range)  
            else: 
                assert idn in q 
                del q[idn] 
                self.dbq.delete_agent_info(idn) 
            return 

        if add_port: 
            assert idn not in q
            q |= {idn} 
        else: 
            assert idn in q 
            q -= {idn} 
            self.dbq.delete_agent_info(idn) 
        return

    def fetch_ports(self,port_type):
        assert port_type in {"r","s","t"}

        if port_type == "r": 
            return self.r_ports
        elif port_type == "s": 
            return self.s_port_variance
        else: 
            return self.t_ports

    def is_related(self,idn,port_type): 
        return idn in self.fetch_ports(port_type) 

    def act_one(self): 
        prg_ = prg__single_to_int(self.prg)
        q = np.cumprod(self.prg_state_shape)[-1]          
        x = np.zeros((q,))
        
        for i in range(q): x[i] = prg_()
        x = x.reshape(self.prg_state_shape) 
        return x

    def premeditate_acts(self,num_acts): 
        for _ in range(num_acts): 
            x = self.act_one()
            self.bc.input(x) 
            self.premeditated.append(x)
        return

    def next_act(self): 
        if len(self.premeditated) > 0: 
            q = self.premeditated.pop(0)
        else: 
            q = self.act_one() 
            self.bc.input(q)  

        self.activity.append(q) 
        self.prev_act = q 
        return q 

    ######################## used to make decisions on port deltas. Some of the logic is arbitrary in correlation to 
    ######################## objective of maximizing score 

    def close_port__max_decision(self,port_type:bool,actual_exec:bool):  

        if port_type == "r": 
            candidates = sorted([(k,v) for k,v in self.execution_delta.items() if k in self.r_ports],key=lambda x:x[1]) 
        elif port_type == "s":
            candidates = self.comm_delta_values(False)
            candidates = sorted([c for c in candidates if c[0] in self.s_port_variance],key=lambda x:x[1],reverse=True) 
        else: 
            candidates = self.comm_delta_values(True) 
            candidates = sorted([c for c in candidates if c[0] in self.t_ports],key=lambda x:x[1],reverse=True) 

        if len(candidates) == 0: return None 
        conn = candidates[0][0] 
        if actual_exec: self.alter_port(conn,port_type,False) 
        return candidates  

    def open_port__max_decision(self,port_type:bool,actual_exec:bool): 
        if port_type == "r": 
            candidates = self.comm_delta_values(True) 
            candidates = sorted([(c0,c1) for (c0,c1) in candidates if not c0 in self.r_ports],\
                        key=lambda x:x[1],reverse=True)  
        elif port_type == "s": 
            candidates = self.comm_delta_values(True) 
            candidates = sorted([(c0,c1) for (c0,c1) in candidates if not c0 in self.s_port_variance],\
                        key=lambda x:x[1]) 
        else: 
            candidates = self.comm_delta_values(False) 
            candidates = sorted([(c0,c1) for (c0,c1) in candidates if not c0 in self.t_ports],\
                        key=lambda x:x[1]) 

        if len(candidates) == 0: return None 
        conn = candidates[0][0] 
        if actual_exec: self.alter_port(conn,port_type,True) 
        return candidates

    def port_delta_decision(self): 
        # arbitrary decision-making by prng to proceed with a delta decision or not 
        d0,d1 = prg_decimal(self.prg,[0.,1.]),prg_decimal(self.prg,[0.,1.])  
        if int(self.prg()) % 2: 
            dx = [d0,d1]
        else: 
            dx = [d1,d0] 
        
        if dx[0] > dx[1]: 
            self.pdelta_log.append(None)
            return None 

        # proceeding with decision 
        candidates = [] 
        for x in ["r","s","t"]: 
            q = self.close_port__max_decision(x,False)
            if type(q) != type(None): 
                candidates.append((q[0][0],x,False)) 

            q2 = self.open_port__max_decision(x,False)
            if type(q2) != type(None): 
                candidates.append((q2[0][0],x,True))
        
        if len(candidates) == 0: 
            self.pdelta_log.append(None)
            return None  

        prg_ = prg__single_to_int(self.prg)
        candidates = prg_seqsort(candidates,prg_) 
        i = prg_() % len(candidates)
        c = candidates[i]
        self.pdelta_log.append(c) 
        self.alter_port(c[0],c[1],c[2])  
        return

    def comm_delta_values(self,is_tbasis): 
        candidates = [] 
        if not is_tbasis: 
            for k,v in self.communication_delta.items(): 
                v2 = sum(v.values())
                candidates.append((k,v2)) 
        else: 
            candidates = defaultdict(float)
            for k,v in self.communication_delta.items(): 
                for k2,v2 in v.items(): 
                    candidates[k2] += v2 
            candidates = [(k,v) for k,v in candidates.items()]
        return candidates

"""
data transmission bridge for CE Agent 
"""
class CEAgentDBBridge: 

    def __init__(self,cea:CEAgent,adb:SimpleAgentDB): 
        self.cea = cea 
        self.adb = adb 

    def exec_query(self,other_idn): 
        assert other_idn in self.adb.agent_idns and other_idn != self.cea.idn 
        assert other_idn in self.cea.s_port_variance 
        q = deepcopy(self.adb.agent_info[other_idn].last_info) 
        self.cea.receive_query_response(other_idn,q) 
        return

    def transmit_agent_state_to_db(self):
        self.adb.update_info(self.cea.idn,self.cea.prev_act)
        return

    def accept_transmission(self,subject_idn,v): 
        q = self.cea.dbq.last_info_for_agent(subject_idn) 
        stat = True 
        if type(q) == type(None): 
            q = deepcopy(v) 
            stat = False 

        d = euclidean_point_distance(v,q) 

        # case: negative reaction 
        if self.cea.negative_reaction_allowed:  
            if stat: 
                self.cea.current_reaction[subject_idn] += d
            else: 
                v_ = np.zeros((len(v),)) 
                d_ = euclidean_point_distance(v_,v)
                self.cea.current_reaction[subject_idn] -= d_ 
        else: 
            self.cea.current_reaction[subject_idn] += d

        return d  