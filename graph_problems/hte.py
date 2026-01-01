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
        return 

    def __next__(self): 
        return -1 

    def relay_info_to_nav(self): 
        return -1 