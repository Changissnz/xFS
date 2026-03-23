"""
used to calculate radial subgraphs of a reference graph 
"""
from .shortest_paths import * 
from .micrograph import * 

class SubgraphFetcher: 

    def __init__(self,reference_graph:defaultdict,prg=None,return_type="distance",edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2): 
        assert type(reference_graph) == defaultdict 

        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}
        assert return_type in {"distance","paths"} 
        self.reference_graph = reference_graph
        self.return_type = return_type
        self.edge_cost_function = edge_cost_function
        self.prg = prg 
        return 

"""
calculates one shortest path per connected node pair, done 
during preprocessing method. After distances of connected 
node pairs have been ascertained, able to quickly fetch 
subgraphs of radius r around any node n in `reference_graph`. 
"""
class RadialSubgraphFetcher(SubgraphFetcher):

    def __init__(self,reference_graph:defaultdict,prg=None,return_type="distance",edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2): 
        super().__init__(reference_graph,prg,return_type,DEFAULT_EDGE_COST_FUNCTION_2) 
        self.preproc() 

    @staticmethod
    def load_preprocessed(reference_graph:defaultdict,prg,return_type,paths_info,\
        components): 

        for k,v in paths_info.items():
            assert k[0] in reference_graph and k[1] in reference_graph
            if return_type == "distance":
                assert is_number(v)
                continue 
            assert type(v) == NodePath
        assert type(components) in {type(None),list} 

        rsf = RadialSubgraphFetcher(defaultdict(set),prg,return_type) 
        rsf.reference_graph = reference_graph
        rsf.paths_info = paths_info  
        rsf.components = components 
        return rsf 

    def preproc(self): 
        self.paths_info,self.components = \
            BDFSCache.BFS_full(self.reference_graph,\
                return_type=self.return_type,prg=self.prg,\
                edge_cost_function=self.edge_cost_function)
        return

    def subgraph(self,node,radius): 
        keys_of_interest = [(node,n2) for n2 in self.reference_graph.keys()]
        nodeset = set() 
        for k in keys_of_interest: 
            assert type(k) == tuple 
            stat = k in self.paths_info
            if not stat: continue
            d = self.paths_info[k] 

            if type(d) == NodePath: d = d.cost() 

            if d <= radius: 
                nodeset |= {k[1]} 

        qx = MicroGraph(self.reference_graph) 
        return qx.subgraph_by_nodeset_(nodeset).dg 

"""
quicker version, designed only for undirected graphs. Also faster 
than <BDFSCache>.  
"""
class QuickSubgraphFetcher(SubgraphFetcher):

    def __init__(self,reference_graph:defaultdict,prg=None,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2): 
        ##assert is_undirected_graph(reference_graph)
        super().__init__(reference_graph,prg,"distance",edge_cost_function) 

    def subgraph(self,node,radius):
        nodeset = set([node]) 
        queue = [(node,0)] 
        covered_edges = set() 
        ref = None
        while len(queue) > 0: 
            #print("QUEUE ",len(queue)) 
            ref,d = queue.pop(0) 
            neighbors = self.reference_graph[ref] 
            for n in neighbors: 
                q = tuple(sorted([ref,n])) 
                if q in covered_edges: continue 
                covered_edges |= {q} 
                d2 = d + self.edge_cost_function(ref,n)
                if d2 > radius: 
                    continue 
                nodeset |= {n}
                queue.append((n,d2))
        qx = MicroGraph(self.reference_graph) 
        return qx.subgraph_by_nodeset_(nodeset).dg 