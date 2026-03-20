from graph_models.controverter import * 

class GTAgentDecisionType: 

    def __init__(self,objective,objective_var):  
        self.objective = objective
        self.objective_var = objective_var 
        self.assert_parameters() 
        return

    def assert_parameters(self): 
        assert self.objective in {"self","others"} 
        if self.objective == "self": 
            assert self.objective_var in {0,1,2} 
        else: 
            assert len(self.objective_var) == 2 
            assert self.objective_var[0] in {0,1,2} 
            assert self.objective_var[1] in {0,1,2} 

    def change_objective(self,objective,objective_var): 
        self.objective = objective 
        self.objective_var = objective_var
        self.assert_parameters() 

    def decide(self,a_idn,mt:MultiAgentActionTable,other_agent_moves,prg=None): 
        assert issubclass(type(mt),MultiAgentActionTable)
        
        if self.objective == "self": 
            moves = mt.sort_agent_moves(a_idn,self.objective_var,other_agent_moves)
            return moves[-1][0] 
        
        index0,index1 = self.objective_var[0],self.objective_var[1] 
        return mt.agent_countermove_for_other_agents(a_idn,set(other_agent_moves.keys()),\
            other_agent_moves,index0,index1,prg = prg)

"""
Game Theory Agent. 
"""
class GTAgent: 

    def __init__(self,agent_idn,objective,objective_var,prg):  
        assert type(prg) in {MethodType,FunctionType,type(None)} 
        self.agent_idn = agent_idn 
        self.dec_maker = GTAgentDecisionType(objective,objective_var)
        self.prg = prg 
        return 

    def change_objective(self,objective,objective_var): 
        self.dec_maker.change_objective(objective,objective_var)

    def decision(self,mt:MultiAgentActionTable,other_agent_moves): 
        return self.dec_maker.decide(self.agent_idn,mt,other_agent_moves,self.prg) 

    @staticmethod 
    def best_decision_for_game(gta,gc,table): 
        assert type(gta) == GTAgent
        assert type(gc) == GameControverter
        assert table in {"c","i"} 

        T = gc.ftable if table == "i" else gc.ftable.agent_action_cmap
        M = {}
        for x in T.agents: 
            gta.agent_idn = x 
            M[x] = gta.decision(T,other_agent_moves={})
        return M 