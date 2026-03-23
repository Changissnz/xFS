from .radial_subgraph import * 
from morebs2.graph_basics import is_directed_graph,graph_childkey_fillin
from .tree_gen import SimpleCounter
from .graph_gen import replace_nodeset_with_node

"""
reduces `base_graph` into n <= `upper_nodesize_threshold` nodes. 

Procedure uses <QuickSubgraphFetcher> for modular reduction. Each new 
node of reduced graph G from `base_graph` represents an i'th degree nodeset of 
`base_graph`. If i equals 0, then nodeset is of `base_graph`. Otherwise, nodeset 
is of a node N_j > N_(j-1) > N_0 in `base_graph`. 
"""
class ModularGraph:

    def __init__(self,base_graph,upper_nodesize_threshold,prg): 
        assert type(base_graph) == defaultdict
        self.is_directed = is_directed_graph(base_graph)
        
        graph_childkey_fillin(base_graph) 
        self.base_graph = base_graph 
        self.ctr = SimpleCounter(max(self.base_graph.keys()) + 1).__next__ 

        self.mod_graphs = dict()
        self.node2nodeset = dict() 

        self.base_graph_ = deepcopy(self.base_graph)
        self.base_reduced = False 
        self.current_graph = defaultdict(set) 


        self.upper_nodesize_threshold = upper_nodesize_threshold 
        self.prg = prg 

        self.fin_stat = True 
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

        nodeseq = prg_seqsort(sorted(self.base_graph_.keys()),self.prg) 
        accounted = set() 
        while len(nodeseq) > 0 and len(self.base_graph_) > self.upper_nodesize_threshold: 
            x = nodeseq.pop(0) 
            if x in accounted: continue 
            q = self.reduce_at_node(x) 
            accounted |= q 
            #print("Q: ",q) 
        self.base_reduced = True 
        return

    def reduce_at_node(self,base_node):         
        q1 = QuickSubgraphFetcher(self.base_graph_,prg=self.prg,\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2) 
        sg = q1.subgraph(base_node,1) 
        graph_childkey_fillin(sg) 
        nodeset = set(sg.keys()) 

        new_node = self.ctr() 
        self.base_graph_ = replace_nodeset_with_node(self.base_graph_,nodeset,new_node) 
        self.node2nodeset[new_node] = nodeset 
        return nodeset

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