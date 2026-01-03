"""
Hidden Threat Exposure walkthroughs  
"""
from quant.hte_aux import * 
from quant.hte_navigator import* 

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

    def __init__(self,hte_surface,hte_navigator):  
        assert hte_surface == HTESurface
        assert hte_navigator == HTENavigator
        self.hte_surf = hte_surface
        self.hte_nav = hte_navigator

        self.terminated_navigators = [] 
        return 

    #-------------------------------------------------------------------------------------------- 

    def preproc(self): 
        assert self.hte_nav.loc in self.hte_surf.entry_points 
        self.feed_navigator_context() 
        return 

    def __next__(self): 
        if self.hte_nav.fin_stat: 
            return 

        l = next(self.hte_nav) 
        contact_stat = self.register_threat_contact(l) 

        # case: navigator made contact with threat. terminate 
        #       navigator. 
        if contact_stat: 
            self.hte_nav.made_contact()
            
        self.feed_navigator_context() 
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
        entry_points = sorted(self.hte_surf.entry_points)
        i = int(self.prg()) % len(entry_points) 
        epoint = entry_points[i] 
        hten = self.hte_nav.reproduce(epoint) 

        self.terminated_navigators.append(self.hte_nav) 
        self.hte_nav = hten 
        return