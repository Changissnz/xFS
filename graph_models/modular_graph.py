from .radial_subgraph import * 
from morebs2.graph_basics import is_directed_graph,graph_childkey_fillin
from .tree_gen import SimpleCounter
from .graph_gen import replace_nodeset_with_node,connected_nodes_to_other_nodeset
from .shortest_paths_approx import * 
from .shortest_paths_type_st import * 


"""
Reduces `base_graph` into n <= `upper_nodesize_threshold` nodes. 

Procedure uses <QuickSubgraphFetcher> for modular reduction. Each new 
node of reduced graph G from `base_graph` represents an i'th degree nodeset of 
`base_graph`. If i equals 0, then nodeset is of `base_graph`. Otherwise, nodeset 
is of a node N_j > N_(j-1) > ... > N_0; N_0 in `base_graph`. 

For a graph G_r of base graph G, G_r either a reduced graph of G or G itself, 
method<one_reduction> is used to reduce G_r to G_s, |G_s| < |G_r|, by this order 
of operations:
- sort nodes of G_r into sequence N_s, by metric of node density (number of base graph nodes 
    the specific node represents), 
- iterate through nodes n in N_s: 
    - if n has already been included in a reduced node during this iteration, ignore it. 
    - set reduced node r_n = n | neighbors(n).
* see method for specific details on on this second step. 
* when `allow_multireduction` is set to False, a node n_x that is a reduction of nodeset N_r in N_s 
  cannot be used in the node reduction centering on another node n_q in N_s. Setting this mode to 
  True will allow for embedded node reductions in a reduced graph G_r of G'. 
"""
# NOTE: algorithm is significantly slow for graphs of roughly 5000 or more in node size. 
class ModularGraph:

    def __init__(self,base_graph,upper_nodesize_threshold,prg,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,\
        allow_multireduction:bool=False,approx_type="std"): 

        assert type(base_graph) == defaultdict
        assert type(prg) in {MethodType,FunctionType}
        assert type(allow_multireduction) == bool 
        assert approx_type in {"std","mst"} 

        self.is_directed = is_directed_graph(base_graph)
        
        graph_childkey_fillin(base_graph) 
        self.base_graph = base_graph 
        self.ctr = SimpleCounter(max(self.base_graph.keys()) + 1).__next__ 

        self.mod_graphs = dict()
        self.node2nodeset = dict() 

        self.base_graph_ = deepcopy(self.base_graph)
        self.node_densities = {k:1 for k in self.base_graph_.keys()} 

        self.base_reduced = False 
        self.current_graph = defaultdict(set) 

        self.upper_nodesize_threshold = upper_nodesize_threshold 
        self.prg = prg 
        self.edge_cost_function = edge_cost_function
        self.allow_multireduction = allow_multireduction
        self.approx_type = approx_type
        self.fin_stat = False  
        return 

    """
    main method 
    """
    def one_reduction(self): 
        if self.fin_stat: return 

        self.base_reduced = False 
        self.one_reduction_() 
        i = len(self.mod_graphs) 
        self.mod_graphs[i] = deepcopy(self.base_graph_)

        if len(self.base_graph_) <= self.upper_nodesize_threshold:
            self.fin_stat = True 

    def one_reduction_(self): 
        if self.base_reduced: return 

        #nodeseq = prg_seqsort(sorted(self.base_graph_.keys()),self.prg)
        
        ## NOTE: scheme produces a more even distribution of reduced node densities,
        ##       in comparison with arbitrary PRNG selection. 
        nodeseq = [(k,v) for k,v in self.node_densities.items()] 
        nodeseq = prg_seqsort_ties(nodeseq,self.prg,vf=lambda x:x[1]) 
        nodeseq = [n[0] for n in nodeseq]

        accounted = set() 
        new_nodes = set() 

        while len(nodeseq) > 0 and len(self.base_graph_) > self.upper_nodesize_threshold: 
            x = nodeseq.pop(0) 
            if x in accounted: continue 
            new_node,q = self.reduce_at_node(x,new_nodes) 

            accounted |= q 
            new_nodes |= {new_node}
            ##print("Q: {} / {}  / {}".format(new_node,x,q)) 

            fx = sum([self.node_densities[i] for i in q]) 
            for i in q: del self.node_densities[i] 
            self.node_densities[new_node] = fx 
            '''
            print("x: ",x)
            print("len: ",len(nodeseq))
            print("accounted:\n{}\n".format(accounted))
            '''

        self.base_reduced = True 
        return

    def reduce_at_node(self,base_node,previous_new_nodes):         
        q1 = QuickSubgraphFetcher(self.base_graph_,prg=self.prg,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2) 
        sg = q1.subgraph(base_node,1) 
        
        if not self.allow_multireduction:
            q = MicroGraph(sg)
            q.subgraph_nodeset_exclusion(previous_new_nodes)
            sg = q.dg 

        graph_childkey_fillin(sg) 
        nodeset = set(sg.keys()) 

        new_node = self.ctr() 
        self.base_graph_ = replace_nodeset_with_node(self.base_graph_,nodeset,new_node) 
        self.node2nodeset[new_node] = nodeset 
        return new_node,nodeset

    def node_to_base_nodeset(self,n): 
        if n in self.base_graph: return {n} 

        nodeset = set() 
        queue = [n] 

        while len(queue) > 0: 
            x = queue.pop(0) 
            qx = deepcopy(self.node2nodeset[x])

            while len(qx) > 0: 
                r = qx.pop() 
                if r in self.base_graph: 
                    nodeset |= {r} 
                else: 
                    queue.append(r) 
        return nodeset

    def base_node_to_rednode(self,n): 

        node = None  
        n_ = n 

        while type(node) == type(None): 
            if n_ in self.base_graph_: 
                node = n_ 
                continue
            n_ = self.node_to_nextnode(n_) 
            assert type(n_) != type(None) 
        return node 
            
    def node_to_nextnode(self,n): 
        for k,v in self.node2nodeset.items(): 
            if n in v: 
                return k 
        return None 

    def shortest_paths__init(self): 

        self.paths_info,_ = BDFSCache.BFS_full(self.base_graph_,return_type="paths",prg=self.prg,max_search_radius=float('inf'),\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False)
        return

    def shortest_path__approx(self,u,v): 
        ured = self.base_node_to_rednode(u) 
        vred = self.base_node_to_rednode(v) 
        #print("U,V: ",ured,vred) 
        p = self.paths_info[(ured,vred)]
        return self.travel_reduced_path(p,u,v) 

    def travel_reduced_path(self,p,u,v): 
        p_ = p.p 
        ref = u 
        print("TRAVELING: ",p_) 
        P = NodePath.preload([],[])
        for i in range(len(p_) - 1): 
            # get the bridging nodes 
            p0,p1 = p_[i],p_[i+1] 
            print("\tx: ",p0,p1)

            # travel to the next node 
            h = self.travel_two_reduced_nodes(ref,p0,p1)

            # update vars 
            P.add_path(h) 
            ref = h.tail()

        print("last")
        q0 = self.node_to_base_nodeset(p_[-1])
        approx = self.sp_approx_for_subgraph(q0) 
        h = approx(ref,v) 
        P.add_path(h) 
        return P 

    def travel_two_reduced_nodes(self,base_node,p0,p1): 

        q0 = self.node_to_base_nodeset(p0)
        q1 = self.node_to_base_nodeset(p1)
        qconn,qconn1 = connected_nodes_to_other_nodeset(self.base_graph,q0,q1)

        g1 = MicroGraph(self.base_graph).subgraph_by_nodeset_(q1).dg 
        
        approx = self.sp_approx_for_subgraph(q0)

        tx = []  
        for t in qconn: 
            # 
            px = approx(base_node,t)  
        
            next_edge_distances = [] 
            for t2 in qconn1: 
                if t2 in self.base_graph[t]: 
                    c = self.edge_cost_function(t,t2) 
                    next_edge_distances.append((t2,c)) 
            next_edge_distances = prg_seqsort_ties(next_edge_distances,self.prg,vf=lambda x:x[1]) 
            n = next_edge_distances.pop(0) 
            px = px + n
 
            tx.append((t,px))  

        tx = prg_seqsort_ties(tx,self.prg,vf=lambda x:x[1].cost()) 
        return tx[0][1]

    def sp_approx_for_subgraph(self,q0): 
        g0 = MicroGraph(self.base_graph).subgraph_by_nodeset_(q0).dg 

        # case: <= 100 nodes, use <BDFSCache> 
        if len(q0) <= 100: 
            ##print("BD")
            paths_info,_ = BDFSCache.BFS_full(g0,return_type="paths",\
                prg=self.prg,max_search_radius=float('inf'),\
                edge_cost_function=self.edge_cost_function,verbose=False)

            def f(u,v): 
                return paths_info[(u,v)] 
            return f 

        # case: > 100 nodes, use approximator         
        if self.approx_type == "std": 
            spa = ShortestPathsApproximator(g0,is_dfs=False,\
                max_subgraph_radius=2,prg=self.prg,max_periphery=50,\
                edge_cost_function=self.edge_cost_function,verbose=False) 
            spa.exec() 

            def f(u,v): 
                return spa.shortest_path(\
                    u,v,by_weight=True)  
        else: 

            spa = ShortestPathsApproximatorTypeST(g0,self.edge_cost_function,\
                self.prg,verbose=False)

            def f(u,v): 
                return spa.shortest_path__approx(u,v) 

        return f