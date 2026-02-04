from graph_models.eb_graph_navigator import * 
from graph_models.community import * 
from graph_models.sparse_graph_gen import * 
from graph_models.graph_gen import * 

from morebs2.numerical_generator import prg_to_prg__LCG_sequence,prg_decimal

DEFAULT_BULL_NETWORK_MAX_EDGES = 10000 

"""
<BullNetwork> is a network with n Chaser agents and 1 Bull agent. The Chasers chase the 
Bull. 

G is an undirected graph of one component.  

At every timestamp, every Chaser c is fed a subgraph context C of G. Every node of C is 
at most `visual_radius` unweighted edge distance to node location of c. Context C is the 
maximum spanning subgraph of radius `visual_radius` that centers around c's node location. 
This context C is what Chaser c has available as its visual. If the Bull is on any node of 
C, c would be able to independently detect it.

The Chasers can coordinate with each other. For any pair of Chasers c0 and c1, if 
unweighted edge distance between node locations of c0 and c1 is at most `c2c_distance`, 
c0 and c1 would pass their graph contexts to each other, resulting in each of c0 and c1 having 
a larger visual from the combined. Both c0 and c1 would be able to travel to every node 
in this larger visual, starting from their current locations. 

The objective of the Chasers is to capture the Bull. To do so, a minumum of one Chaser must 
be located on the same node as that of the Bull. There are four possible information modes for 
<BullNetwork> (see variable<open_info_mode>), pertinent for when a Chaser and Bull are in vicinity 
of each other. In terms of the graph, the Bull is in vicinity of a Chaser c if Bull is on a node in 
the context of c.  
- (0,0): Chaser c in vicinity is not given the next path of Bull. Bull in vicinity is not given Chaser c's 
         next path. 
- (0,1): Chaser c in vicinity is not given the next path of Bull. Bull in vicinity is given Chaser c's 
         next path. 
- (1,0): Chaser c in vicinity is given the next path of Bull. Bull in vicinity is not given Chaser c's 
         next path.
- (1,1): Chaser c in vicinity is given the next path of Bull. Bull in vicinity is given Chaser c's 
         next path.
In the last case of information mode (1,1), the algorithm determines whether the Bull or the Chaser 
makes the last pre-move (calculation for next path decision). This determination uses float 
`bull_is_2nd_premover` in [0.,1.], as a threshold variable for a PRNG decimal in [0.,1.]. The party 
that makes the last pre-move would know the other party's pre-move, and would have perfect knowledge 
of that other party's next node destination/s. 
In the case of (0,0) and (1,0), Bull pre-moves first.  
In the case of (0,1), Bull pre-moves last.  

The Bull and Chasers move in the ordering algorithmically specified. If a Bull is not in the vicinity 
of any Chaser, it sits at the same node location in 'idle' mode. If a Chaser does not detect any Bull 
in its vicinity, it is in 'search' mode. Chaser will travel the base graph `G` one edge for every 
timestamp, according to the rule of preferring nodes least frequently traveled over in its vicinity. 
See class<NodeObjectiveNavigator> for details on this traveling mechanism. In the event where Chaser 
does detect Bull in its vicinity, it will switch to 'capture' mode. It stops the traveling mechanism of 
one node per timestamp, and instead predicts a target node n_t the Bull may be on, and travels a path 
P from its location to n_t. The predicted target node n_t, in cases of information mode (1,0), is 
guaranteed to be accurate. In cases of (1,1), there is a probability, corresponding to `bull_is_2nd_premover`, 
that Bull would know the path calculated by the Chaser and avoid it. When any Chaser switches to 'capture' 
mode, the Bull would switch from 'idle' to 'flee' mode. At any timestamp in this mode, Bull chooses an 
escape node n_e that it predicts none of the Chasers in its vicinity will travel to. But sometimes, there 
are no options. If mode is (0,1), Bull would always know the locations of all Chasers in its vicinity. 

When there are multiple Chasers in the vicinity of the Bull, the Chasers that are in coordination with 
each other will prefer paths with unique destination nodes, since only one Chaser needs to be at the same 
location as the Bull to capture it. Two Chasers at one node is wasteful redundancy in this network's 
rules. 

In the case where two Chasers c0 and c1 are in vicinity of each other, as set by the `c2c_distance`, 
and Chaser c0 is in 'capture' mode and c1 is in 'search' mode, then c1 does not travel one edge distance 
as in the normal case, instead c1 chooses a path P from its location to c0's current location (before c0 
travels its next path). This is a coordination logistic that allows one Chaser, in 'capture' mode, to 
guide other Chasers, in 'search' mode, in order to route more Chasers closer to the Bull, increasing the 
odds of the Bull being captured. 

For a set of k Chasers in 'capture' mode, the programming determines each of these Chasers' predicted 
target nodes (predicted next location of Bull) by these rules: 
- The reference node is current node location of Bull, if information mode is (0,*) or if Bull is last 
  pre-mover. Otherwise, the reference node is the last node of the Bull's next path. 
- For every Chaser: 
    If reference node has not already been selected by any Chaser as a predicted target node, set Chaser 
    target node to reference node. Otherwise, set the Chaser's target node to a node that satisfies these 
    conditions: 
    - node has not yet been selected by any Chaser to be a target node. 
    - node, out of the remaining options, is closest to the reference node. There could be ties for 
      closest to reference node. 

See the algorithms for class<EnergyBasedGraphNavigator> in file<eb_graph_navigator>. The method used by 
Bull is <next__Bull> and that by Chaser is <next__chaser>. 

NOTE: 
The generation scheme to produce base graphs for this <BullNetwork> was programmed in consideration of the 
relatively long Python runtimes for bread-first search on densely connected graphs of 100 nodes or more. The 
scheme starts off by generating a tree of branching degree in range [1,4]. This tree is the minumum spanning tree 
for the base graph. Scheme then adds edges between the tree leaves and the other nodes, and edges between those 
nodes and other nodes. See class<SparseConnectedGraphGen> for more details. 
""" 
class BullNetwork: 

    def __init__(self,G,edge_cost_function,entry_points,bull,agents,visual_radius,c2c_distance,prg,\
        open_info_mode,bull_is_2nd_premover:float):   
        assert type(G) == defaultdict and edge_count(G) <= DEFAULT_BULL_NETWORK_MAX_EDGES
        assert graph_component_size(G) == 1 and is_undirected_graph(G) 
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
        assert 0. <= bull_is_2nd_premover <= 1. 

        self.G = G 
        self.edge_cost_function = edge_cost_function
        self.entry_points = entry_points 
        self.bull = bull 
        self.agents = agents 
        self.terminated_agents = {} 

        self.visual_radius = visual_radius 
        self.c2c_distance = c2c_distance 
        self.prg = prg

        # (0|1,0|1)
        # [0] chasers know Bull's next path if Bull is in sight 
        # [1] Bull knows every Chaser's next path if Chaser is in sight 
        self.oi_mode = open_info_mode
        self.bull_is_2nd_premover = bull_is_2nd_premover 

        self.spa = None 
        self.timestamp = 0 
        self.fin_stat = False 
        self.bull_cap = False 
        self.verbose = False 
        return

    def set_verbosity(self,verbose): 
        assert type(verbose) == bool 
        self.verbose = verbose 
        self.bull.verbose = verbose 
        for v in self.agents.values(): 
            v.verbose = verbose 

    def load_shortest_paths_approx(self,spa): 
        assert type(spa) == ShortestPathsApproximator
        assert spa.fin_stat 
        self.spa = spa 

    def __next__(self): 
        if self.fin_stat: return 

        if self.verbose: print("\t\tTIMESTAMP {}".format(self.timestamp)) 
        self.feed_contexts()
        self.premove() 

        # move bull 
        next(self.bull) 

        # move agents 
        akeys = sorted(self.agents.keys())
        for a in akeys: 
            next(self.agents[a]) 

        if self.verbose: print("------------------------------")
        self.check_stat() 
        self.timestamp += 1 

    def check_stat(self): 
        if self.fin_stat: 
            return 
        
        bull_loc = self.bull.location() 
        q = set([v.location() for v in self.agents.values()]) 
        if bull_loc in q: 
            self.fin_stat = True 
            self.bull_cap = True 
            return 

        keys = sorted(self.agents.keys())
        for k in keys: 
            v = self.agents[k] 
            if v.fin_stat: 
                self.terminated_agents[k] = v 
                del self.agents[k] 
        
        if len(self.agents) == 0: 
            self.fin_stat = True 
        
        if self.bull.fin_stat: 
            self.fin_stat = True 
        return 

    def premove(self):
        bull_is_2nd = prg_decimal(self.prg,[0.,1.]) <= self.bull_is_2nd_premover

        if bull_is_2nd and self.oi_mode == (1,1):  
            self.premove__chasers() 
            self.premove__Bull() 
        elif self.oi_mode == (0,1): 
            self.premove__chasers() 
            self.premove__Bull() 
        else: 
            self.premove__Bull() 
            self.premove__chasers() 
        return

    def premove__chasers(self): 
        # load up agent paths 
        if self.oi_mode[0]: 
            bp = self.bull.current_path 
        else: 
            bp = None 

        def co_op_filter(v,ci): 
            l = v.location() 
            q = [] 
            for k,other in ci.items(): 
                if k in v.other_chasers: 
                    q.append(other)
            return q 

        co_op_info = dict() 
        akeys = sorted(self.agents.keys())
        for a in akeys:
            v = self.agents[a] 
            if v.fin_stat: continue 

            ci = co_op_filter(v,co_op_info)
            bp_ = bp if v.bull_loc else None 
            p = v.agent_predicts_best_path__chaser(bp_,ci)  
            if not type(p) == type(None): 
                co_op_info[v.idn] = (p,v.mode)
            
            ####
        """
        for k,v in co_op_info.items(): 
            print("K: ",k)
            print(v[0]) 
            print(v[1])
            print()  
        """
            #### 

        return

    def premove__Bull(self):
        if self.bull.fin_stat: return 

        if self.oi_mode[1]: 
            pths = [] 
            for v in self.agents.values(): 
                if v.mode == "capture": 
                    if type(v.current_path) != type(None): 
                        pths.append(v.current_path)
        else: 
            pths = None 

        self.bull.agent_predicts_best_path__bull(pths)
        return

    def feed_contexts(self): 
        # bull premove 
        self.context_for_agent(self.bull.idn) 

        # chaser premoves 
        akeys = sorted(self.agents.keys())
        for k in akeys: 
            self.context_for_agent(k) 

        for k in akeys: 
            self.feed_agent_other_contexts(k) 

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
            chaser_locs = None if len(chaser_locs) == 0 else chaser_locs 

        agent.receive_context(G_,spaths,bull_loc,chaser_locs) 
        return

    def feed_agent_other_contexts(self,agent_idn): 
        D = self.feed_agent_other_contexts_(agent_idn) 
        A = self.agents[agent_idn]

        entire_nodeset = set() 
        for v in D.values(): 
            entire_nodeset |= v[1] 

        if type(A.bull_loc) != type(None): 
            entire_nodeset |= set(self.bull.context.keys())

        loc = self.agents[agent_idn].location() 
        q = self.spa.shortest_paths_from_node_to_nodeset(loc,entire_nodeset,True)
        for k,v in q.items(): 
            q[k] = v.adjust_weights(self.edge_cost_function) 

        A.add_other_chasers_info(D,q) 

    """
    return: 
    - idn of agent in proximity -> (agent location, nodeset of agent graph visual) 
    """
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

            if len(px.pweights) <= self.c2c_distance: 
                px = px.adjust_weights(self.edge_cost_function)
                nodeset = set(self.agents[a2].context.keys())            
                d[a2] = (loc,nodeset) 
        return d 

    def shortest_paths_of_subgraph(self,sg:defaultdict): 
        pths,_ = BDFSCache.BFS_full(sg,return_type="paths",prg=self.prg,max_search_radius=float('inf'),\
                edge_cost_function=self.edge_cost_function,verbose=False)
        return pths

    @staticmethod 
    def generate_instance(num_nodes,growth_type,num_entry_points,\
        num_agents,visual_radius,c2c_distance,prg,open_info_mode,\
        bull_is_2nd_premover,bull_energy,chaser_energy,\
        weight_range=[1,10]):

        G,spa = BullNetwork.generate_base_graph(num_nodes,prg,growth_type) 
        bn = BullNetwork.generate_instance_(G,num_entry_points,num_agents,\
            visual_radius,c2c_distance,prg,open_info_mode,bull_is_2nd_premover,\
            bull_energy,chaser_energy,weight_range)
        bn.load_shortest_paths_approx(spa) 
        return bn 

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
        sgg.form_tree() 

        spa = ShortestPathsApproximator(sgg.d,is_dfs=False,max_subgraph_radius=3,prg=prg,max_periphery=50,\
                edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)  
        spa.ref_node = 0 
        spa.exec() 

        sgg.phase_two_edges() 
        return sgg.d,spa 