from .node_path import * 

class HyperGraph:

    def __init__(self,nodeset,nodepaths):
        assert type(nodeset) == set 
        for x in nodepaths: 
            assert type(x) == NodePath 
            assert set(x.p).issubset(nodeset) 

        self.nodes = nodeset 
        self.edges = nodepaths 