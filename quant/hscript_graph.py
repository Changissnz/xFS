from graph_models.graph_gen import * 
from graph_models.path_induction import * 
from .levenschtein import * 

class HomoScriptAdmin: 

    def __init__(self,requirements,demand_map,open_info:bool): 
        assert type(requirements) == dict 
        assert type(demand_map) == dict 
        for v in demand_map.values():
            vk = set(v.keys())
            assert requirements == vk 
        assert type(open_info) == bool 

        self.requirements = requirements 
        # agent idn -> requirement idn -> list  
        self.demand_map = demand_map
        self.open_info = open_info
        return

    """
    agent_action_map := agent idn -> (requirement idn,path,idn of other agent imitated)
    """
    def register_agent_actions(self,agent_action_map): 
        if len(agent_action_map) == 0: return 

        dx = defaultdict(float) 
        redundancy = defaultdict(float)
        requirements = set() 
        for k,v in agent_action_map.items(): 

            # deduction #1: path difference 
            req_idn = v[0]
            expected_path = v[1] 
            q = self.path_difference(k,req_idn,expected_path) 
            dx[k] += q 

            # deduction #2: redundancy penalty given to original 
            if type(v[2]) != type(None): 
                dx[v[2]] += q / 2
    
            requirements |= {req_idn}

        # deduction #3: missing requirements deduction, evenly distributed 
        q = self.missing_requirements_deduction(requirements)
        q = q / len(agent_action_map) 

        for k in dx.keys(): 
            dx[k] += q 
        return dx

    def path_difference(self,agent_idn,req_idn,agent_path): 
        actual_path = self.demand_map[agent_idn][req_idn]
        return levenschtein_distance(actual_path,agent_path) 

    def missing_requirements_deduction(self,satisfied_reqs):
        q = self.requirements - satisfied_reqs
        c = 0 
        for x in q: 
            c += self.cumulative_sum_for_requirement(x)
        return c 
    
    def cumulative_sum_for_requirement(self,req_idn):
        c = 0 
        for v in self.demand_map.values(): 
            c += len(v[req_idn])
        return c 

    """
    agent_info_* := (agent idn, req idn, path)

    return: 
    - (original difference of agent 1) - (swapped difference of agent 1),
      (original difference of agent 2) - (swapped difference of agent 2). 
    """
    def approximate_swap_difference(self,agent_info_1,agent_info_2):
        if not self.open_info: 
            return 0,0 

        pd1 = self.path_difference(agent_info_1[0],agent_info_1[1],agent_info_1[2])
        pd2 = self.path_difference(agent_info_2[0],agent_info_2[1],agent_info_2[2])

        pd1_ = self.path_difference(agent_info_1[0],agent_info_2[1],agent_info_2[2])
        pd2_ = self.path_difference(agent_info_2[0],agent_info_1[1],agent_info_1[2])

        return pd1 - pd1_, pd2 - pd2_ 

class HomoScriptAgent: 

    def __init__(self,demand_map,chosen_req,score):
        assert type(demand_map) == dict 
        assert chosen_req in demand_map 
        assert score > 0 

        self.demand_map = demand_map 
        self.chosen_req = chosen_req
        self.score = score 
        return

    def role_swap_query(self): 
        return -1 

    def role_swap_response(self): 
        return -1 

    def exec(self): 
        return self.demand_map[self.chosen_req].p 

class HomoScriptNetwork: 

    def __init__(self,admin,agents,prg,info_mode_is_open:bool=False): 
        assert type(admin) == HomoScriptAdmin
        assert type(agents) == dict 
        for v in agents.values(): assert type(v) == HomoScriptAgent
        assert type(prg) in {MethodType,FunctionType}
        assert type(info_mode_is_open) == bool 

        self.admin = admin 
        self.agents = agents 
        self.deceased_agents = dict() 
        self.open_info = info_mode_is_open 
        self.fin_stat = False 
        return