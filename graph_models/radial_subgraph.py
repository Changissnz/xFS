"""
used to calculate radial subgraphs of a reference graph 
"""
from .shortest_paths import * 
from .micrograph import * 

"""
calculates one shortest path per connected node pair, done 
during preprocessing method. After distances of connected 
node pairs have been ascertained, able to quickly fetch 
subgraphs of radius r around any node n in `reference_graph`. 
"""
class RadialSubgraphFetcher:

    def __init__(self,reference_graph:defaultdict,prg=None,return_type="distance"): 
        assert type(reference_graph) == defaultdict 

        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}
        assert return_type in {"distance","paths"} 
        self.reference_graph = reference_graph
        self.return_type = return_type
        self.prg = prg 
        self.preproc() 

    @staticmethod
    def load_preprocessed(reference_graph:defaultdict,prg,return_type,paths_info,\
        components): 

        for k,v in paths_info.items():
            assert k in reference_graph  
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
                return_type=self.return_type,prg=self.prg)
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