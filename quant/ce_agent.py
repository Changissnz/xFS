from graph_models.agent_database import * 
from .ul_vec_classifier import * 

"""
communication/execution agent 
"""
class CEAgent: 

    def __init__(self,idn,r_ports,s_port_variance,t_ports,prg,prg_state_shape,\
        new_s_port_var_range = [0.,1.]):  
        assert type(idn) == int
        assert type(r_ports) == type(t_ports) == set 
        assert type(s_port_variance) == dict 
        assert type(prg_state_shape) == int and prg_state_shape > 0 

        self.idn = idn 
        self.r_ports = r_ports 
        self.s_port_variance = s_port_variance
        self.t_ports = t_ports  
        self.prg = prg
        self.prg_state_shape = prg_state_shape
        self.new_s_port_var_range = new_s_port_var_range  
        self.dbq = SimpleAgentDB(np.ndarray) 

        self.premeditated = []
        self.activity = [] 
        self.prev_act = None 
        self.current_query_idn = None 

        self.current_transmission = None 
        return 

    def load_transmission(self): 
        return -1 

    def receive_from_peer(self):  
        return -1 

    def __str__(self): 
        S = "Agent {}".format(self.idn) 
        S += "\n\tR-ports:\n{}\n".format(self.r_ports) 
        S += "\n\tS-ports:\n"
        for k,v in self.s_port_variance.items(): 
            S += "* agent {}, variance {}\n".format(k,v) 
        S += "\n\tT-ports:\n{}\n".format(self.t_ports) 
        return S 

    def pending_query(self,peer_idn):  
        assert peer_idn in self.known_other_agents
        self.current_query_idn = peer_idn 
        return 
    
    def receive_query_response(self,r):  
        self.dbq.update_agent(self.current_query_idn,r) 
        self.current_query_idn = None 
        return
    
    def alter_port(self,idn,port_type,add_port:bool):  
        q = self.fetch_ports(port_type) 

        if port_type == "s": 
            if add_port: 
                assert idn not in q 
                q[idn] = modulo_in_range(self.prg(),self.new_s_port_var_range)  
            else: 
                assert idn in q 
                del q[idn] 
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
        q = np.cumprod(self.prg_state_shape)[-1]          
        x = np.zeros((q,))
        for i in range(q): 
            x[i] = int(prg())
        x = x.reshape(self.prg_state_shape) 
        return x

    def premeditate_acts(self,num_acts): 
        for _ in range(num_acts): 
            x = self.act_one()
            self.premeditated.append(x)
        return

    def next_act(self): 
        if len(self.premeditated) > 0: 
            q = self.premeditated.pop(0)
        else: 
            q = self.act_one() 

        self.activity.append(q) 
        self.prev_act = q 
        return q 

"""
data transmission bridge for CE Agent 
"""
class CEAgentDBBridge: 

    def __init__(self,cea_map:CEAgent,adb:SimpleAgentDB): 
        self.cea = cea 
        self.adb = adb 

    def exec_query(self,other_idn): 
        assert other_idn in self.adb.agent_idns and other_idn != self.cea.idn 
        q = deepcopy(self.adb.agent_idns[other_idn].last_info) 
        self.cea.receive_query_response(q) 
        return

    def transmit_agent_state_to_db(self):
        self.adb.update_agent(self.cea.idn,self.cea.prev_act)
        return

    