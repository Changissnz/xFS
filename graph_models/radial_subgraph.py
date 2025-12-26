"""
used to calculate radial subgraphs of a reference graph 
"""
from .shortest_paths import * 

# TODO: test 
"""
calculates one shortest path per connected node pair, done 
during preprocessing method. After distances of connected 
node pairs have been ascertained, able to quickly fetch 
subgraphs of radius r around any node n in `reference_graph`. 
"""
class RadialSubgraphFetcher:

    def __init__(self,reference_graph:defaultdict): 
        assert type(reference_graph) == defaultdict 
        self.reference_graph = reference_graph
        self.preproc() 

    def preproc(self): 
        self.paths_info,self.components = \
            BDFSCache.BFS_full(self.reference_graph,\
                return_type="distance",prg=self.prg)
        return

    def subgraph(self,node,radius): 
        other_nodes = [k in self.reference_graph.items() if k != n] 
        keys_of_interest = [(n,n2) for n2 in other_nodes]
        nodeset = {n} 
        for k in keys_of_interest: 
            if k not in self.paths_info: continue
            d = self.paths_info[v] 

            if d <= radius: 
                nodeset |= {k[1]} 

        qx = MicroGraph(self.reference_graph) 
        return qx.subgraph_by_nodeset_(nodeset).dg 