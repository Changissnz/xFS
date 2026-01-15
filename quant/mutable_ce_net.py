from .ce_net import * 

class MutableCEAgentNetwork(CEAgentNetwork): 

    def __init__(self,cea_map,prg):
        super().__init__(cea_map,prg,True) 
        self.deterministic_one_hundred(True) 
        self.auto_agents = set() 

        self.pending_decisions = dict()  
        return

    def __next__(self):
        self.move_one_timestamp() 
        self.auto_agent_decisions()  
        return

    def set_auto_agents(self,aset): 
        assert type(aset) == set 
        for a in aset: 
            assert a in self.cea_map 
        self.auto_agents = aset 

    def set_agent_prg(self,idn,prg): 
        q = self.fetch_agent(idn) 
        q.prg = prg 
        return 

    def agent_scores(self): 
        return {k:v.score for k,v in self.cea_map.items()} 

    @staticmethod 
    def generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,s_conn_range,\
        t_conn_range,s_port_variance_range,prg,cl_num_balls=50,prg_output_range=[-1000,1000],\
        cl_radius_ratio = 0.1):  

        can = CEAgentNetwork.generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,\
            s_conn_range,t_conn_range,s_port_variance_range,prg,cl_num_balls,prg_output_range,\
            cl_radius_ratio,True,True) 
        return MutableCEAgentNetwork(can.cea_map,can.prg)

    def auto_agent_decisions(self): 
        ordering = prg_seqsort(sorted(self.auto_agents),prg__single_to_int(self.prg)) 
        for i in ordering: 
            self.cea_map[i].port_delta_decision() 
        return