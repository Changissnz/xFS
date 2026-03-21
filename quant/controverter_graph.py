from quant.gt_agent import * 
from graph_models.node_path import * 
from morebs2.numerical_generator import prg_decimal,prg_to_prg__LCG_sequence,\
    prg_partition_for_float__type2

class ControverterNet: 

    def __init__(self,amap:dict,tmap:dict,N:NodePath,prg,allow_agent_move_knowledge,\
        is_correlation_variable:bool): 

        for v in amap.values(): assert type(v) == GTAgent
        assert len(amap) > 1 

        for v in tmap.values(): assert type(v) == GameControverter
        assert set(tmap.keys()) == set(N.p)

        assert type(N) == NodePath
        assert type(allow_agent_move_knowledge) == bool 
        assert type(is_correlation_variable) == bool 


        self.amap = amap 
        self.tmap = tmap 
        self.N = N
        self.prg = prg 

        self.auto_agents = set(amap.keys()) 
        self.nonauto_agents = set()

        self.allow_agent_move_knowledge = allow_agent_move_knowledge
        self.is_correlation_variable = is_correlation_variable
        return

    def set_non_auto_agent(self,a_idn,prg=None): 
        assert a_idn in self.amap 
        self.nonauto_agents |= {a_idn}
        self.auto_agents -= {a_idn}

        if type(prg) in {MethodType,FunctionType}:
            self.amap[a_idn].prg = prg 
        return 

    def set_auto_agent(self,a_idn,prg=None): 
        assert a_idn in self.amap 
        self.auto_agents |= {a_idn}
        self.nonauto_agents -= {a_idn}

        if type(prg) in {MethodType,FunctionType}:
            self.amap[a_idn].prg = prg 
        return

    def prng_set_correlation_values(self): 
        for node_idn in self.N: 
            if type(node_idn) == type(None): 
                break 
            d0 = prg_decimal(self.prg,[0.,1.])
            d1 = prg_decimal(self.prg,[0.,1.]) 
            self.set_correlation_values_for_node(node_idn,d0,d1) 
        return 

    def set_correlation_values(self,pcorrelation_payoff,pcorrelation_upturn): 
        for node_idn in self.N: 
            if type(node_idn) == type(None): 
                break 
            self.set_correlation_values_for_node(node_idn,pcorrelation_payoff,pcorrelation_upturn)
    
    def set_correlation_values_for_node(self,node_idn,pcorrelation_payoff,pcorrelation_upturn): 

        C = self.tmap[node_idn]
        if type(pcorrelation_payoff) != type(None): 
            C.pcorrelation_payoff = pcorrelation_payoff
        if type(pcorrelation_upturn) != type(None): 
            C.pcorrelation_upturn = pcorrelation_upturn

    def __next__(self): 
        for node_idn in self.N: 
            if type(node_idn) == type(None): break 
            self.process_at_node(node_idn,self.allow_agent_move_knowledge)
        
        if self.is_correlation_variable:
            self.prng_set_correlation_values()

    def agent_value_ranking(self):
        d = [] 
        for k in self.amap.keys(): 
            a = self.amap[k]
            v = a.value
            d.append((k,v))
        d = sorted(d,key=lambda x:x[1])[::-1] 
        s = "" 
        for d_ in d: 
            s += "agent {} value {}\n".format(d_[0],d_[1]) 
        s += "\n"
        return s 

    def process_at_node(self,node_idn,allow_agent_move_knowledge:bool):  
        # sort the agents by prng 
        agent_idns = prg_seqsort(sorted(self.amap.keys()),self.prg) 
        d = {} 
        k = {} 

        # have each agent decide 
        for a in agent_idns:
            # account for cumulative payoffs 
            ag = self.amap[a] 
            ag.account_for_payoffs()  

            # decide next move 
            m = self.agent_decision(a,node_idn,k) 
            d[a] = m 

            if allow_agent_move_knowledge: 
                k[a] = m 
        
        # update payoffs 
        self.process_agent_decisions(node_idn,d) 

        # update Controverter 
        C = self.tmap[node_idn] 
        ##print("DD")
        ##print(d) 
        
        C.recv_agent_move_map(d) 
        next(C)
        return

    """
    loads info for agent payoffs based on decisions in `dec_map`.
    """
    def process_agent_decisions(self,node_idn,dec_map):
        s = agent_move_map_to_string(dec_map)

        C = self.tmap[node_idn] 
        
        map_i = C.ftable[s]
        map_c = C.ftable.agent_action_cmap[s]
        map_d = C.ftable.agent_action_dmap[s]

        # adjust cumulative by subtracting immediate 
        keys = sorted(map_c.keys())
        for k in keys: 
            map_c[k] = map_c[k] - map_i[k] 
            map_d[k] -= 1 

        # partition cumulative according to duration, using 
        # each agent's PRNG 
        map_cseq = {} 
        for k in keys:
            d = map_d[k]
            F = map_c[k]

            px = self.amap[k].prg
            map_cseq[k] = list(prg_partition_for_float__type2(F,d,px,m=1))

        # add (immediate,cumulative) to each agent's info.  
        for k in keys: 
            a = self.amap[k] 
            d = dec_map[k] 
            i = float(map_i[k])
            c = map_cseq[k]
            a.add_to_payoff_queue(d,i,c) 

        return

    def agent_decision(self,a_idn,node_idn,other_agent_moves): 
        C = self.tmap[node_idn] 

        if a_idn in self.auto_agents: 
            ranked_moves = C.rank_agent_moves(a_idn,is_cumulative_payoff=True)
            #print("RANKING")
            #print(ranked_moves)
            return ranked_moves[-1][0] 
        else: 
            # choose cumulative or immediate type 
            a = self.amap[a_idn] 
            q = prg_decimal(a.prg,[0.,1.]) 
            t = None 
            #   cumulative 
            if q >= 0.5: 
                t = C.ftable 
            #   immediate
            else: 
                t = C.ftable.agent_action_cmap
            
            # set agent decision type 
            self.switch_nonauto_agent_decision_type(a_idn)

            # decide 
            other_agents = set(self.amap.keys()) - {a_idn}
            d = a.decision(t,other_agents,other_agent_moves)
            return d 

    def switch_nonauto_agent_decision_type(self,a_idn): 
        a = self.amap[a_idn]
        x = int(a.prg()) % 6

        if x < 3: 
            a.change_objective("self",x) 
        else: 
            one = int(a.prg()) % 3
            two = int(a.prg()) % 3
            a.change_objective("others",(one,two)) 
        return

    @staticmethod 
    def generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg,allow_agent_move_knowledge=False,\
        is_correlation_variable=True): 
        assert type(path_size) == int and path_size > 0 

        N = NodePath.preload([i for i in range(path_size)],[1 for _ in range(path_size -1)])
        tmap = {} 
        for i in range(path_size): 
            print("-- controverter for node {}".format(i))
            n = ControverterNet.generate_one_node(num_agents,\
                agent_action_value_range,\
                cumulative_payoff_multiplier_range,prg)
            tmap[i] = n 

        agents = {} 
        prg_seq = prg_to_prg__LCG_sequence(prg,num_agents,45.5+67.7) 
        for i in range(num_agents): 
            agents[i] = GTAgent(i,"self",2,prg_seq[i]) 

        return ControverterNet(agents,tmap,N,prg,allow_agent_move_knowledge,\
            is_correlation_variable)  

    @staticmethod
    def generate_one_node(num_agents,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg): 

        agents = {i for i in range(num_agents)}
        agent2movesize_map = {i:\
            modulo_in_range(int(prg()),GameControverter.DEFAULT_GAME_AGENT_MOVE_SIZE_RANGE) \
            for i in range(num_agents)} 
        move_idn_counter = SimpleCounter(0).__next__ 
        pcorrelation_payoff = prg_decimal(prg,[0.,1.]) 
        pcorrelation_upturn = prg_decimal(prg,[0.,1.]) 

        T = GameControverter.generate_instance(agents,agent2movesize_map,agent_action_value_range,\
            prg,GameControverter.DEFAULT_GAME_AGENT_PAYOFF_MOVE_BRACKET_RANGE,move_idn_counter,\
            cumulative_payoff_multiplier_range,pcorrelation_payoff,pcorrelation_upturn)
        return T