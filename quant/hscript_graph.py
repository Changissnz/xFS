from graph_models.graph_gen import * 
from graph_models.path_induction import * 
from .levenschtein import * 
from morebs2.numerical_generator import prg_choose_n,prg_to_prg__LCG_sequence,\
    prg_decimal,prg__single_to_decimal

DEFAULT_HOMO_FRAME_BOT_GRAPH_NODE_RANGE = [500,2000] 
DEFAULT_HOMO_FRAME_BOT_GRAPH_CONNECTIVITY = [0.00005,0.01]
DEFAULT_HOMO_FRAME_BOT_PATH_LENGTH_RANGE = [5,55] 

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
        if len(agent_action_map) == 0: return dict() 

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
        s = simple_string_cmp_metric(actual_path,agent_path) 
        return s 

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

    def missing_requirements_deduction(self,active_agent_set,satisfied_reqs): 
    
        # deduction #3: missing requirements deduction, evenly distributed 
        q = self.missing_requirements_deduction_(satisfied_reqs)
        q = q / len(active_agent_set) 

        dx = dict() 
        for k in active_agent_set: 
            dx[k] = q 
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

    def __str__(self): 
        s = "agent idn: {}, chosen req: {}, score: {}".format(self.idn,self.chosen_req,self.score) + "\n" 
        return s 

    def exec(self): 
        return (self.chosen_req,self.demand_map[self.chosen_req]) 

"""
network used in simulation Homo Frame Bot 
"""
class HomoScriptNetwork: 

    def __init__(self,admin,agents,prg,info_mode_is_open:bool=False,verbose:bool=False): 
        assert type(admin) == HomoScriptAdmin
        assert type(agents) == dict 
        for k,v in agents.items(): 
            assert k == v.idn 
            assert type(v) == HomoScriptAgent
            qd = set(v.demand_map.keys())
            assert qd == admin.requirements

        assert type(prg) in {MethodType,FunctionType}
        assert type(info_mode_is_open) == bool 

        self.admin = admin 
        self.agents = agents 
        self.prg = prg 
        self.terminated_agents = dict() 
        self.open_info = info_mode_is_open 
        self.verbose = verbose 
        self.fin_stat = len(self.agents) == 0  
        self.timestamp = 0 
        return

    def set_prgs_for_agents(self,base_prng): 
        q = sorted(self.agents.keys()) 
        l = len(q) 
        prngs = prg_to_prg__LCG_sequence(base_prng,l,2+771/980) 

        for q_ in q: 
            agent = self.agents[q_] 
            agent.prg = prngs.pop(0)
        return 

    def __next__(self):
        if self.fin_stat: return 
        if self.verbose: 
            print("---------------------------------------------------------------------------")
            print("\t\tTIMESTAMP ",self.timestamp)
            print("---------------------------------------------------------------------------")

        self.timestamp += 1 

        dmap = self.premove__path_swap() 
        if self.verbose: 
            print("-- planned moves")
            for k,v in dmap.items(): 
                print("* agent: {}  score: {}".format(k,self.agents[k].score)) 
                print("* default requirement: {}".format(self.agents[k].chosen_req))
                print("* requirement: {}".format(v[0]))
                ##print("path: {}".format(v[1])) 
                print("* imitating: {}".format(v[2])) 
                print() 

        dx = self.admin.register_agent_actions(dmap) 
        self.deduct_scores(dx)
        if self.fin_stat: return 

        satisfied_reqs = set([v[0] for v in dmap.values()])
        remaining_reqs = self.admin.requirements - satisfied_reqs 

        erm,rem_reqs = self.extra_role_map() 
        if self.verbose and len(erm) > 0: 
            print("-- extra roles") 
            for k,v in erm.items(): 
                print("* agent: {}  extra roles: {}".format(k,[v_[0] for v_ in v])) 
                print() 

        sat_reqs = self.register_extra_roles(erm) 
        if self.fin_stat: return 

        satisfied_reqs = satisfied_reqs | sat_reqs 
        dx = self.admin.missing_requirements_deduction(set(self.agents.keys()),satisfied_reqs)
        if self.verbose and len(dx) > 0: 
            q = set(dx.values()) 
            d = len(self.admin.requirements) - len(satisfied_reqs)
            print("[!] missing {} requirements. deducting {} from each agent".format(d,q.pop())) 
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

    """
    return:
    - dict, agent idn -> | (path of agent's chosen req) - admin.paths[agent idn][agent's chosen req] |
    """
    def default_path_differences(self): 
        d = {} 
        for k,v in self.agents.items(): 
            q0,q1 = v.exec()
            d[k] = self.admin.path_difference(k,q0,q1) 
        return d 

    #--------------------------------- phase 1 of agent decisions: agents deciding on paths to 
    #--------------------------------- take, based on swap scores. 

    def premove__path_swap(self):
        bmap = self.base_action_map() 
        agent_keys = prg_seqsort(sorted(set(bmap.keys())),prg__single_to_int(self.prg)) 

        for agent_idn in agent_keys: 
            self.initiate_path_swap(agent_idn,bmap) 
        return bmap 

    def initiate_path_swap(self,agent_idn1,agent_action_map):  
        agent_keys = sorted(set(agent_action_map.keys()) - {agent_idn1}) 
        agent_info_1 = agent_action_map[agent_idn1] 

        for agent_idn2 in agent_keys:
            agent_info_2 = agent_action_map[agent_idn2]   

            ai1 = [agent_idn1,agent_info_1[0],agent_info_1[1]] 
            ai2 = [agent_idn2,agent_info_2[0],agent_info_2[1]] 

            d0,d1 = self.admin.approximate_swap_difference(ai1,ai2)
            decision,two_way = self.swap_decision(agent_idn1,agent_idn2,d0,d1) 

            if decision and two_way: 
                print("swap {} <<---->> {}".format(agent_idn1,agent_idn2)) 
                agent_info_1[0],agent_info_2[0] = agent_info_2[0],agent_info_1[0]  
                agent_info_1[1],agent_info_2[1] = agent_info_2[1],agent_info_1[1] 
            elif decision: 
                print("swap {} <<---- {}".format(agent_idn1,agent_idn2)) 
                agent_info_1[0] = agent_info_2[0] 
                agent_info_1[1] = agent_info_2[1] 
                agent_info_1[2] = agent_idn2 
            else: 
                pass  
        return 

    def swap_decision(self,agent_idn1,agent_idn2,d1,d2): 
        dec1 = d1 > 0 
        dec2 = d2 > 0 
        
        # case: open info, both agents individually agree to swap 
        if dec1 and dec2: 
            return True,True  

        prg1 = self.agents[agent_idn1].prg 
        prg2 = self.agents[agent_idn2].prg 

        # case: agents make decision to swap based on PRNG, due to 
        #       no open info. 
        if not self.open_info: 
            dec1 = prg_decimal(prg1,[0.,1.]) >= 0.5 
            dec2 = prg_decimal(prg2,[0.,1.]) >= 0.5 

        d1 = prg_decimal(prg1,[0.,1.])
        d2 = prg_decimal(prg2,[0.,1.])

        # go with decision of the agent with the higher PRNG output.  
        if d1 >= d2: 
            return dec1,False 
        return dec2,False 
    
    #--------------------------------- phase 2 of agent decisions: taking up extra roles 

    def register_extra_roles(self,erm): 
        sat_reqs = [] 
        while len(erm) > 0: 
            d = dict() 
            empty = [] 
            for k,v in erm.items(): 
                d[k] = v.pop(0) 
                if len(v) == 0: 
                    empty.append(k) 
            for t in empty: 
                del erm[t] 
            
            terminated = [] 
            for k,v in d.items(): 
                if k in self.terminated_agents: 
                    terminated.append(k)
                else: 
                    sat_reqs.append(v[0]) 
            for t in terminated: del d[t] 

            dx = self.admin.register_agent_actions(d)
            self.deduct_scores(dx)
        return set(sat_reqs) 

    def extra_role_map(self): 
        if len(self.terminated_agents)  == 0: 
            return dict(),set() 

        rem_req_map = defaultdict(list) 
        q = sorted(self.terminated_agents.keys()) 
        rem_reqs = [] 
        for q_ in q: 
            x = self.terminated_agents[q_].chosen_req 
            d = self.extra_role_decision(x) 
            if type(d) != type(None): 
                rem_req_map[d[0]].append([x,d[1],None]) 
            else: 
                rem_reqs.append(x) 
        return rem_req_map,set(rem_reqs)

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

    #------------------------------------------------------------------------------ 

    @staticmethod 
    def generate_instance(num_agents,prg,agent_score,open_info): 
        assert num_agents <= 200 

        # generate the graph 
        is_dsg = False 
        is_realtime_gen = bool(int(prg()) % 2) 
        vertex_degree = modulo_in_range(int(prg()),DEFAULT_HOMO_FRAME_BOT_GRAPH_NODE_RANGE)
        edge_connectivity = modulo_in_range(prg(),DEFAULT_HOMO_FRAME_BOT_GRAPH_CONNECTIVITY)
        verbose = False 
        gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,\
            edge_connectivity,verbose=False)
        gg.full_run() 
        G = graph_to_one_component(gg.d,prg)

        # choose `num_agents` sources and `num_agents` targets 
        X = prg_choose_n(sorted(G.keys()),num_agents * 2,prg__single_to_int(prg),True)
        sources = X[:num_agents] 
        targets = X[num_agents:] 

        # calculate shortest paths for each source 
        spaths = {} 
        for s in sources: 
            bdfsc = BDFSCache(s,G,is_bfs=True,prg=prg,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,num_paths_per_node=3,\
                max_search_radius=float('inf'),verbose=False)
            bdfsc.exec() 
            path_ind = PathInduction(s,bdfsc.min_paths,prg,[2,4]) 
            spaths[s] = path_ind 

        # calculate paths for every agent         
        prgs = prg_to_prg__LCG_sequence(prg,num_agents,3.111+2/97) 
        sources_ = prg_seqsort(sorted(sources),prg__single_to_int(prg)) 
        agents = {} 
        admin_demand_map = {} 
        for j,idn in enumerate(range(num_agents)): 
            demand_map = {} 
            admin_demand_map[idn] = dict() 
            for (i,requirement) in enumerate(sources): 
                # path for agent 
                path_length = modulo_in_range(int(prg()),DEFAULT_HOMO_FRAME_BOT_PATH_LENGTH_RANGE)
                target = targets[i]
                pinduction = spaths[requirement] 
                roundabout_first = int(prg()) % 2
                P = pinduction.one_path(target,roundabout_first,path_length)
                demand_map[requirement] = P.p 

                # path for admin 
                path_length2 = modulo_in_range(int(prg()),DEFAULT_HOMO_FRAME_BOT_PATH_LENGTH_RANGE)
                roundabout_first2 = int(prg()) % 2
                q = pinduction.prg 
                pinduction.prg = prgs[j] 
                P2 = pinduction.one_path(target,roundabout_first2,path_length2) 
                pinduction.prg = q 

                admin_demand_map[idn][requirement] = P2.p 
            
            # initialize the agent 
            chosen_req = sources_[j] 
            prg_ = prgs[j] 
            agent = HomoScriptAgent(idn,demand_map,chosen_req,prg_,agent_score)
            agents[idn] = agent 

        # initialize the admin 
        admin = HomoScriptAdmin(set(sources),admin_demand_map,open_info)
        hsn = HomoScriptNetwork(admin,agents,prg,info_mode_is_open=open_info,verbose=False)
        return hsn 