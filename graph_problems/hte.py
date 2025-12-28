"""
Hidden Threat Exposure walkthroughs  
"""
from quant.hte_aux import * 
from quant.hte_navigator import* 

class HTEBot:

    def __init__(self,hte_surface,hte_navigator):  
        assert hte_surface == HTESurface
        assert hte_navigator == HTENavigator
        self.hte_surface = hte_surface
        self.hte_navigator = hte_navigator
        return 

    def __next__(self): 

        return -1 