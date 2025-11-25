from collections import defaultdict 

class GraphGen:

    def __init__(self,is_dsg,prg,is_realtime_gen:bool,\
        vertex_degree=None,edge_connectivity=None):

        assert is_dsg in {0,1}
        assert type(is_realtime_gen) == bool 
        assert type(vertex_degree) == int and vertex_degree > 0 

        if type(edge_connectivity) == float: 
            assert 1.0 >= edge_connectivity >= 0.0 
        else: 
            assert type(edge_connectivity) == type(None)

        self.is_dsg = is_dsg 
        self.prg = prg 
        self.is_realtime_gen = is_realtime_gen
        self.vertex_degree = vertex_degree
        self.edge_connectivity = edge_connectivity

        self.finstat = False 
        self.d = defaultdict(set)  
        return

    def preproc(self): 
        medges_ = sum([i for i in range(1,self.vertex_degree)])

        if self.is_dsg == 0: 
            self.max_edges = medges_
        elif self.is_dsg == 1: 
            self.max_edges = medges_ * 2 
        self.edge_degree = ceil(self.edge_connectivity * self.max_edges)

        if self.is_realtime_gen: 
            return 

        for i in range(self.vertex_degree): 
            self.d[i] = set() 
        return

    def __next__(self): 
        if self.finstat: 
            return False 