from graph_models.graph_gen import * 
from graph_models.path_induction import * 
from .levenschtein import * 

"""
administrative agent in simulation Homo Frame Bot 
"""
class HomoScriptAdmin: 

    def __init__(self,requirements,demand_map,open_info:bool): 
        assert type(requirements) == set  
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

    #------------------------- phase one of admin actions: registering agent primary roles 

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
        return dx 

    def path_difference(self,agent_idn,req_idn,agent_path): 
        actual_path = self.demand_map[agent_idn][req_idn]
        return levenschtein_distance(actual_path,agent_path) 


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

    #------------------------- phase two of admin actions: registering agent extra roles 

    def missing_requirements_deduction(self,agent_actionset_map): 
        satisfied_reqs = set() 
        for v in agent_actionset_map.values(): 
            satisfied_reqs |= v 

        # deduction #3: missing requirements deduction, evenly distributed 
        q = self.missing_requirements_deduction_(satisfied_reqs)
        q = q / len(agent_actionset_map) 

        dx = dict() 
        for k in agent_actionset_map.keys(): 
            dx[k] += q 
        return dx

    def missing_requirements_deduction_(self,satisfied_reqs):
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
subject agent in simulation Homo Frame Bot 
"""
class HomoScriptAgent: 

    def __init__(self,idn,demand_map,chosen_req,prg,score):
        assert type(demand_map) == dict
        for k,v in demand_map.items(): 
            assert k == v[0] 

        assert chosen_req in demand_map 
        assert type(prg) in {MethodType,FunctionType}
        assert score > 0 

        self.idn = idn 
        self.demand_map = demand_map 
        self.chosen_req = chosen_req
        self.prg = prg 
        self.score = score 
        return

    def exec(self): 
        return (self.chosen_req,self.demand_map[self.chosen_req]) 

"""
network used in simulation Homo Frame Bot 
"""
class HomoScriptNetwork: 

    def __init__(self,admin,agents,prg,info_mode_is_open:bool=False,verbose:bool=False): 
        assert type(admin) == HomoScriptAdmin
        assert type(agents) == dict 
        for k,v in agents.values(): 
            assert k == v.idn 
            assert type(v) == HomoScriptAgent
        assert type(prg) in {MethodType,FunctionType}
        assert type(info_mode_is_open) == bool 

        self.admin = admin 
        self.agents = agents 
        self.terminated_agents = dict() 
        self.open_info = info_mode_is_open 
        self.verbose = verbose 
        self.fin_stat = len(self.agents) == 0  
        return

    def __next__(self):
        if self.fin_stat: return 

        dmap = self.premove__path_swap() 
        dx = self.admin.register_agent_actions(dmap) 
        self.deduct_scores(dx)
        if self.fin_stat: return 

        satisfied_reqs = set([v[0] for v in dmap.values()])
        remaining_reqs = self.admin.requirements - satisfied_reqs 

        erm = self.extra_role_map(remaining_reqs) 
        satisfied_reqs2 = set([v[0] for v in erm.values()]) 
        dx = self.admin.register_agent_actions(erm)
        self.deduct_scores(dx)
        if self.fin_stat: return 

        satisfied_reqs = satisfied_reqs | satisfied_reqs2 
        dx = self.missing_requirements_deduction(satisfied_reqs)
        self.deduct_scores(dx) 


    def deduct_scores(self,delta_map):
        terminated = []  
        for k,v in delta_map.items(): 
            self.agents[k].score -= v 
            if self.agents[k].score <= 0.: 
                terminated.append(k) 

        for d in terminated: 
            self.terminated_agents[d] = self.agents[d] 
            del self.agents[d] 
        self.fin_stat = len(self.agents) == 0 
        
    """
    agent_action_map := agent idn -> (requirement idn,path,idn of other agent imitated)
    """
    def base_action_map(self): 
        d = {} 
        for k,v in self.agents.items(): 
            q = v.exec() 
            d[k] = [q[0],q[1],None] 
        return d 

    #--------------------------------- phase 1 of agent decisions: agents deciding on paths to 
    #--------------------------------- take, based on swap scores. 

    def premove__path_swap(self):
        bmap = self.base_action_map() 
        agent_keys = sorted(sorted(set(agent_action_map.keys()))) 

        for agent_idn in agent_keys: 
            self.initiate_path_swap(agent_idn,bmap) 
        return bmap 

    def initiate_path_swap(self,agent_idn1,agent_action_map):  
        agent_keys = sorted(set(agent_action_map.keys()) - {agent_idn1}) 
        agent_info_1 = agent_action_map[agent_idn1] 

        for agent_idn2 in agent_keys:
            agent_info_2 = agent_keys[agent_idn2]         
            d0,d1 = self.admin.approximate_swap_difference(agent_info_1,agent_info_2)
            decision,two_way = self.swap_decision(agent_idn1,agent_idn2,d0,d1) 

            if decision and two_way: 
                agent_info_1[1],agent_info_2[1] = agent_info_2[1],agent_info_1[1] 
            elif decision: 
                agent_info_1[1] = agent_info_2[1] 
                agent_info_1[2] = agent_idn2 
            else: 
                pass  
        return 

    def swap_decision(self,agent_idn1,agent_idn2,d1,d2): 
        dec1 = d1 > 0 
        dec2 = d2 > 0 
        
        # case: both agents individually agree to swap 
        if dec1 and dec2: 
            return True,True  

        # case: through PRNG output comparison, agents go with 
        #       decision of the agent with the higher PRNG output.  
        prg1 = self.agents[agent_idn1].prg 
        prg2 = self.agents[agent_idn2].prg 
        d1 = prg_decimal(prg1,[0.,1.])
        d2 = prg_decimal(prg2,[0.,1.])

        if d1 >= d2: 
            return dec1,False 
        return dec2,False 
    
    #--------------------------------- phase 2 of agent decisions: taking up extra roles 

    def extra_role_map(self,remaining_reqs): 
        rem_req_map = {} 
        q = sorted(remaining_reqs) 
        for q_ in q: 
            x = self.extra_role_decision(q_) 
            if type(x) != type(None): 
                rem_req_map[x[0]] = [q_,x[1],None] 
        return rem_req_map 

    def extra_role_decision(self,req_idn):
        agent_candidates = prg_seqsort(sorted(self.agents.keys()),prg__single_to_int(self.prg)) 

        for a in agent_candidates: 
            agent = self.agents[a] 
            prg = prg__single_to_decimal(agent.prg)
            q = prg() 
            # case: agent does not accept taking extra role 
            if q < 0.5: 
                continue 

            # case: agent does accept taking extra role. cease iteration. 
            else: 
                P = self.extra_role_decision_(a,req_idn)
                return (a,P)
        return None 

    def extra_role_decision_(self,agent_idn,req_idn): 
        agent_path = self.agents[agent_idn].demand_map[req_idn] 

        terminated_keys = sorted(self.terminated_agents.keys())
        other_paths = [self.terminated_agents[a].demand_map[req_idn] for a in \
            terminated_keys]

        score = self.admin.path_difference(agent_idn,req_idn,agent_path)
        possible_paths = [(agent_path,score)] 
        if not self.open_info: 
            for p in other_paths: 
                possible_paths.append((p,score)) 
        else: 
            for p in other_paths: 
                score2 = self.admin.path_difference(agent_idn,req_idn,p)
                possible_paths.append((p,score2))

        possible_paths = prg_seqsort_ties(possible_paths,prg__single_to_int(self.prg),vf=lambda x:x[1]) 
        return possible_paths[-1][0]