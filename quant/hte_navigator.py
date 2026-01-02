from graph_models.base_node import * 
from .hte_analog_induction import * 

DEFAULT_HTE_VISUAL_RADIUS = 3 

class HTENavigatorPrediction:

    def __init__(self,reference_graph,threat_nodes,prg):
        self.reference_graph = reference_graph
        self.threat_nodes = threat_nodes 
        self.prg = prg 
        return

    def possible_threats(self,context:defaultdict,loc,radius):
        d = {t:(loc,radius) for t in self.threat_nodes}

        hai = HTEAnalogInducer(self.reference_graph,context,self.threat_nodes,\
            next_graph_hyp_map=d, isomorphic_subgraph_radius_range=\
            DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE,prg = self.prg)

        possible = set() 
        for t in self.threat_nodes: 
            possible |= hai.possible_threat_analogs(t) 
        return possible 

class HTENavigator(NodeObjectiveNavigator): 

    def __init__(self,loc,avoid_nodeset,take_nodeset,objective_nodeset,prg,\
        path_log_length=float('inf'),absolute_avoid:bool=False,\
        visual_radius=DEFAULT_HTE_VISUAL_RADIUS): 
        
        super().__init__(loc,avoid_nodeset,take_nodeset,objective_nodeset,\
            prg,path_log_length,absolute_avoid) 

        self.visual_radius = visual_radius
        self.visual_of_graph = defaultdict(set)
        self.fin_stat = False 
        self.hnp = None 
        return

    def __next__(self): 
        if self.fin_stat: return 

        if self.loc in self.objective_nodeset: 
            return 

        return self.make_choice() 

    def load_previous_HTE_data(self,reference_graph,threat_nodes): 
        self.hnp = HTENavigatorPrediction(reference_graph,threat_nodes,self.prg)
    
    def receive_context(self,graph_visual:defaultdict): 
        assert self.loc in graph_visual

        super().receive_context(graph_visual)          
        self.visual_of_graph = (MicroGraph(self.visual_of_graph) + \
            MicroGraph(graph_visual)).dg

        self.predict_threats() 

    # CAUTION: overcautious? 
    def predict_threats(self): 
        if type(self.hnp) = type(None): return 

        possible = self.hnp.possible_threats(self.context,self.loc,self.visual_radius)
        self.avoid |= possible 
        return possible 