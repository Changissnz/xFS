from graph_models.dfs import * 
from graph_models.bfs import * 

"""
controller for navigating an undirected simple graph 
"""
class USGController:

    def __init__(self): 
        self.searches = dict() 
        self.search_target_nodeset = dict()
        self.found_target_nodeset = dict() 
        self.search_ctr = 0 
        return

    def set_new_search(self,is_dfs:bool,start_node,d:defaultdict,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION,\
        nextnode_priority_function=None,search_target_nodeset:set=set()):

        if is_dfs: 
            q = DFSCache(start_node,d,edge_cost_function,2,\
                nextnode_priority_function)
        else: 
            q = BFSCache(start_node,d,edge_cost_function,\
                nextnode_priority_function)

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

        return tcost,stat1,found_nodes 