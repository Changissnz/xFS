from .micrograph import * 
from math import ceil 
from morebs2.graph_basics import * 
    
"""
given number of vertices for simple,undirected graph 
"""
def max_simple_edges(num_vertices): 
    if num_vertices in {0,1}:  
        return 0 
    return sum([i for i in range(1,num_vertices)])

# TODO: relocate this.
"""
draws the minumum number of edges for a graph, directed 
or undirected, to be one component (all nodes are connected). 
"""
def graph_to_one_component(G:defaultdict,prg): 

    gx = GraphComponentDecomposition(G) 
    gx.decompose() 

    if gx.is_directed: 
        components = [sorted(flatten_setseq(c)) for c in gx.components] 
    else: 
        components = [sorted(c) for c in gx.components]

    i = 0 
    l = len(components) - 1 
    print("connecting {} components".format(l + 1)) 
    for j in range(l): 
        c0 = components[j] 
        c1 = components[j+1] 

        i0 = int(prg()) % len(c0)
        i1 = int(prg()) % len(c1) 

        n0,n1 = c0[i0],c1[i1]

        G[n0] |= {n1} 
        if not gx.is_directed: 
            G[n1] |= {n0}  
    return G 

# TODO: relocate this.
def directed_to_undirected_graph(d): 
    assert type(d) in {defaultdict,dict}

    for k,v in d.items(): 
        for v_ in v: 
            if v_ not in d: 
                d[v_] = {k}
                continue 
            d[v_] |= {k} 
    return d 

#
"""
generates a graph,directed or not, according to given 
parameters `vertex_degree` and `edge_connectivity`. 
"""
class GraphGen:

    """
    is_realtime_gen := ?vertices not declared at start? 
    """
    def __init__(self,is_dsg,prg,is_realtime_gen:bool,\
        vertex_degree=None,edge_connectivity=None):

        assert is_dsg in {0,1}
        assert type(is_realtime_gen) == bool 
        assert type(vertex_degree) == int and vertex_degree > 0 
        assert type(edge_connectivity) == float and 1.0 >= edge_connectivity >= 0.0 

        self.is_dsg = is_dsg 
        self.prg = prg 
        self.is_realtime_gen = is_realtime_gen
        self.vertex_degree = vertex_degree
        self.edge_connectivity = edge_connectivity

        self.finstat = False 
        self.d = defaultdict(set)  
        self.preproc() 
        return

    def to_file(self,fp): 
        dict_to_file(self.d,fp)

    # TODO: test 
    def isotransform(self,start_integer):
        x = dict() 
        R1 = [i for i in range(self.vertex_degree)]
        R2 = [i for i in range(start_integer,start_integer + self.vertex_degree)] 
        
        for (i,j) in zip(R1,R2): 
            x[i] = j 
        
        mg = MicroGraph(self.d) 
        mg2 = MicroGraph.isotransform_MG(mg,x)
        self.d = mg2.dg 

    def preproc(self): 
        medges_ = max_simple_edges(self.vertex_degree)

        if self.is_dsg == 0: 
            self.max_edges = medges_
        elif self.is_dsg == 1: 
            self.max_edges = medges_ * 2 
        self.wanted_edge_degree = ceil(self.edge_connectivity * self.max_edges)
        self.current_edge_degree = 0 

        if self.is_realtime_gen: 
            return 

        for i in range(self.vertex_degree): 
            self.d[i] = set() 
        return

    """
    current edge connectivity 
    """
    def edge_connectivity_(self):

        medges_ = max_simple_edges(len(self.d))
        if medges_ == 0: 
            return 2.0 

        medges_ = medges_ * 2 if self.is_dsg else medges_ 
        return self.current_edge_degree_() / medges_ 


    def current_edge_degree_(self): 
        c = 0 
        for k,v in self.d.items(): 
            c += len(v) 
        
        if self.is_dsg: 
            return c 

        return int(c / 2)

    def full_run(self): 
        while not self.finstat: 
            self.__next__() 
        
    def __next__(self): 
        if self.finstat: 
            return False 

        if self.is_realtime_gen: 
            stat = self.new__realtime() 
        else: 
            stat = self.new_edge()
        self.finstat = not stat 
        return not self.finstat 

    def new__realtime(self): 
        # case: maybe add another vertex if vertex capacity not reached
        l = len(self.d)
        if l < self.vertex_degree: 

            # subcase: empty vertices 
            if l == 0: 
                self.d[l] = set() 
                return True 

            q = int(self.prg()) % 2 

            stat = False 
            # add new vertex 
            if q: 
                if l not in self.d: 
                    self.d[l] = set() 
                    stat = True 
                if stat: 
                    return stat 

            stat = False 
            # subcase: connectivity has been reached, have to add another vertex 
            ec = self.edge_connectivity_()
            if ec >= self.edge_connectivity: 
                if l not in self.d: 
                    self.d[l] = set() 
                    stat = True 
                if stat: 
                    return stat 
            return self.new_edge() 

        # case: add new edge 
        return self.new_edge()

    def new_edge(self): 
        if self.current_edge_degree >= self.wanted_edge_degree: 
            return False 

        x = sorted(self.d.keys()) 
        while len(x) > 0: 
            n = int(self.prg()) % len(x) 
            n = x.pop(n)
            n2 = self.available_endnodes_for_node(n) 
            if len(n2) == 0: 
                continue 

            n2 = sorted(n2)
            nx = int(self.prg()) % len(n2) 
            nx = n2[nx] 
            self.d[n] |= {nx} 
            if not self.is_dsg: 
                self.d[nx] |= {n} 

            self.current_edge_degree += 1 
            break 
        return True 

    def available_endnodes_for_node(self,n):
        rx = set([i for i in range(self.vertex_degree)]) - {n} 
        return rx - self.d[n]