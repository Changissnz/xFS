from .radial_subgraph import * 
from morebs2.graph_basics import *
from math import ceil 

def graph_component_size(G:defaultdict): 
    gx = GraphComponentDecomposition(G) 
    gx.decompose() 
    return len(gx.components)

def subgraph_component_size(G:defaultdict,subgraph_nodeset:set): 
    mg = MicroGraph(G).subgraph_by_nodeset_(subgraph_nodeset)
    return graph_component_size(mg.dg)

# TODO: test this. 
"""
an algorithm to calculate arbitrary communities, based on 
eccentricity measures that are, in turn, calculated from 
shortest paths. Differs from the Louvain/Leiden algorithms.  

Algorithm first calculates shortest paths between every 
node pair, by a classic breadth-first search approach. 
Algorithm then proceeds to grouping nodes, in the ordering 
of greatest to least node eccentricity. Not suitable for 
larger graphs (> 500 nodes).

d := defaultdict, graph 
prg := PRNG
max_radius := float, 0 < f <= 1
rsf := None|RadialSubgraphFetcher
"""
class RadialGraphCommunities: 

    def __init__(self,d:defaultdict,prg,max_radius,rsf=None): 
        if type(max_radius) == float: 
            assert 0 < max_radius <= 1. 
        else: 
            assert type(max_radius) == int 
            assert max_radius > 0 
        assert len(d) > 0 

        if type(rsf) == type(None): 
            self.rsf = RadialSubgraphFetcher(d,prg,return_type="paths")
        else: 
            assert type(rsf) == RadialSubgraphFetcher
            assert rsf.reference_graph == d 
            assert rsf.return_type == "paths"
            self.rsf = rsf 

        self.prg = prg 
        self.max_radius = max_radius 
        self.order_nodes()
        self.community_nodesets = []
        self.fin_stat = False 
        return

    def order_nodes(self): 
        self.node_ordering = node_eccentricity_ranking(self.rsf.paths_info,\
            self.prg,return_type="all")[::-1]
        
        if type(self.max_radius) == float: 
            qx = self.node_ordering[0][1]
            self.max_radius = ceil(self.max_radius * qx)
        return 

    """
    main method 
    """
    def exec(self): 
        while not self.fin_stat: 
            self.one_new_community() 

    """
    `community` -> nodeset s.t. for any two nodes n1,n2, n1 is connected to n2. 
    """
    def one_new_community(self): 
        if self.fin_stat: return 

        if len(self.node_ordering) == 0: 
            self.fin_stat = True 
            return 

        ref_node = self.node_ordering.pop(0)[0] 

        nodeset = set(self.rsf.subgraph(ref_node,self.max_radius).keys())

        accounted_nodes = set(flatten_setseq(self.community_nodesets))
        nodeset = nodeset - accounted_nodes

        i = 0 
        while i < len(self.node_ordering): 
            n = self.node_ordering[i][0]
            if n in nodeset: 
                self.node_ordering.pop(i) 
                continue 
            i += 1 
        self.community_nodesets.append(nodeset) 
        return nodeset

    def subgraph(self,node,radius): 
        return self.rsf.subgraph(node,radius) 


"""
variant of the original Louvain method for graph community detection. 

In this variant, bigger communities grow stronger in scoring during search process. 
This trait prones the algorithm to produce communities of a disproportionate scale 
to one another. 
"""
class ReinforcementCommunityFinder: 

    def __init__(self,G,prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,\
        max_reassignment:bool=True,force_reassignment:bool=False,verbose:bool=False):  

        assert type(G) == defaultdict 
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}
        assert type(edge_cost_function) in {MethodType,FunctionType}
        assert type(max_reassignment) == bool 
        assert type(force_reassignment) == bool 

        assert type(verbose) == bool 


        self.G = G 
        self.prg = prg 
        self.edge_cost_function = edge_cost_function
        self.max_reassignment = max_reassignment
        self.force_reassignment = force_reassignment
        self.verbose = verbose 
        self.communities = [] 
        self.node_ordering = None 
        self.fin_stat = False 
        self.preproc() 
        return


    """
    main method #2 

    method that uses <ReinforcementCommunityFinder> to find n communities out 
    of graph G, |G| >= n. 

    NOTE: if `fast_part` set to False, then not guaranteed to produce the wanted 
          number n of communities. 
    """
    @staticmethod 
    def partition_into_n_communities(G,n,prg,edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,\
        max_reassignment=False,fast_part:bool=False,verbose=False): 

        assert n <= len(G) 
        #gd = GraphComponentDecomposition(G) 
        #gd.decompose() 
        #assert n >= len(gd.components) 

        rcf = ReinforcementCommunityFinder(G,prg,edge_cost_function,max_reassignment,\
            force_reassignment=False,verbose=verbose) 

        while len(rcf.communities) > n and not rcf.fin_stat: 
            next(rcf) 

        if len(rcf.communities) == n: 
            return rcf.communities

        if not fast_part: 
            ReinforcementCommunityFinder.community_reduction(rcf,n)
            return rcf.communities 
            
        return ReinforcementCommunityFinder.prng_merge_communities(G,\
            rcf.communities,n,prg) 

    # NOTE: guaranteed to reduce number of communities to `n`, given valid 
    #       parameter values. 
    @staticmethod 
    def prng_merge_communities(G,communities,n,prg):
        def prg_(): return int(prg())

        if len(communities) <= n: return communities 

        communities = prg_seqsort_ties(communities,prg_,vf=lambda x: len(x)) 
        cache = [] 

        i0 = 0 
        while len(communities) > n and i0 < len(communities):  
            comm = communities.pop(i0)  
        
            neighbors = [G[c] for c in comm] 
            neighbors = flatten_setseq(neighbors) 
            stat = False 
            for (i,c) in enumerate(communities): 
                inter = c.intersection(neighbors)
                if len(inter) > 0:
                    stat = True  
                    c |= comm 
                    
                    j = i+1 
                    if j >= len(communities): break 

                    while len(c) > len(communities[j]): 
                        j += 1 
                        if j >= len(communities): break 
                    
                    if j != i + 1:
                        communities.insert(j,c) 
                        communities.pop(i)         
                    break 
            
            if not stat:
                communities.insert(i0,comm) 
                i0 += 1 
         
        return communities

    # NOTE: deficient, not guaranteed to reduce number of communities to n. 
    @staticmethod 
    def community_reduction(rcf,n): 
        if len(rcf.communities) <= n: return 
        
        if rcf.cumulative_edge_sum == 0: return 

        nodes = rcf.G.keys() 
        node_comm_degree = []  
        for n2 in nodes: 
            i,_ = rcf.node_community_info(n2)
            c = len(rcf.communities[i])
            node_comm_degree.append((n2,c))

        no = prg_seqsort_ties(node_comm_degree,rcf.prg,vf=lambda x:x[1])
        rcf.fin_stat = False 
        rcf.node_ordering = [n2[0] for n2 in no]
        rcf.force_reassignment = True 

        while len(rcf.communities) > n and not rcf.fin_stat: 
            next(rcf) 
         
    def preproc(self): 
        def prg_(): return int(self.prg())
        self.node_ordering = prg_seqsort(sorted(self.G.keys()),prg_) 
        self.communities.clear() 

        for n in self.node_ordering:
            self.communities.append(set([n]))

        # edge weight sums (undirected graph) 
        c = 0 
        for k,v in self.G.items(): 
            c2 = sum([self.edge_cost_function(k,v_) for v_ in v]) 
            c += c2 
        self.cumulative_edge_sum = c / 2  
        self.fin_stat = self.cumulative_edge_sum == 0 
        return 

    """
    main method #1 
    """
    def exec(self): 
        while not self.fin_stat: 
            next(self) 
        return 

    def __next__(self): 
        if self.fin_stat: 
            return 

        if not len(self.node_ordering): 
            self.fin_stat = True 
            return 

        n = self.node_ordering.pop(0) 
        
        if self.verbose: print("assign comm for ",n)
        self.try_moving_node(n) 
        if self.verbose: print("-" * 25)

    def try_moving_node(self,n):   
        current_community,other_communities = self.node_community_info(n) 
        assert type(current_community) != type(None) 

        better_comm = None 
        if self.force_reassignment: 
            better_comm = self.force_moving_node__comm_rankings(\
                n,current_community,other_communities)
        else: 
            better_comm = self.optional_moving_node__comm_rankings(\
                n,current_community,other_communities)
        
        # case: no better communities, terminate. 
        if len(better_comm) == 0: 
            if self.verbose: print("- no comm reassignment") 
            return 

        # case: choose highest scoring community 
        better_comm = sorted(better_comm,key=lambda x: x[1]) 

        if self.max_reassignment: 
            better_comm_index = better_comm[-1][0] 
        else: 
            i = int(self.prg()) % len(better_comm) 
            better_comm_index = better_comm[i][0] 
        
        self.reassign(n,current_community,better_comm_index)
        return

    def force_moving_node__comm_rankings(self,n,current_community,other_communities): 
        node_comm = self.communities[current_community] 
        node_comm1 = node_comm - {n} 
        comm_score1 = self.community_score(node_comm1)  

        better_comm = [] 
        best_score = 0 
        for i in other_communities: 
            other_comm = self.communities[i] 
            other_comm1 = other_comm | {n} 
            other_score1 = self.community_score(other_comm1) 
            S2 = comm_score1 + other_score1 

            if S2 > best_score:  
                better_comm.append((i,S2)) 
                best_score = S2 

        if self.verbose: print("-- comm size: {}, better={}".format(len(node_comm),len(better_comm)))
        return better_comm

    def optional_moving_node__comm_rankings(self,n,current_community,other_communities): 

        node_comm = self.communities[current_community] 
        comm_score = self.community_score(node_comm) 

        node_comm1 = node_comm - {n} 
        comm_score1 = self.community_score(node_comm1)  

        better_comm = [] 
        for i in other_communities: 
            other_comm = self.communities[i] 
            other_score0 = self.community_score(other_comm)

            other_comm1 = other_comm | {n} 
            other_score1 = self.community_score(other_comm1) 

            S1 = comm_score + other_score0 
            S2 = comm_score1 + other_score1

            if S2 > S1: 
                better_comm.append((i,S2)) 
        return better_comm 


    def node_community_info(self,n): 
        neighbors = self.G[n] 

        current_community = None 
        other_communities = [] 

        for (i,c) in enumerate(self.communities): 
            if n in c: 
                current_community = i 
                continue 
            
            if len(c.intersection(neighbors)) > 0: 
                other_communities.append(i) 
        return current_community,other_communities

    def community_score(self,nodeset): 
        S = 0 
        for n in nodeset: 
            for n2 in nodeset: 
                s = self.edge_cost_function(n,n2) 
                S += s 
        return S / self.cumulative_edge_sum 

    def reassign(self,n,current_comm_index,better_comm_index):   
        current_comm = self.communities[current_comm_index] 
        better_comm = self.communities[better_comm_index] 

        assert n in current_comm 

        if self.verbose: 
            print("- reassigning {} from\n{}\nto\n{}".format(n,current_comm,better_comm)) 

        #if self.force_reassignment: 
        #    better_comm |= current_comm
        #    current_comm.clear()
        #else: 
        current_comm -= {n} 
        better_comm |= {n} 
        if len(current_comm) == 0: 
            self.communities.pop(current_comm_index) 
        return