"""
Implementation of the NP-Complete problem, Token Swapping. 

NOTE: performance issues for graphs of larger node size ( > 2000 nodes). 
"""
from .modular_graph import * 
from .community import graph_component_size
from morebs2.numerical_generator import prg_decimal

DEFAULT_SUBMODULE_NODESIZE_ECC_EST = 3 


"""
NOTE: not guaranteed to solve token-swapping problem in permutation graph. 
"""
class PSwapGraph: 

    def __init__(self,G,P,prg,edge_cost_function): 
        assert type(G) == defaultdict 
        assert graph_component_size(G) == 1
        assert len(P) == len(G) 
        assert set(P.keys()) == set(P.values()) == set(G.keys()) 

        self.G = G 
        self.P = P 
        self.prg = prg 
        self.edge_cost_function = edge_cost_function
        self.module_eccentricities = defaultdict(float)

        self.mod_order = None 
        return 

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

        self.M = ModularGraph(self.G,20,self.prg,\
            edge_cost_function=self.edge_cost_function,\
            approx_type="mst",record_peridistance=True,\
            ensure_even_density=True)

        self.M.full_reduction() 
        self.M.shortest_paths__init()
        self.reset_sp_approx()
        self.estimate_eccentricities()
        return

    def reset_sp_approx(self): 
        self.M.set_pa_mode(True) 

    def estimate_eccentricities(self):
        assert len(self.M.base_graph_) > 1, "estimation scheme does not work!"

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

    def module_route_one_round(self): 
        self.set_swapping_order()
        print("one round")
        for m in self.mod_order:
            self.route_to_module(m) 

    def route_to_module(self,m): 
        c = self.module_mismatch(m,"count")
        stat = c == 0
        print("-- mod: {}  is solved? {}  mismatch #: {}".format(m,stat,c))

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
            self.swap_edge(q0,q1) 
        return 

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
            self.greedy_swap_on_node(nodeset[i])
            max_swaps -= 1 
        return 
    
    def greedy_swap_on_node(self,node):
        # case: solved. 
        if self.P[node] == node: return 

        neighbors = prg_seqsort(sorted(self.G[node]),self.prg) 

        n_ = None 
        best_score = float('inf')
        d0 = self.token_distance(self.P[node])
        for n in neighbors: 
            d1 = self.token_distance(self.P[n])

            self.swap_edge(node,n) 
            d0_ = self.token_distance(self.P[n])
            d1_ = self.token_distance(self.P[node]) 

            dx = (d0_ - d0) + (d1_ - d1) 

            if dx < best_score: 
                best_score = dx 
                n_ = n 

            self.swap_edge(node,n) 

        if type(n_) != type(None): 
            self.swap_edge(node,n) 
        return

    #--------------------------------------------------------------------------------------------

    # NOTE: does not check for existence of edge 
    def swap_edge(self,n0,n1): 
        self.P[n0],self.P[n1] = self.P[n1],self.P[n0]
        return 