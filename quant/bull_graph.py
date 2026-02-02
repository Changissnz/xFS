from graph_models.eb_graph_navigator import * 
from graph_models.radial_subgraph import * 
from graph_models.shortest_paths_approx import * 
from graph_models.sparse_graph_gen import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence

DEFAULT_BULL_NETWORK_MAX_EDGES = 10000 

# NOTE: shortest paths approximator used first uses default edge distance of 1 for 
#       all edges. As a result, paths between pairs of nodes may not be the cheapest in 
#       weight. 
class BullNetwork: 

    def __init__(self,G,edge_cost_function,entry_points,bull,agents,visual_radius,c2c_distance,prg,\
        open_info_mode,bull_is_2nd_premover:bool):   
        assert type(G) == defaultdict and edge_count(G) <= DEFAULT_BULL_NETWORK_MAX_EDGES
        assert type(prg) in {MethodType,FunctionType} 
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert entry_points.issubset(set(G.keys())) 
        assert type(bull) == EnergyBasedGraphNavigator
        assert type(agents) == dict 
        for k,v in agents.items(): 
            assert type(v) == EnergyBasedGraphNavigator 
            assert k == v.idn and k != bull.idn 
        assert 1 <= visual_radius <= c2c_distance 
        assert type(open_info_mode) == tuple and len(open_info_mode) == 2 and \
            set(open_info_mode).issubset({0,1})
        assert type(bull_is_2nd_premover) == bool

        self.G = G 
        self.edge_cost_function = edge_cost_function
        self.entry_points = entry_points 
        self.bull = bull 
        self.agents = agents 
        
        self.visual_radius = visual_radius 
        self.c2c_distance = c2c_distance 
        self.prg = prg
        self.oi_mode = open_info_mode
        self.bull_is_2nd_premover = bull_is_2nd_premover 

        self.spa = None 
        self.preproc() 
        return

    """
    calculates approximate shortest paths 
    """
    def preproc(self): 
        self.spa = ShortestPathsApproximator(self.G,is_dfs=False,max_subgraph_radius=5,prg=self.prg,max_periphery=50,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)   
        self.spa.exec() 
        return 

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
        D = self.feed_agent_other_contexts_(agent_idn) 

        entire_nodeset = set() 
        for v in D.values(): 
            entire_nodeset |= v[1] 

        loc = self.agents[agent_idn].location() 
        q = self.spa.shortest_paths_from_node_to_nodeset(loc,entire_nodeset,True)
        for k,v in q.items(): 
            q[k] = v.adjust_weights(self.edge_cost_function) 

        A = self.agents[agent_idn]
        A.add_other_chasers_info(D,q) 

    def feed_agent_other_contexts_(self,agent_idn): 
        assert agent_idn in self.agents 
        other_agents = set(self.agents.keys()) - {agent_idn} 

        loc_ = self.agents[agent_idn].location() 
        d = {} 
        for a2 in other_agents: 
            loc = self.agents[a2].location() 

            px = self.spa.shortest_path(loc_,loc,False) 
            if type(px) == type(None): 
                continue 
            px = px.adjust_weights(self.edge_cost_function)
            if len(px.pweights) <= self.c2c_distance: 
                nodeset = set(self.agents[a2].context.keys())            
                d[a2] = (loc,nodeset) 
        return d 

    def shortest_paths_of_subgraph(self,sg:defaultdict): 
        keys = sorted(sg.keys()) 
        dx = dict() 

        for k in keys: 
            for k2 in keys: 
                # case: path already exists 
                if (k,k2) in self.spa.nodepair_path_info: 
                    dx[(k,k2)] = self.spa.nodepair_path_info[(k,k2)] 
                    dx[(k,k2)] = dx[(k,k2)].adjust_weights(self.edge_cost_function)
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
                    dx[(k,k2)] = dx[(k,k2)].adjust_weights(self.edge_cost_function)
        return dx 

    def premove(self): 
        return -1 

    def open_info_mode(self): 
        return -1 

    def pass_info_from(self,bull): 
        return -1 

    @staticmethod 
    def generate_instance(num_nodes,growth_type,num_entry_points,\
        num_agents,visual_radius,c2c_distance,prg,open_info_mode,\
        bull_is_2nd_premover,bull_energy,chaser_energy,\
        weight_range=[1,10]):

        G = BullNetwork.generate_base_graph(num_nodes,prg,growth_type) 
        return BullNetwork.generate_instance_(G,num_entry_points,num_agents,\
            visual_radius,c2c_distance,prg,open_info_mode,bull_is_2nd_premover,\
            bull_energy,chaser_energy,weight_range)


    @staticmethod 
    def generate_instance_(G,num_entry_points,num_agents,visual_radius,\
        c2c_distance,prg,open_info_mode,bull_is_2nd_premover,bull_energy,\
        chaser_energy,weight_range=[1,10]): 
        assert len(G) >= num_agents + 1 

        # choose the entry points 
        q = sorted(G.keys())
        entry_points = prg_choose_n(q,num_entry_points,prg__single_to_int(prg),is_unique_picker=False) 
        entry_points = set(entry_points)

        # make the edge cost function 
        gw = GraphWeightGen(G,prg,is_dsg=False,weight_range=weight_range)
        edge_cost_function = gw.weight 

        # choose the agent and bull locations 
        n = num_agents + 1
        q = sorted(G.keys())
        locations = prg_choose_n(q,n,prg__single_to_int(prg),is_unique_picker=False) 

        prgs = prg_to_prg__LCG_sequence(prg,num_agents+1,3.4123) 

        # make the agents 
        bull_idn = 0 
        bull_loc = locations.pop(0)
        bull = EnergyBasedGraphNavigator(bull_idn,bull_loc,bull_energy,prgs.pop(0),True)

        agents = {}
        for i in range(1,num_agents+1): 
            loc = locations.pop(0)
            agent = EnergyBasedGraphNavigator(i,loc,chaser_energy,prgs.pop(0),False) 
            agents[i] =agent 

        return BullNetwork(G,edge_cost_function,entry_points,bull,agents,\
            visual_radius,c2c_distance,prg,open_info_mode,bull_is_2nd_premover)

    @staticmethod
    def generate_base_graph(num_nodes,prg,growth_type): 

        leaf_backtrack_conn_ratio_range = [0.05,0.15] 
        backtrack_conn_range = [3,7]
        branching_range = [1,4] 

        sgg = SparseConnectedGraphGen(num_nodes,leaf_backtrack_conn_ratio_range,backtrack_conn_range,\
            is_dsg=False,prg=prg,branching_range=branching_range,\
            growth_type=growth_type)
        sgg.make() 
        return sgg.d 