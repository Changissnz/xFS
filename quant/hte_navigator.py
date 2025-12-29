from graph_models.base_node import * 

DEFAULT_HTE_VISUAL_RADIUS = 3 

class HTENavigator(NodeObjectiveNavigator): 

    def __init__(self,loc,avoid_nodeset,take_nodeset,objective_nodeset,prg,\
        path_log_length=float('inf'),absolute_avoid:bool=False,\
        visual_radius=DEFAULT_HTE_VISUAL_RADIUS): 
        
        super().__init__(loc,avoid_nodeset,take_nodeset,objective_nodeset,\
            prg,path_log_length,absolute_avoid) 

        self.visual_radius = visual_radius
        self.visual_of_graph = defaultdict(set)
        self.fin_stat = False 
        return

    def __next__(self): 
        if self.fin_stat: return 

        if self.loc in self.objective_nodeset: 
            return 

        return self.make_choice() 
    
    def receive_context(self,graph_visual:defaultdict): 
        assert self.loc in graph_visual

        super().receive_context(graph_visual)          
        self.visual_of_graph = (MicroGraph(self.visual_of_graph) + \
            MicroGraph(graph_visual)).dg

    