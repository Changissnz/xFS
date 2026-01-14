from graph_models.agent_database import * 
from .ul_vec_classifier import * 

"""
communication/execution agent 
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
        self.communication_delta = defaultdict(defaultdict)  
        # source agent -> (positive resistance)::float 
        #   map is for cumulative values from source agent transmitted from agent connected to source 
        self.execution_delta = defaultdict(float)  
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