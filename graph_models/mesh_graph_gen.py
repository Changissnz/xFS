from .graph_gen import * 
from .node_path import * 
from morebs2.numerical_generator import prg_choose_n,prg__single_to_int,prg__constant
from morebs2.graph_basics import flatten_setseq

#------------------------------ functions specialized for class<ParallelGraphSurface>

"""
return: 
- set of nodes comprising the parallel 
"""
def parallel_base_nodes(pgraph): 
    assert type(pgraph) == defaultdict 
    return set(pgraph.keys()) 

"""
return: 
- set of nodes connected to parallel but belonging to 
  another parallel 
"""
def parallel_other_nodes(pgraph): 
    assert type(pgraph) == defaultdict 
    base_nodes = parallel_base_nodes(pgraph) 
    total_nodes = flatten_setseq([v for v in pgraph.values()])
    return total_nodes - base_nodes  

#--------------------------------------------------------------

"""
represents one dimension, consisting of n disconnected parallels, 
for a lattice graph. 
"""
class ParallelGraphSurface: 

    def __init__(self,starting_idn,prg,parallel_length_range,is_dsg:bool):
        assert is_valid_range(parallel_length_range,True,False) 
        assert type(prg) in {MethodType,FunctionType} 

        self.starting_idn = starting_idn 
        self.current_index = starting_idn
        self.prg = prg 
        self.pl_range = parallel_length_range
        self.is_dsg = is_dsg 
        self.parallels = []
        self.parallel_heads = [] 
        self.parallel_tails = []
        self.parallels_nodeset = []  

    def nodeset(self): 
        return flatten_setseq(self.parallels_nodeset) 

    def __len__(self): 
        return len(self.parallels)

    def __getitem__(self,i):
        if isinstance(i, slice): 
            return self.p.__getitem__(i)    

        if type(i) in {list,np.ndarray}:
            qx = []
            for i_ in i:
                qx.append(self.__getitem__(i_))
            return qx 

        assert i < len(self) 
        return self.parallels[i]   

    def one_new_parallel(self): 
        num_vertices = int(modulo_in_range(self.prg(),self.pl_range)) 
        G = generate_graph__path(num_vertices,self.current_index,self.is_dsg)
        self.parallels.append(G) 
        self.parallel_heads.append(self.current_index) 
        self.current_index += num_vertices
        self.parallel_tails.append(self.current_index - 1) 

        self.parallels_nodeset.append(set(G.keys()))
        return

    def connect_to_surface(self,parallel_index,num_heads,other_surface,num_other_parallels):  
        assert 0 <= parallel_index < len(self) 
        assert type(other_surface) == ParallelGraphSurface
        assert 0 <= num_other_parallels <= len(other_surface) 

        if num_other_parallels == 0: 
            return 

        # choose the first node from this parallel 
        parallel = self[parallel_index]  
        keys = sorted(parallel.keys())

        heads = prg_choose_n(keys,num_heads,prg__single_to_int(self.prg),is_unique_picker=True) 

        for h in heads: 
            self.connect_to_surface_(parallel_index,h,other_surface,num_other_parallels) 

    def connect_to_surface_(self,parallel_index,parallel_head,other_surface,num_other_parallels):  

        parallel = self[parallel_index]  

        # choose n parallels from the other surface 
        q = [i for i in range(len(other_surface))] 
        q_ = prg_choose_n(q,num_other_parallels,prg__single_to_int(self.prg),is_unique_picker=True)

        ##print("connecting surface @ {} to {} other parallels".format(parallel_index,num_other_parallels))
        ref = parallel_head  
        chosen_parallel_nodes = [] 
        for (i,p_index) in enumerate(q_): 

            parallel2 = other_surface[p_index] 
            keys = sorted(parallel2.keys())
            index = int(self.prg()) % len(keys)
            node2 = keys[index] 
            chosen_parallel_nodes.append(node2) 

            parallel[ref] |= {node2} 
            if not self.is_dsg: 
                parallel2[node2] |= {ref} 

            parallel = parallel2 
            ref = node2 
        return

    def uniform_connect_to_surface(self,parallel_index,other_surface):

        l = len(other_surface) 
        for i in range(l): 
            self.uniform_connect_to_surface_(parallel_index,other_surface,i)
        return

    def uniform_connect_to_surface_(self,parallel_index,other_surface,parallel_index_2): 
        parallel = self[parallel_index]
        parallel2 = other_surface[parallel_index_2]

        keys1 = sorted(parallel.keys())
        keys2 = sorted(parallel2.keys())
        max_length = max([len(keys1),len(keys2)]) 


        for i in range(max_length):
            i0 = i % len(keys1) 
            i1 = i % len(keys2) 
            n0,n1 = keys1[i0],keys2[i1]

            parallel[n0] |= {n1} 
            if not self.is_dsg: 
                parallel[n1] |= {n0} 
        return

    def to_MicroGraph(self): 
        x = MicroGraph(defaultdict(set)) 
        for x2 in self.parallels: 
            x2_ = MicroGraph(x2) 
            x = x + x2_ 
        return x 

    def node_to_parallel_index(self,n): 
        for (i,s) in enumerate(self.parallels): 
            if n in s: 
                return i 
        return -1 

    """
    index of other surface's parallel -> number of parallel's nodes connected to this surface

    NOTE: connection is target of (source,target) edge format.  
    """
    def parallel_intersection_degree_map(self,other_surface): 
        assert type(other_surface) == ParallelGraphSurface

        d = defaultdict(int)
        for p in self.parallels: 
            other_nodes = parallel_other_nodes(p)
            for t in other_nodes:
                q = other_surface.node_to_parallel_index(t)
                if q != -1: 
                    d[q] += 1 
        return d

"""
Used to generate strictly two-dimensional mesh graphs, simple and 
undirected. For lattice graphs of greater dimension and connectivity 
than the simple square patterns, refer to the generators in 
file<graph_models.lattice_graph_gen>. 
"""
class Mesh2DGraphGen(ParallelGraphSurface):

    def __init__(self,starting_idn,num_rows,num_cols): 
        assert type(num_rows) == int and num_rows > 0

        prg = prg__constant(1)  
        super().__init__(starting_idn,prg,[num_cols,num_cols+1],is_dsg=False) 
        self.num_rows = num_rows 

        self.G = None 

    """
    main method
    """ 
    def make(self): 
        self.make_parallel_frame() 
        self.connect_columns() 

    def make_parallel_frame(self): 

        for _ in range(self.num_rows): 
            self.one_new_parallel()
        self.G = self.to_MicroGraph().dg 

    def connect_columns(self): 
        for i in range(1,self.num_rows): 
            self.connect_column(i) 

    """
    connects row at `index` with previous row 
    at `index - 1`. 
    """
    def connect_column(self,index): 
        assert self.num_rows > index >= 1

        p0 = NodePath.from_graph(self.parallels[index -1],False) 
        p1 = NodePath.from_graph(self.parallels[index],False) 

        for j in range(self.pl_range[0]): 
            n0,n1 = p0[j],p1[j] 
            self.G[n0] |= {n1} 
            self.G[n1] |= {n0}  