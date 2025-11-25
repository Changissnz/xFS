from collections import defaultdict 

class GraphGen:

    def __init__(self,is_usg,prg,is_realtime_gen:bool=True,vertex_degree=None,\
        edge_connectivity=None):
        assert is_usg in {0,1,2}
        assert type(is_realtime_gen) == bool 
        assert type(vertex_degree) in {type(None),int}
        if type(vertex_degree) == int: 
            assert vertex_degree > 0 

        if type(edge_connectivity) == float: 
            assert 1.0 >= edge_connectivity >= 0.0 
        else: 
            assert type(edge_connectivity) == type(None)

        self.is_usg = is_usg 
        self.prg = prg 
        self.is_realtime_gen = is_realtime_gen
        self.vertex_degree = vertex_degree
        self.edge_connectivity = edge_connectivity

        self.finstat = False 
        return

    def preproc(self): 
        return -1 

    def __next__(self): 
        if self.finstat: 
            return False 



        