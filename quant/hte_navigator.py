from graph_models.base_node import * 
from .hte_analog_induction import * 

DEFAULT_HTE_VISUAL_RADIUS = 2 
DEFAULT_CONTRA_RISK = 0.5 

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
            try: 
                x = hai.possible_threat_analogs(t) 
                possible |= x 
            except: 
                print("NICHT ",t)
                print(set(self.reference_graph.keys()))
                pass 
        return possible 

class HTENavigator(NodeObjectiveNavigator): 

    def __init__(self,loc,avoid_nodeset,take_nodeset,objective_nodeset,prg,\
        path_log_length=float('inf'),absolute_avoid:bool=False,\
        visual_radius=DEFAULT_HTE_VISUAL_RADIUS,contra_risk=DEFAULT_CONTRA_RISK,\
        fuel=float('inf')): 
        
        super().__init__(loc,avoid_nodeset,take_nodeset,objective_nodeset,\
            prg,path_log_length,absolute_avoid) 

        self.visual_radius = visual_radius
        self.contra_risk = contra_risk 
        self.fuel = fuel 
        self.visual_of_graph = defaultdict(set)
        self.fin_stat = False 
        self.success_stat = False 
        self.hnp = None 
        return

    def __next__(self): 
        if self.fin_stat: return 
        if self.fuel <= 0: 
            self.fin_stat = True 
            return 

        if self.loc in self.objectives: 
            return 

        l = self.make_choice() 
        self.fuel -= 1 
        return l 

    def load_previous_HTE_data(self,reference_graph,threat_nodes): 
        self.hnp = HTENavigatorPrediction(reference_graph,threat_nodes,self.prg)
    
    def load_previous_visual_of_graph(self,reference_graph): 
        assert type(reference_graph) == defaultdict 
        self.visual_of_graph = reference_graph

    def receive_context(self,graph_visual:defaultdict): 
        assert self.loc in graph_visual

        super().receive_context(graph_visual)          
        self.visual_of_graph = (MicroGraph(self.visual_of_graph) + \
            MicroGraph(graph_visual)).dg

        self.predict_threats() 

    # CAUTION: overcautious? 
    def predict_threats(self): 
        if type(self.hnp) == type(None): return 

        possible = self.hnp.possible_threats(self.context,self.loc,self.visual_radius)
        self.possible_avoid |= possible 
        return possible 

    def made_contact(self): 
        self.avoid |= {self.loc}
        self.mark_finish() 

    def made_objective(self): 
        self.success_stat = True 
        self.mark_finish()

    def mark_finish(self): 
        self.fin_stat = True 

    def reproduce(self,new_entry_loc,iso_predict_mode): 
        if not self.fin_stat: 
            print("cannot reproduce active navigator")
            return 

        # declare new 
        hten = HTENavigator(new_entry_loc,self.avoid,self.take-self.avoid,self.objectives,\
            self.prg,path_log_length=float('inf'),absolute_avoid=self.absolute_avoid,\
            visual_radius=self.visual_radius,contra_risk=self.contra_risk)
        hten.load_previous_visual_of_graph(self.visual_of_graph)
        hten.add_possible_avoid(self.possible_avoid)

        take = set(hten.path_log) - {self.loc}
        # if terminated by threat, add possible avoid 
        if not self.success_stat: 
            possible_avoid = set(self.context.keys()).intersection(set(self.path_log)) - {self.loc} 
            take = set() 
            if len(possible_avoid) > 0: 
                possible_avoid = prg_seqsort(sorted(possible_avoid),self.prg) 
                la = ceil((1-self.contra_risk) * len(possible_avoid))
                q = set(possible_avoid[:la])
                take = set(possible_avoid[la:]) 
                possible_avoid = q 

            hten.add_possible_avoid(possible_avoid) 
        hten.add_take(take) 

        # add previous HTESurface data if `iso_predict_mode`
        if iso_predict_mode: hten.load_previous_HTE_data(self.visual_of_graph,self.avoid)
        return hten