from .micrograph import * 
from math import ceil 
from morebs2.graph_basics import * 
from morebs2.matrix_methods import is_valid_range
from morebs2.numerical_generator import modulo_in_range
from types import FunctionType,MethodType

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
Selection of unconnected node pairs for edges done by PRNG 
`prg`. 
"""
def graph_to_one_component(G:defaultdict,prg,verbose=False): 

    gx = GraphComponentDecomposition(G) 
    gx.decompose() 

    if gx.is_directed: 
        components = [sorted(flatten_setseq(c)) for c in gx.components] 
    else: 
        components = [sorted(c) for c in gx.components]

    i = 0 
    l = len(components) - 1 
    if verbose: print("connecting {} components".format(l + 1)) 
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

    keys = sorted(d.keys())
    for k in keys:
        v = d[k]  
        for v_ in v: 
            if v_ not in d: 
                d[v_] = {k}
                continue 
            d[v_] |= {k} 
    return d 


"""
counts the number of pairs of edges 
    (u,v) (v,u) 
with non-equal weights. 
"""
def nonequal_edge_weight_counts(G,wf): 
    assert type(G) == defaultdict  

    non_identical_weights = 0  
    number_bidirectional = 0 

    for k,v in G.items(): 
        for v_ in v: 
            w = wf(k,v_) 

            try: 
                w_ = wf(v_,k) 
            except: 
                continue 
            
            if w != w_: 
                non_identical_weights += 1 
            number_bidirectional += 1 
    return non_identical_weights,number_bidirectional 

def does_path_exist(G,p): 
    assert type(G) == defaultdict  
    assert type(p) == list 

    if len(p) == 0: 
        return True 
    
    if len(p) == 1: 
        return p[0] in G

    for i in range(len(p) - 1): 
        st = (p[i],p[i+1]) 
        if p[i] not in G: 
            return False 
        if p[i+1] not in G[p[i]]: 
            return False 
    return True 

#-------------------------- two elementary graph types 

def generate_graph__path(num_vertices,starting_node_idn:int,is_dsg:bool): 
    G = defaultdict(set) 
    if num_vertices == 0: return G 

    c = starting_node_idn
    G[c] = set() 
    if num_vertices == 1: return G 

    for i in range(c+1,c+num_vertices):
        G[i-1] |= {i} 
        if not is_dsg: 
            G[i] |= {i-1} 
    
    G[c+num_vertices-2] |= {c+num_vertices-1} 
    if not is_dsg: 
        G[c+num_vertices-1] |= {c+num_vertices-2}
    return G 

def generate_graph__complete(num_vertices,starting_node_idn:int): 
    assert num_vertices >= 1 
    G = defaultdict(set) 

    N = {i for i in range(starting_node_idn,starting_node_idn+num_vertices)} 

    for i in range(starting_node_idn,starting_node_idn+num_vertices): 
        G[i] = N - {i}
    return G 

#---------------------------------------------------------------------------- 

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
        vertex_degree=None,edge_connectivity=None,verbose=False):

        assert is_dsg in {0,1}
        assert type(is_realtime_gen) == bool 
        assert type(vertex_degree) == int and vertex_degree > 0 
        assert type(edge_connectivity) == float and 1.0 >= edge_connectivity >= 0.0 

        self.is_dsg = is_dsg 
        self.prg = prg 
        self.is_realtime_gen = is_realtime_gen
        self.vertex_degree = vertex_degree
        self.edge_connectivity = edge_connectivity
        self.verbose = verbose 
        
        self.finstat = False 
        self.d = defaultdict(set)  
        self.preproc() 
        return

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
    main method
    """
    def full_run(self): 
        while not self.finstat: 
            if self.verbose:
                print("degree {} conn {}".format(len(self.d),self.current_edge_degree))
            self.__next__() 
        
    def __next__(self): 
        if self.finstat: 
            return False 

        if self.is_realtime_gen: 
            stat = self.new__realtime() 
        else: 
            stat = self.new_edge()
        self.finstat = not stat# and len(self.d) == self.vertex_degree
        return not self.finstat 

    def new__realtime(self): 
        # case: maybe add another vertex if vertex capacity not reached
        l = len(self.d)
        if l < self.vertex_degree: 
            #   an easier function to understand  
            """
            self.d[l] = set() 

            q = int(self.prg()) % 2 
            if self.edge_connectivity_() < self.edge_connectivity and q: 

                return self.new_edge() 
            return True 
            """

            # subcase: empty vertices 
            #"""
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
            #"""

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
            nq = int(self.prg()) % len(n2) 
            nq = n2[nq] 
            self.d[n] |= {nq} 
            if not self.is_dsg: 
                self.d[nq] |= {n} 

            self.current_edge_degree += 1 
            break 
        return True 

    def available_endnodes_for_node(self,n):
        rx = set([i for i in range(len(self.d))]) - {n} 
        return rx - self.d[n]

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

    def to_file(self,fp): 
        dict_to_file(self.d,fp)

#----------------------------------------------------------------------------------------- 

class GraphWeightGen: 

    def __init__(self,G,prg,is_dsg:bool,weight_range): 
        assert type(G) == defaultdict 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(is_dsg) == bool 
        assert is_valid_range(weight_range,True,False) or \
            is_valid_range(weight_range,False,False) 

        self.G = G 
        self.G_ = deepcopy(G)
        self.prg = prg 
        self.is_dsg = is_dsg 
        self.weight_range = weight_range 

        self.W = None 
        self.generate() 

    def generate(self): 
        self.W = defaultdict(float)

        keys = sorted(self.G_.keys())
        for k in keys:
            v = self.G_[k] 
            for v_ in v: 
                w = modulo_in_range(self.prg(),self.weight_range) 
                self.W[(k,v_)] = w 

                if not self.is_dsg: 
                    if k in self.G_[v_]: 
                        self.W[(v_,k)] = w 
                        self.G_[v_] -= {k} 
            del self.G_[k] 
        return 

    """
    NOTE: 
    edges (u,u) always output 0 
    """
    def weight(self,u,v):
        if u == v: return 0 

        ks = [x for x in self.W if x[0] == u] 
        assert (u,v) in self.W, "({},{}) not found".format(u,v) 
        return self.W[(u,v)] 


#-----------------------------------------------------------------------------------------

from morebs2.numerical_generator import prg__LCG

def base_graph_sample_FU(): 
    is_dsg = False 
    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
    is_realtime_gen = True 
    vertex_degree = 250 
    edge_connectivity = 0.22#0.175 
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity) 
    gg.full_run() 

    D4 = graph_to_one_component(deepcopy(gg.d),prg)
    return D4 

def base_graph_sample_25N(): 
    is_dsg = False 
    prg = prg__LCG(15.6,653.44,-2174.1174,22199.5) 
    is_realtime_gen = True 
    vertex_degree = 2500 
    edge_connectivity = 0.0022#0.175 
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity,verbose=False) 
    gg.full_run() 
    D4 = graph_to_one_component(deepcopy(gg.d),prg)
    return D4 

def generated_graph_sample_1000(vertex_degree=1000,edge_connectivity=0.001): 
    is_dsg = False 
    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
    is_realtime_gen = True 
    #vertex_degree = 1000
    #edge_connectivity = 0.001
    
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity,verbose=False) 
    gg.full_run() 
    
    D = gg.d 
    D2 = graph_to_one_component(deepcopy(gg.d),prg)
    return D2 