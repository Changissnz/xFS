from graph_models.dfs import * 
from graph_models.bfs import * 

"""
controller for navigating an undirected simple graph. Can use BFS or DFS. 
Main features include target node search and travel cost accounting. 
"""
class USGController:

    def __init__(self): 
        self.searches = dict() 
        self.search_target_nodeset = dict()
        self.found_target_nodeset = dict() 
        self.search_ctr = 0 
        self.no_duplicate_touch_nodes__combined = False 
        self.touched_nodes__combined = set() 
        return

    def set_new_search(self,is_dfs:bool,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None,search_target_nodeset:set=set(),\
        no_duplicate_touch_nodes=False):

        if is_dfs: 
            q = DFSCache(start_node,d,edge_cost_function,2,\
                nextnode_priority_function,no_duplicate_touch_nodes)
        else: 
            q = BFSCache(start_node,d,edge_cost_function,\
                nextnode_priority_function,no_duplicate_touch_nodes)

        self.searches[self.search_ctr] = q 
        self.search_target_nodeset[self.search_ctr] = search_target_nodeset 
        self.found_target_nodeset[self.search_ctr] = set() 
        self.search_ctr += 1 
        return

    """
    return:
    - cost of move, ?has terminated?, set of target nodes found 
    """
    def move_search(self,search_index): 
        assert search_index in self.searches 

        q = self.searches[search_index] 
        stat1 = q.move_one()  

        tcost = sum([q.fetch_edge_cost(x[0],x[1]) \
            for x in q.previous_edges])

        found_nodes = set()
        for x in q.previous_edges:
            if x[1] in self.search_target_nodeset[search_index]:
                found_nodes |= {x[1]}
                self.found_target_nodeset[search_index] |= {x[1]}
        
        # case: update touched nodes for all searches 
        if self.no_duplicate_touch_nodes__combined: 
            self.touched_nodes__combined |= q.touched_nodes 
            self.update_no_duplicate_touch__combined() 

        return tcost,stat1,found_nodes 

    def recent_edges(self,search_index): 
        return self.searches[search_index].previous_edges

    def set_no_duplicate_touch(self,index): 
        #assert type(self.searches[index]) == BFSCache
        self.searches[index].no_duplicate_touch_nodes = True 

    """
    used to synchronize all current searches to be considerate 
    of the one superset of touched nodes spread out between them. 
    """
    def set_no_duplicate_touch__combined(self,stat):
        assert type(stat) == bool  
        self.no_duplicate_touch_nodes__combined = stat 
        self.touched_nodes__combined = set() 
        for v in self.searches.values(): 
            self.touched_nodes__combined |= v.touched_nodes

    def update_no_duplicate_touch__combined(self): 
        for v in self.searches.values(): 
            v.touched_nodes = deepcopy(self.touched_nodes__combined) 
        return 