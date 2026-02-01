from graph_models.eb_graph_navigator import * 

"""
for Chaser agent 
"""
class CaptureFormationDecider: 

    def __init__(self,chaser):  
        self.chaser = chaser 
        return

    def partition_review(self): 

        return -1 

    def bull_partition_review(self): 

        return -1 

"""
for Bull agent 
"""
class EscapePathDecider: 

    def __init__(self,bull):  
        self.bull = bull  
        return

    def partition_review(self): 
        return -1 