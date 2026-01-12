from graph_models.agent_database import * 
from .ul_vec_classifier import * 

"""
communication/execution agent 
"""
class CEAgent: 

    def __init__(self,idn,r_ports,s_ports,t_ports,s_port_variance,prg,prg_state_shape):  
        assert type(idn) == int
        assert type(r_ports) == type(s_ports) == \
            type(t_ports) == set
        assert type(prg_state_shape) == int and prg_state_shape > 0 

        self.idn = idn 
        self.r_ports = r_ports 
        self.s_ports = s_ports
        self.t_ports = t_ports  
        self.s_port_variance = s_port_variance
        self.prg = prg
        self.prg_state_shape = prg_state_shape 
        self.dbq = SimpleAgentDB(np.ndarray) 

        self.premeditated = []
        self.activity = [] 
        self.prev_act = None 
        self.current_query_idn = None 
        return 

    def transmit(self): 
        return -1 

    def receive_from_peer(self):  
        return -1 

    def pending_query(self,peer_idn):  
        assert peer_idn in self.known_other_agents
        self.current_query_idn = peer_idn 
        return 
    
    def receive_query_response(self,r):  
        self.dbq.update_agent(self.current_query_idn,r) 
        self.current_query_idn = None 
        return
    
    def alter_port(self,idn,port_type,add_port:bool):  
        assert port_type in {"r","s","t"}

        if port_type == "r": 
            q = self.r_ports
        elif port_type == "s": 
            q = self.s_ports
        else: 
            q = self.t_ports

        if add_port: 
            assert idn not in q
            q |= {idn} 
        else: 
            assert idn in q 
            q -= {idn} 
        return

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

    