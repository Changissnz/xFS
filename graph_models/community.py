from .radial_subgraph import * 

# TODO: test this. 
"""
an algorithm to calculate arbitrary communities, based on 
eccentricity measures that are, in turn, calculated from 
shortest paths. Differs from the Louvain/Leiden algorithms.  
"""
class RadialGraphCommunities: 

    def __init__(self,d:defaultdict,prg,max_radius): 
        if type(max_radius) == float: 
            assert 0 < max_radius <= 1. 
        else: 
            assert type(max_radius) == int 
            assert max_radius > 0 
        assert len(d) > 0 

        self.rsf = RadialSubgraphFetcher(d,prg,return_type="paths")
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
            qx = self.node_ordering[0][1].cost() 
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

        nodeset = set(self.rsf.subgraph(ref_node,self.radius).keys())

        accounted_nodes = set(flatten_setseq(self.community_nodesets))
        nodeset = nodeset - accounted_nodes

        while i < len(self.node_ordering): 
            n = self.node_ordering[i][0]
            if n in nodeset: 
                self.node_ordering.pop(i) 
                continue 
            i += 1 
        self.community_nodesets.append(nodeset) 
        return nodeset