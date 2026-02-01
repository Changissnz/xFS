from .network_capform import * 
from graph_models.radial_subgraph import * 
from graph_models.shortest_paths_approx import * 

class BullNetwork: 

    def __init__(self,G,edge_cost_function,entry_points,bull,agents,visual_radius,c2c_distance,prg):   
        assert type(G) == defaultdict 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert entry_points.issubset(set(G.keys())) 
        assert type(bull) == EnergyBasedGraphNavigator
        assert type(agents) == dict 
        for k,v in agents.items(): 
            assert type(v) == EnergyBasedGraphNavigator 
            assert k == v.idn and k != bull.idn 
        assert 1 <= visual_radius <= c2c_distance 

        self.G = G 
        self.edge_cost_function = edge_cost_function
        self.entry_points = entry_points 
        self.bull = bull 
        self.agents = agents 
        
        self.visual_radius = visual_radius 
        self.c2c_distance = c2c_distance 
        self.prg = prg 

        self.spa = None 
        self.preproc() 
        return

    """
    calculates approximate shortest paths 
    """
    def preproc(self): 
        self.spa = ShortestPathsApproximator(self.G,is_dfs=False,max_subgraph_radius=3,prg=self.prg,max_periphery=50,\
                edge_cost_function=self.edge_cost_function) 
        self.spa.exec() 
        self.spa.add_12000_new_paths() 
        return 

    def shortest_paths_of_subgraph(self,sg:defaultdict): 
        keys = sorted(sg.keys()) 
        dx = dict() 

        for k in keys: 
            for k2 in keys: 
                # case: path already exists 
                if (k,k2) in self.spa.nodepair_path_info: 
                    dx[(k,k2)] = self.spa.nodepair_path_info[(k,k2)] 
                    continue 

                # case: inverse of path exists 
                if (k2,k) in dx: 
                    p = dx[(k2,k)] 
                    dx[(k,k2)] = p.invert() 
                    continue 

                # case: deduce new path 
                pths = self.spa.deduce_path(k,k2,True) 
                if len(pths) == 0: 
                    continue 
                else: 
                    dx[(k,k2)] = self.spa.nodepair_path_info[(k,k2)]
        return dx 
         
    # NOTE: somewhat inefficient method. Calculates shortest paths twice. 
    def context_for_agent(self,a_idn): 
        agent = None 
        is_bull = False 
        if a_idn in self.agents: 
            agent = self.agents[a_idn] 
        else: 
            assert a_idn == self.bull.idn 
            agent = self.bull 
            is_bull = True 

        assert type(agent) != type(None)

        qsf = QuickSubgraphFetcher(self.G,self.prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)
        G_ = qsf.subgraph(agent.location(),self.visual_radius)
        spaths = self.shortest_paths_of_subgraph(G_)

        bull_loc = None 
        if not is_bull: 
            x = self.bull.location() 
            if x in G_: 
                bull_loc = x 

        chaser_locs = None 
        if is_bull: 
            q = set({v.location() for v in self.agents.values()}) 
            chaser_locs = q.intersection(set(G_.keys()))
        agent.receive_context(G_,spaths,bull_loc,chaser_locs) 
        return

    def feed_agent_other_contexts(self,agent_idn): 
        assert agent_idn in self.agents 
        other_agents = set(self.agents.keys()) - {agent_idn} 

        loc_ = self.agents[agent_idn].location() 
        d = {} 
        for a2 in other_agents: 
            loc = self.agents[a2].location() 

            px = self.spa.shortest_path(loc_,loc,False) 
            if type(px) == type(None): 
                continue 

            if len(px.pweights) <= self.c2c_distance: 
                nodeset = set(self.agents[a2].context.keys())            
                d[a2] = (loc,nodeset) 
        return d 

    @staticmethod 
    def generate_instance(G,num_entry_points,num_agents,visual_radius):
        return -1 

    @staticmethod
    def generate_base_graph(): 
        return -1 