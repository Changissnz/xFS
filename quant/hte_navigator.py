from graph_models.base_node import * 
from .hte_analog_induction import * 

DEFAULT_HTE_VISUAL_RADIUS = 2 
DEFAULT_CONTRA_RISK = 0.5 

class HTENavigatorPrediction:

    def __init__(self,reference_graph,threat_nodes,prg):
        self.reference_graph = reference_graph
        self.threat_nodes = threat_nodes 
        self.prg = prg 
        self.suspected_threat_nodes = set()  
        return

    """
    NOTE: this prediction route involves reviewing all known threat nodes from 
          previous context for the current partial context, a subgraph centered 
          around navigator location `loc` with an arbitrary `radius`. 

          For usage, this method would be called every time navigator travels to 
          another node, which could be non-unique. Due to this logistic, method is 
          slow and computationally intensive. 
    """
    def possible_threats(self,context:defaultdict,loc,radius,store_results:bool=False):
        d = {t:(loc,radius) for t in self.threat_nodes}
        return self.full_possible_threats_for_next_context(context,d,store_results)
        
    """
    NOTE: this prediction route takes a `next_context`, the full graph for the next 
          <HTESurface>, and makes predictions on the threat nodes of this `next_context`. 
          This is a one-time method called after <HTEBot> updates its <HTESurface>. It 
          is quicker than the approaching of a navigator calling function<possible_threats> 
          every time it travels to a next node. 
    """
    def full_possible_threats_for_next_context(self,next_context,next_context_hyp_map,\
        store_results:bool=False): 

        hai = HTEAnalogInducer(self.reference_graph,next_context,self.threat_nodes,\
            next_context_hyp_map, isomorphic_subgraph_radius_range=\
            DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE,prg = self.prg)

        possible = set() 
        print("THREAT NODES: ",len(self.threat_nodes))
        for t in self.threat_nodes: 
            try: 
                x = hai.possible_threat_analogs(t) 
                possible |= x 
            except: 
                print("NICHT ",t)
                pass 
        print("THREAT ISOS: ",len(possible))
        if store_results: 
            print("STORING {} SUSPECTS".format(len(possible)))
            self.suspected_threat_nodes = deepcopy(possible) 
        return possible 


"""
Navigator is a subclass of <NodeObjectiveNavigator> and is specially designed 
for the graph problem of Hidden Threat Exposure (HTE). There are some deficits 
to navigator decision-making that prevent it from being a consistently intelligent 
solution for the issue of navigating networkings in Hidden Threat Exposure. One 
major issue is the navigator does not remember the paths it took, either those 
that resulted in a threat node or those that allowed it to reach its objective. 
Navigator only stores some of the individual nodes it took into memory, classifying 
those nodes as `take` (safe to travel over), `possible_avoid` (possible threat), 
and `avoid` (certain threat). To exemplify, one possible error a navigator may 
take by this contextless (no path information included) node labeling is that a 
path p0,p1,p2 may be taken as p2,p1,p0 by a successive navigator. 

This classification process is not without fault in the general case, especially 
when the navigator encounters contra (mobile) threats. When a navigator encounters 
a contra threat, navigator labels the node location of the contra threat as `avoid`. 
But the contra threat would relocate to another node location. So the next navigator 
would have the wrong node labeling and make decisions to avoid that node location, 
despite the threat relocating due to contra. This design is deficient but developed 
and used in this program because it is simple and does not invoke bigger problems 
such as more machine-learning requirements and the curse of dimensionality. This 
navigator type does not have the ability to recognize whether a threat a previous 
navigator encountered (the navigator was terminated) is contra or not, only that 
the previous navigator encountered a threat at that specific node location. 
"""
class HTENavigator(NodeObjectiveNavigator): 

    def __init__(self,loc,avoid_nodeset,take_nodeset,objective_nodeset,prg,\
        path_log_length=float('inf'),absolute_avoid:bool=False,\
        visual_radius=DEFAULT_HTE_VISUAL_RADIUS,contra_risk=DEFAULT_CONTRA_RISK,\
        fuel=float('inf'),memory_less:bool=False,uses_isomorphic_prediction:bool=False): 
        
        super().__init__(loc,avoid_nodeset,take_nodeset,objective_nodeset,\
            prg,path_log_length,absolute_avoid) 

        self.visual_radius = visual_radius
        self.contra_risk = contra_risk 
        self.fuel = fuel 
        self.memory_less = memory_less
        self.uses_isomorphic_prediction = uses_isomorphic_prediction
        self.visual_of_graph = defaultdict(set)
        self.fin_stat = False 
        self.success_stat = False 
        self.hnp = None 
        return

    def __str__(self): 

        S = "** navigator info\n"
        S += "- visual of graph: {}\n".format(len(self.visual_of_graph)) 
        S += "- avoid: {}\n".format(len(self.avoid))
        S += "- possible avoid: {}\n".format(len(self.possible_avoid))
        S += "- take: {}\n".format(len(self.take)) 
        S += "- path length: {} unique nodes: {}\n".format(len(self.path_log),len(set(self.path_log)))  
        S += "- success: {}\n".format(self.success_stat)
        return S 

    def __next__(self): 
        if self.fin_stat: return 
        if self.fuel <= 0: 
            self.fin_stat = True 
            return 

        if self.loc in self.objectives: 
            return 

        # case: contra node, update status of node as safe
        ##if self.loc in self.avoid: 
        ##    self.avoid -= {self.loc} 

        risk_possible_avoid = bool(prg_decimal(self.prg,[0.,1.]) <= self.contra_risk)
        self.set_risk_possible_avoid(risk_possible_avoid)
        l = self.make_choice() 
        self.fuel -= 1 
        return l 

    def load_previous_HTE_data(self,reference_graph,threat_nodes): 
        self.hnp = HTENavigatorPrediction(reference_graph,threat_nodes,self.prg)
        return 

    def full_navigator_prediction(self,next_context,next_context_hyp_map): 
        self.hnp.full_possible_threats_for_next_context(next_context,next_context_hyp_map,True) 
        print("--- isomorphic prediction for {} nodes".format(len(self.hnp.suspected_threat_nodes)))
        self.possible_avoid |= self.hnp.suspected_threat_nodes
    
    def load_previous_visual_of_graph(self,reference_graph): 
        assert type(reference_graph) == defaultdict 
        self.visual_of_graph = reference_graph

    def receive_context(self,graph_visual:defaultdict): 
        assert self.loc in graph_visual

        super().receive_context(graph_visual)          
        self.visual_of_graph = (MicroGraph(self.visual_of_graph) + \
            MicroGraph(graph_visual)).dg

        ##self.predict_threats() 

    # CAUTION: overcautious? 
    def predict_threats(self): 
        if type(self.hnp) == type(None): return 

        possible = self.hnp.possible_threats(self.context,self.loc,self.visual_radius)
        self.possible_avoid |= possible 
        return possible 

    def made_contact(self): 
        if not self.memory_less: 
            self.avoid |= {self.loc}
        self.mark_finish() 

    def made_objective(self): 
        self.success_stat = True 
        self.mark_finish()

    def mark_finish(self): 
        self.fin_stat = True 

    def reproduce(self,new_entry_loc,next_full_context): 

        # case: same surface 
        if type(next_full_context) == type(None): 
            avoid = self.avoid 
            take = self.take - self.avoid 
            objectives = self.objectives 
        # case: different surface 
        else: 
            avoid = set() 
            take = set() 
            objectives = next_full_context[2] 

        hten = HTENavigator(new_entry_loc,avoid,take,objectives,\
            self.prg,path_log_length=float('inf'),absolute_avoid=self.absolute_avoid,\
            visual_radius=self.visual_radius,contra_risk=self.contra_risk,\
            memory_less=self.memory_less,uses_isomorphic_prediction=self.uses_isomorphic_prediction)        

        take = set() 
        # case: same surface, load cumulative visual of graph and nodes of status `possible avoid`.
        if type(next_full_context) == type(None): 
            hten.load_previous_visual_of_graph(self.visual_of_graph)
            hten.add_possible_avoid(self.possible_avoid)
            take = self.take | set(hten.path_log) - {self.loc} \
                if not self.memory_less else set() 

        # case: same surface, if terminated by threat, add possible avoid 
        if not self.success_stat and not self.memory_less and type(next_full_context) == type(None): 
            possible_avoid = set(self.context.keys()).intersection(set(self.path_log)) - {self.loc} 
            take = self.take - set(hten.path_log)
            if len(possible_avoid) > 0: 
                possible_avoid = prg_seqsort(sorted(possible_avoid),self.prg) 
                la = ceil((1-self.contra_risk) * len(possible_avoid))
                q = set(possible_avoid[:la])
                take = take | set(possible_avoid[la:]) 
                possible_avoid = q 
            hten.add_possible_avoid(possible_avoid) 
        hten.add_take(take) 

        # case: new surface, use previous <HTESurface> data to make threat predictions if 
        #       `uses_isomorphic_prediction`
        if type(next_full_context) != type(None) and hten.uses_isomorphic_prediction: 
            assert type(next_full_context) == tuple and len(next_full_context) == 3
            assert type(next_full_context[0]) == defaultdict 
            assert type(next_full_context[1]) == dict 
            q = set(next_full_context[1].keys())
            hten.load_previous_HTE_data(self.visual_of_graph,q) 
            hten.full_navigator_prediction(next_full_context[0],next_full_context[1])            

        return hten