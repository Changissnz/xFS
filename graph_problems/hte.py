"""
Hidden Threat Exposure walkthroughs  
"""
from quant.hte_aux import * 
from quant.hte_navigator import* 

DEFAULT_NAVIGATOR_NODE_FUEL_MULTIPLIER = 1.0 

# TODO: test. 
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
----------------------------------------------------------------------------

The <HTENavigator> is a subclass of <NodeObjectiveNavigator>, a structure 
that uses these four node categories to prioritize which node to travel 
to during the course of navigation:
- objective (ideal node to be on)
- take (a node that the navigator classified as safe to travel over)
- possible avoid (a node that the navigator classified as a possible threat node)
- avoid (a node that the navigator classified as a certain threat node).
<HTENavigator> uses a stochastic process to make decisions revolving around these 
four node categories. For a starting node n0 and objective node n1, one <HTENavigator> 
may take a path P from n0 to n1, but a succeeding <HTENavigator> may not take the same 
path P despite starting at same node n0. 

If two nodes are of the same category, the <NodeObjectiveNavigator> prioritizes 
the node less frequently travelled, according to its node encounters map,  
    encountered node -> frequency of travel.

A navigator travels a surface (network) with threats of unknown location (node) 
on it. Navigator terminates when it travels into a threat node (loss) or an objective 
node (win) or when it runs out of fuel (loss). When a navigator terminates, <HTEBot> can 
summon another navigator instance for the same surface. This navigator instance may have 
access to the previous navigator's node encounters map, depending on <HTEBot> variable 
`navigator_remembers_past_encounters`. If the navigator is `memory_less`, it does not store 
the nodes of the paths it took into memory, the nodes without threats on them into the 
`take` nodeset, in other words. The next summoned navigator for the same <HTESurface> will 
not know the nodes the previous navigator took. 

When <HTESurface> 'reproduces` a new <HTESurface> from a previous one, this new <HTESurface> 
is an isomorphic derivation of the previous surface. So the threat nodes of the previous 
surface may translate into those of similar geometric property to this new <HTESurface>. 
If `navigator_uses_isomorphic_prediction` is set to True, the <HTENavigator> will attempt 
to predict threat nodes on the new <HTESurface> before proceeding to traveling it. 

From the navigator perspective, there are three mode classes: 
- navigator_remembers_past_encounters
- navigator_uses_isomorphic_prediction
- memory_less navigator (see function<set_memoryless_navigator>)

A <HTEThreat> may be one of two categories, contra or constant. When a navigator encounters 
a <HTEThreat>, the navigator terminates and the lifespan of the <HTEThreat> reduces by 1 
(<HTEThreat> terminates when its lifespan decreases to 0). If the <HTEThreat> is still 
active after the navigator encounters it, <HTEThreat> will stay at the same node if it is 
constant. If <HTEThreat> is contra, it will attempt to relocate to another node that satisfies 
the following conditions: 
- new node location does not have an existing threat on it, 
- new node location is a node on an ending subpath the terminated navigator took to get to the 
  original threat location. The ending subpath is a suffix of the entire path the navigator took, which 
  may contain duplicate nodes, and is of length equal to the navigator's radius of vision plus one. 
A contra <HTEThreat> that cannot find a new node location that satisfies these two conditions 
will stay at the original node location. 

There are two types of reproductions in <HTEBot>, one for the <HTESurface> and one for the 
<HTENavigator>. 
"""
class HTEBot:

    def __init__(self,hte_surface,hte_navigator,navigator_remembers_past_encounters:bool=False,\
        navigator_uses_isomorphic_prediction:bool=True,verbose=False):  
        assert type(hte_surface) == HTESurface
        assert type(hte_navigator) in {type(None),HTENavigator} 

        self.hte_surf = hte_surface
        self.hte_surf_prior_ref = None 
        self.hte_nav = hte_navigator
        self.navigator_remembers = navigator_remembers_past_encounters
        self.verbose = verbose 
        self.previous_hsurfaces = [] 
        self.hsurface_prior_ref = [] 
        self.terminated_navigators = [] 

        self.preproc() 
        self.hte_nav.uses_isomorphic_prediction = navigator_uses_isomorphic_prediction 
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

    #-------------------------------------------- methods for node navigator 
    def run_navigator(self): 
        if self.verbose: print("-- navigator at node={}, fuel={}".format(self.hte_nav.loc,self.hte_nav.fuel))

        while not self.hte_nav.fin_stat: 
            next(self) 
            if self.verbose: print("-- navigator at node={}, fuel={}".format(self.hte_nav.loc,self.hte_nav.fuel))
        if self.verbose: print("-- status: ",self.hte_nav.success_stat)
        return

    def set_memoryless_navigator(self,stat:bool=True):
        assert type(stat) == bool  
        self.hte_nav.memory_less = stat  

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

    #--------------------------- methods to produce succeeding navigators and threat surfaces

    def reproduce_terminated_navigator(self,next_full_context=None):

        epoint = self.choose_entry_point_for_navigator() 
        hten = self.hte_nav.reproduce(epoint,next_full_context=next_full_context)  
        if self.navigator_remembers and type(next_full_context) == type(None): 
            hten.encountered = self.hte_nav.encountered 
            hten.encountered[epoint] += 1 

        self.terminated_navigators.append(self.hte_nav) 
        self.hte_nav = hten 
        self.feed_navigator_context() 
        self.register_threat_contact(self.hte_nav.loc)
        self.hte_nav.fuel = DEFAULT_NAVIGATOR_NODE_FUEL_MULTIPLIER * len(self.hte_surf.base_graph)
        if self.verbose: print("** reproducing navigator at entry={}".format(self.hte_nav.loc)) 
        return

    def reproduce_surface(self): 
        htes2,isomap = self.hte_surf.prng_reproduction_scheme2() 

        isomap_hyp = {} 
        nav_avoid = self.hte_nav.avoid 
        for k,v in isomap.items(): 
            if k not in nav_avoid: 
                continue 

            isomap_hyp[k] = (v,modulo_in_range(\
                int(self.hte_surf.prg()),DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE))
            
        self.previous_hsurfaces.append(self.hte_surf) 
        if type(self.hte_surf_prior_ref) != type(None): 
            self.hsurface_prior_ref.append(self.hte_surf_prior_ref) 

        self.hte_surf = htes2 
        self.hte_surf_prior_ref = isomap 

        next_full_context = (self.hte_surf.base_graph,isomap_hyp,self.hte_surf.objective_points)
        self.reproduce_terminated_navigator(next_full_context=next_full_context)
        return

    def choose_entry_point_for_navigator(self): 
        entry_points = sorted(self.hte_surf.entry_points)
        i = int(self.hte_surf.prg()) % len(entry_points) 
        return entry_points[i] 