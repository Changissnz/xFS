from graph_models.graph_gen import * 
from graph_models.path_induction import * 

class HomoScriptAdmin: 

    def __init__(self,requirements,demand_map): 
        assert type(requirements) == dict 
        assert type(demand_map) == dict 

        self.requirements = requirements 
        # agent idn -> requirement idn -> NodePath 
        self.demand_map = demand_map
        return

class HomoScriptAgent: 

    def __init__(self,demand_map,chosen_req):
        assert type(demand_map) == dict 
        assert chosen_req in demand_map 

        self.demand_map = demand_map 
        self.chosen_req = chosen_req
        return

    def role_swap_query(self): 
        return -1 

    def role_swap_response(self): 
        return -1 

    def exec(self): 
        return self.demand_map[self.chosen_req].p 

class HomoScriptNetwork: 

    def __init__(self,admin,agents,prg): 
        assert type(admin) == HomoScriptAdmin
        assert type(agents) == dict 
        for v in agents.values(): assert type(v) == HomoScriptAgent

        self.admin = admin 
        self.agents = agents 
        return

