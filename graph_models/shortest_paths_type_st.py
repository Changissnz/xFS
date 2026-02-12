from .spanning_tree import * 
from .path_induction import * 
from morebs2.graph_basics import * 

"""
Another approximation scheme, besides from the original @ file<graph_models.shortest_paths_approx>. 
"""
# NOTE: despite the "hacking" of the base graph into minumum spanning trees, search times for 
#       shortest paths are not a drastic improvement from <ShortestPathsApproximator>. 
# NOTE: more testing needed. 
class ShortestPathsApproximatorTypeST: 

    def __init__(self,G,edge_cost_function,prg,verbose=False): 
        assert type(G) == defaultdict
        assert type(prg) in {FunctionType,MethodType}
        self.G =  G 
        self.edge_cost_function = edge_cost_function
        self.prg = prg 
        self.verbose = verbose

        self.fin_stat = False 
        self.previous_heads = set() 
        self.nodepair_path_info = dict() 
        self.preproc() 
        return  

    def preproc(self): 
        gd = GraphComponentDecomposition(self.G) 
        gd.decompose() 
        self.components = [sorted(c) for c in gd.components]
        return 

    def __next__(self): 
        if self.fin_stat: return len(self.nodepair_path_info) 

        h = self.next_head()
        if type(h) == type(None): return len(self.nodepair_path_info) 

        if self.verbose: 
            print("conducting shortest paths from {}".format(h))
        spaths1,spaths2 = self.shortest_paths_from_head(h) 

        if self.verbose: 
            print("got {} paths for source, {} deductions".format(len(spaths1),len(spaths2))) 

        self.nodepair_path_info = update_shortest_paths_map(self.nodepair_path_info,spaths1)
        self.nodepair_path_info = update_shortest_paths_map(self.nodepair_path_info,spaths2)
        return len(self.nodepair_path_info) 

    def next_head(self): 
        if self.fin_stat: 
            return 

        if len(self.components) == 0: 
            self.fin_stat = True 

        # choose a component 
        q = int(self.prg()) % len(self.components) 
        c = self.components[q] 
        d = int(self.prg()) % len(c) 
        h = c.pop() 

        if len(c) == 0: 
            self.components.pop(q) 
        
        if h in self.previous_heads: 
            return self.next_head() 

        self.previous_heads |= {h} 
        return h 

    def shortest_paths_from_head(self,head):

        st = SpanningTree(self.G,\
            edge_cost_function=self.edge_cost_function,prg=None) 

        st.init_head(head) 
        st.make() 
        G_ = st.tree() 
        if self.verbose: 
            print("-- searching...")
        bc = BDFSCache(head,G_,is_bfs=True,prg=self.prg,\
            edge_cost_function=lambda u,v:1,num_paths_per_node=1,\
            max_search_radius=float('inf'),verbose=False)
        bc.exec()

        P = bc.min_paths 
        P_ = dict() 
        for k,v in P.items(): 
            P_[(head,k)] = v[0] 
        
        if self.verbose: 
            print("-- deducing")
            
        PI = PathInduction(head,P,self.prg,num_segment_range=[3,7])
     
        return P_,PI.induce_paths_from_other_references(self.G)   