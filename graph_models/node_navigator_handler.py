from .base_node import * 
from .radial_subgraph import * 

"""
for use with class<NodeObjectiveNavigator>,class<CyclicalNodeNavigatorTypeSM>. 

See file<base_node>, file<cyclical_navigator>. 
"""
class NavigatorGraphHandler: 

    def __init__(self,reference_graph,radius,navigator,prg): 
        assert issubclass(type(navigator),NodeObjectiveNavigator)
        self.G = reference_graph
        self.radius = radius 
        self.navigator = navigator
        self.prg = prg  

        self.qsf = QuickSubgraphFetcher(self.G,self.prg)

    def __next__(self): 
        l = self.navigator.loc 
        C = self.qsf.subgraph(l,self.radius)

        self.navigator.receive_context(C) 
        return self.navigator.make_choice()

    @staticmethod
    def iterate_n_rounds(nh,num_rounds): 
        assert type(nh) == NavigatorGraphHandler
        for _ in range(num_rounds): 
            next(nh)   