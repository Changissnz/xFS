"""
Hidden Threat Exposure walkthroughs  
"""
from quant.hte_aux import * 
from quant.hte_navigator import* 

DEFAULT_NAVIGATOR_NODE_FUEL_MULTIPLIER = 1.0 

"""
Hidden Threat Exposure automaton is related to the 1990's video 
game, Minesweeper. See this wikipedia article, 
https://en.wikipedia.org/wiki/Minesweeper_(video_game), 
for more details. 

Hidden Threat Exposure explores the issues of hidden 
threats (mines) from a connectionist perspective (traversing through 
a network), in addition to the problem of selecting nodes that are not 
threats for travel over. The use of cycling variants, as part of 
trial-and-error discovery, in Hidden Threat Exposure traversal decisions
are a kind of machine-learning technique. 
"""
class HTEBot:

    def __init__(self,hte_surface,hte_navigator,verbose=False):  
        assert type(hte_surface) == HTESurface
        assert type(hte_navigator) in {type(None),HTENavigator} 

        self.hte_surf = hte_surface
        self.hte_nav = hte_navigator
        self.verbose = verbose 
        self.terminated_navigators = [] 

        self.preproc() 
        self.hte_nav.fuel = DEFAULT_NAVIGATOR_NODE_FUEL_MULTIPLIER * len(self.hte_surf.base_graph)
        return 

    #-------------------------------------------------------------------------------------------- 

    def preproc(self): 
        if type(self.hte_nav) == type(None): 
            epoint = self.choose_entry_point_for_navigator() 
            avoid = set() 
            take = set() 
            objectives = deepcopy(self.hte_surf.objective_points)

            self.hte_nav = HTENavigator(epoint,avoid,take,objectives,\
                self.hte_surf.prg,path_log_length=float('inf'),\
                absolute_avoid=False,visual_radius=DEFAULT_HTE_VISUAL_RADIUS)
        
        assert self.hte_nav.loc in self.hte_surf.entry_points 
        self.feed_navigator_context() 
        self.register_threat_contact(self.hte_nav.loc)
        return 

    def run_navigator(self): 
        if self.verbose: print("-- navigator at node={}, fuel={}".format(self.hte_nav.loc,self.hte_nav.fuel))

        while not self.hte_nav.fin_stat: 
            next(self) 
            if self.verbose: print("-- navigator at node={}, fuel={}".format(self.hte_nav.loc,self.hte_nav.fuel))
        if self.verbose: print("-- status: ",self.hte_nav.success_stat)
        return

    def __next__(self): 
        if self.hte_nav.fin_stat: 
            return 

        l = next(self.hte_nav) 
        self.feed_navigator_context() 

        contact_stat = self.register_threat_contact(l) 

        # case: navigator made contact with threat. terminate 
        #       navigator. 
        if contact_stat: 
            self.hte_nav.made_contact()
            

        # case: navigator made contact with objective. 
        obj_stat = self.hte_nav.loc in self.hte_surf.objective_points
        if obj_stat: 
            self.hte_nav.made_objective() 
        return

    def feed_navigator_context(self): 
        n,r = self.hte_nav.loc,self.hte_nav.visual_radius
        qsf = QuickSubgraphFetcher(self.hte_surf.base_graph)
        d = qsf.subgraph(n,r) 
        self.hte_nav.receive_context(d)
        return 

    def register_threat_contact(self,l): 
        # case: l is not a threat node 
        if l not in self.hte_surf.threat_map: 
            return False 

        # case: threat has been nullified 
        t = self.hte_surf.threat_map[l] 
        if t.fin_stat:
            return False 

        # retrieving variables to feed into <HTESurface> for threat registration. 

        #   get only the nodes of the navigator travel log in the 
        #   navigator context
        pertinent_path_info = deepcopy(self.hte_nav.path_log) 
        i = 0 
        while i < len(pertinent_path_info): 
            p = pertinent_path_info[i] 
            if p not in self.hte_nav.context: 
                pertinent_path_info.pop(i) 
            else: 
                i += 1
    
        #   get only the threat nodes in navigator context 
        threats = set(self.hte_surf.threat_map.keys()) 
        context_nodes = set(self.hte_nav.context.keys())
        threats = threats.intersection(context_nodes) 

        # feed the <HTESurface> navigator info 
        self.hte_surf.update_threat_activation(l,pertinent_path_info,threats)
        return True 

    #----------------------------------------------------------------------------------------------

    def reproduce_terminated_navigator(self):
        if not self.hte_nav.fin_stat: return 

        epoint = self.choose_entry_point_for_navigator() 
        hten = self.hte_nav.reproduce(epoint,iso_predict_mode=True)  

        self.terminated_navigators.append(self.hte_nav) 
        self.hte_nav = hten 
        self.feed_navigator_context() 
        self.register_threat_contact(self.hte_nav.loc)
        self.hte_nav.fuel = DEFAULT_NAVIGATOR_NODE_FUEL_MULTIPLIER * len(self.hte_surf.base_graph)
        if self.verbose: print("** reproducing navigator at entry={}".format(self.hte_nav.loc)) 
        return

    def choose_entry_point_for_navigator(self): 
        entry_points = sorted(self.hte_surf.entry_points)
        i = int(self.hte_surf.prg()) % len(entry_points) 
        return entry_points[i] 