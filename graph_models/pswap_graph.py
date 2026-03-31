"""
Implementation of the NP-Complete problem, Token Swapping. 

NOTE: performance issues for graphs of larger node size ( > 2000 nodes). 
"""
from .modular_graph import * 
from .community import graph_component_size
from morebs2.numerical_generator import prg_decimal

DEFAULT_PSWAP_NUM_MODULES_RANGE = [15,25] 
DEFAULT_SUBMODULE_NODESIZE_ECC_EST = 3 

DEFAULT_PSWAP_NUM_TIMESTAMPS_DEFAULT_TOKEN_ROUTE = 5 
DEFAULT_PSWAP_NUM_TIMESTAMPS__NO_IMPROVEMENT_UPDATE = 3 
DEFAULT_PSWAP_NUM_GREEDYROUTE_ITERATIONS_POSTUPDATE = 2 

"""
NOTE: not guaranteed to solve token swapping problem in permutation graph. 

This is an implementation of a solution search to the NP-Complete problem, 
Token Swapping. The proposed solution search is described in this paper @ 

https://github.com/Changissnz/deline_crypto/blob/master/dc_paper.pdf
(~ pg. 29). 
---------------------------------------------------------------------------
"""
class PSwapGraph: 

    def __init__(self,G,P,prg,edge_cost_function,record_swaps:bool=False,verbose:bool=False): 
        assert type(G) == defaultdict 
        assert len
        assert graph_component_size(G) == 1
        assert len(P) == len(G) 
        assert set(P.keys()) == set(P.values()) == set(G.keys()) 
        assert type(edge_cost_function) in {FunctionType,MethodType}
        assert type(record_swaps) == bool == type(verbose)

        self.G = G 
        self.P = P 
        self.prg = prg 
        self.edge_cost_function = edge_cost_function
        self.record_swaps = record_swaps
        self.verbose = verbose 
        self.swap_seq = deque() 
        self.module_eccentricities = defaultdict(float)

        self.mod_order = None 

        # for swaps conducted. 
        self.c = 0 
        return 

    def __len__(self): 
        return len(self.G) 

    #---------------------------------- preprocessing methods 

    """
    pre-main method 
    """
    def preswap_analysis(self): 
        '''
        self.M = ModularGraph.default_instance(self.G,self.prg,\
            edge_cost_function=self.edge_cost_function,\
            approx_type="std",record_peridistance=True,\
            ensure_even_density=True) 
        '''

        l = len(self.G)
        x = modulo_in_range(int(self.prg()),DEFAULT_PSWAP_NUM_MODULES_RANGE) 

        if x > l: 
            d = prg_decimal(self.prg,[0.35,65]) 
            x = ceil(l * d)


        self.M = ModularGraph(self.G,x,self.prg,\
            edge_cost_function=self.edge_cost_function,\
            approx_type="mst",record_peridistance=True,\
            ensure_even_density=True)

        self.M.full_reduction() 
        self.M.shortest_paths__init()
        self.reset_sp_approx(use_bdfs=False)
        self.estimate_eccentricities()
        return

    """
    auxiliary method used to reset shortest paths approximation for 
    the current <ModularGraph> instance `M`.
    """
    def reset_sp_approx(self,use_bdfs): 
        self.M.set_pa_mode(True,use_bdfs) 

    #------------------------------ eccentricity approximation; used in preprocessing. 

    """
    estimates eccentricities of modules. These measures are used to 
    determine ordering of token-routing. 
    """
    def estimate_eccentricities(self):
        assert len(self.M.base_graph_) > 1, "estimation scheme does not work!"
        self.module_eccentricities.clear()

        keys = prg_seqsort(sorted(self.M.base_graph_.keys()),self.prg) 
        for k in keys: 
            self.estimate_mod_ecc(k)
        return 

    def estimate_mod_ecc(self,m):
        x = self.M.farthest_modules(m)

        for x_ in x: 
            q = self.ecc_approx__module2module(m,x_)

            self.module_eccentricities[x_] = \
                max([self.module_eccentricities[x_],q]) 
            self.module_eccentricities[m] = \
                max([self.module_eccentricities[m],q]) 
        return 

    def ecc_approx__module2module(self,m0,m): 
        nodeset = self.choose_submod_nodeseq(m0) 
        q = self.choose_submod_nodeseq(m)

        dx = [] 
        for n in nodeset: 
            for q_ in q: 
                d = self.M.shortest_path__approx(n,q_)
                dx.append(d.cost()) 
        return max(dx)  

    """
    chooses q <= DEFAULT_SUBMODULE_NODESIZE_ECC_EST nodes of 
    nodeset for reduced node `n`. 

    Oscillates between choosing the most and least eccentric 
    nodes in the node queue. 
    """
    def choose_submod_nodeseq(self,n): 
        q = self.M.node_to_base_nodeset(n)
        x = [(q_,self.M.peridistance[q_]) for q_ in q] 
        x = prg_seqsort_ties(x,self.prg,vf=lambda y:y[1]) 

        if prg_decimal(self.prg,[0.,1.]) > 0.5: 
            x = x[::-1] 

        x_ = [] 
        i = -1  
        while len(x) > 0 and len(x_) < DEFAULT_SUBMODULE_NODESIZE_ECC_EST: 
            x_.append(x.pop(i)[0])  
            i = (i - 1) % -2  
        return x_ 

    #-------------------------------- for token information 

    # NOTE: approximate token distance; could vary by approximation scheme's shortest paths. 
    """
    return: 
    - cumulative unsolved token distance to solve-nodes, # of solved tokens. 
    """
    def cumulative_token_distance(self): 
        q = sorted(self.P.keys()) 
        s = 0 
        solved = 0 
        for q_ in q: 
            d = self.token_distance(q_)
            if d == 0: 
                solved += 1 
            s += d 
        return s,solved 

    def token_distance(self,node): 
        q = self.token_path(node)
        if type(q) == type(None): 
            return 0 
        return q.cost() 

    def token_path(self,node): 
        t = self.token_location(node)
        if t == node: return None  
        return self.M.shortest_path__approx(t,node) 

    def token_location(self,token): 
        for k,v in self.P.items(): 
            if v == token: return k 
        assert False 

    #---------------------------------- token-swapping by routing (via path per token to solve-node) 

    def set_swapping_order(self): 
        V = [(k,v) for k,v in self.module_eccentricities.items()]
        V = prg_seqsort_ties(V,self.prg,vf=lambda x:x[1])[::-1]
        self.mod_order = [v[0] for v in V]
        return

    """
    main method #1 
    """
    def module_route_one_round(self): 
        self.set_swapping_order()
        if self.verbose: print("one round")
        for m in self.mod_order:
            self.route_to_module(m) 

    def route_to_module(self,m): 
        c = self.module_mismatch(m,"count")
        stat = c == 0
        if self.verbose: print("-- mod: {}  is solved? {}  mismatch #: {}".format(m,stat,c))

        if stat:
            return 

        self.M.order_module_nodes_by_ecc(m)
        nodes = self.M.module2ecc_map[m]

        for n in nodes: 
            p = self.token_path(n)
            if type(p) == type(None): continue 
            self.conduct_route(p)
        return

    def conduct_route(self,p): 
        l = len(p)
        for i in range(l -1): 
            q0,q1 = p[i],p[i+1] 
            self.swap_edge(q0,q1,log_swap=True) 
        return 

    """
    return: 
    - # of mismatched nodes of module `m` OR 
      subset of mismatched nodes of `m`. 
    """
    def module_mismatch(self,m,return_type="count"):
        assert return_type in {"count","subset"}

        c = 0 if return_type == "count" else set()
        b = self.M.node_to_base_nodeset(m)
        for b_ in b: 
            if return_type == "count": 
                c += int(self.P[b_] != b_)
            else: 
                c |= {b_}
        return c 

    #----------------------------------------- token-swapping by greedy swap (negative change in distance of swapped token pair)

    """
    main method #2
    """
    def module_greedy_swap_one_round(self): 
        self.set_swapping_order()
        print("one round")
        for m in self.mod_order:
            self.greedy_swaps_on_module(m) 

    def greedy_swaps_on_module(self,m): 
        c = self.module_mismatch(m,"count")
        if c == 0: return 

        b = self.M.node_to_base_nodeset(m)
        self.greedy_swaps_on_nodeset(b) 

    def greedy_swaps_on_nodeset(self,nodeset,max_swaps=50):
        nodeset = sorted(nodeset)

        while max_swaps > 0: 
            i = int(self.prg()) % len(nodeset) 

            ## approach 1: arbitrary swap 
            #self.greedy_swap_on_node(nodeset[i])

            ## approach 2: greedy swap route. 
            q0 = min([max_swaps,10])
            q = self.greedy_route_on_node(nodeset[i],q0)
            max_swaps -= q 

            if q != q0: break 
        return 

    def greedy_route_on_node(self,node,num_swaps=10): 
        stat = True 

        x = num_swaps 
        while stat and num_swaps > 0: 
            stat,node = self.greedy_swap_on_node(node) 
            num_swaps -= 1 
        return x - num_swaps 
    
    def greedy_swap_on_node(self,node):
        # case: solved. 
        if self.P[node] == node: return False,None 

        neighbors = prg_seqsort(sorted(self.G[node]),self.prg) 

        n_ = None 
        best_score = float('inf') 
        d0 = self.token_distance(self.P[node])
        for n in neighbors: 
            d1 = self.token_distance(self.P[n])

            self.swap_edge(node,n,log_swap=False) 
            d0_ = self.token_distance(self.P[n])
            d1_ = self.token_distance(self.P[node]) 

            dx = (d0_ - d0) + (d1_ - d1) 

            if dx < best_score: 
                best_score = dx 
                n_ = n 

            self.swap_edge(node,n,log_swap=False) 

        if type(n_) != type(None) and best_score <= 0: 
            self.swap_edge(node,n_,log_swap=True) 
            return True,n_
        return False,None 

    #--------------------------------------------------------------------------------------------

    # NOTE: does not check for existence of edge 
    def swap_edge(self,n0,n1,log_swap:bool=False): 
        self.P[n0],self.P[n1] = self.P[n1],self.P[n0]

        if log_swap: 
            self.c += 1 

            if self.record_swaps: 
                self.swap_seq.append((n0,n1)) 
        return 

    @staticmethod
    def generate_token_placement(num_nodes,prg): 
        assert type(num_nodes) == int and num_nodes >= 1 

        p = [i for i in range(num_nodes)] 
        p0 = prg_seqsort(deepcopy(p),prg) 
        P = {p_:p0_ for (p_,p0_) in zip(p,p0)}
        return P 

"""
Handles the token-swapping operations for a <PSwapGraph> instance. 

NOTE: Not guaranteed to solve token swapping problem in permutation graph. 
      Obtaining swapping solution depends on PRNG. 

The method<auto_solution_search> is the approach <PSGraphHandler> 
takes.

By default, approach calls method<PSwapGraph.module_greedy_swap_one_round> 
for `num_timestamps_default_move`. If there is no improvement in number of solved 
tokens for `no_improvement_update` iterations of method<auto_solution_search>, 
method<update_PSwapGraph_paths> is called. When method<update_PSwapGraph_paths> 
is called, a new modularization is calculated, along with new shortest paths, and 
method<PSwapGraph.module_greedy_swap_one_round> is called for `greedy_route_iterations` 
iterations.

Method<auto_solution_search> is called repeatedly until <PSwapGraph> is solved, or 
solution cannot be obtained via the PRNG <pg.prg>. 
"""
class PSGraphHandler: 

    def __init__(self,pg:PSwapGraph,\
        num_timestamps_default_move:int=DEFAULT_PSWAP_NUM_TIMESTAMPS_DEFAULT_TOKEN_ROUTE,\
        no_improvement_update:int=DEFAULT_PSWAP_NUM_TIMESTAMPS__NO_IMPROVEMENT_UPDATE,\
        greedy_route_iterations:int=DEFAULT_PSWAP_NUM_GREEDYROUTE_ITERATIONS_POSTUPDATE): 
        assert type(pg) == PSwapGraph
        assert num_timestamps_default_move > 0 
        assert 6 >= no_improvement_update > 0 
        assert 6 >= greedy_route_iterations > 0 

        self.pg = pg 
        self.num_timestamps_default_move = num_timestamps_default_move
        self.no_improvement_update = no_improvement_update
        self.greedy_route_iterations = greedy_route_iterations

        self.pg.preswap_analysis()
        self.highest_token_score = 0
        self.num_no_improvement = 0 

        self.fin_stat = False 
        return 

    """
    main method #2 
    """
    def full_auto_search(self): 
        while not self.fin_stat: 
            self.auto_solution_search() 

    """
    main method #1 
    """
    def auto_solution_search(self): 
        if self.fin_stat: 
            return 

        if self.highest_token_score == len(self.pg): 
            self.fin_stat = True 
            return 

        self.update_PSwapGraph_paths() 
        self.default_move() 

        return


    def default_move(self): 
        highest_score = self.highest_token_score

        for _ in range(self.num_timestamps_default_move): 
            self.pg.module_route_one_round()
            t = self.pg.cumulative_token_distance()[1]
            self.highest_token_score = max([\
                self.highest_token_score,t]) 
            if t == len(self.pg): 
                break 

        if self.highest_token_score > highest_score:
            self.num_no_improvement = 0
        else: 
            self.num_no_improvement += 1 
        return

    def update_PSwapGraph_paths(self): 
        
        if self.num_no_improvement < self.no_improvement_update: 
            return 

        self.pg.preswap_analysis() 
        self.num_no_improvement = 0 

        for _ in range(self.greedy_route_iterations): 
            self.pg.module_greedy_swap_one_round() 
        return