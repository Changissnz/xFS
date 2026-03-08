from .graph_gen import * 
from morebs2.numerical_generator import prg_choose_n,prg__single_to_int
from morebs2.graph_basics import flatten_setseq

"""
file used to generate lattice graphs of variable dimension. 
Two classes of lattice graphs: 
- variably connected 
- symmetric 
"""

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

"""
represents one dimension, consisting of n parallels, for a lattice graph. 
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

class LatticeGraphGen:

    def __init__(self,shape,prg,parallel_length_range,is_dsg:bool):  
        self.shape = shape 
        self.prg = prg 
        self.parallel_length_range = parallel_length_range
        self.is_dsg = is_dsg 
        self.index = 0 
        self.surfaces = []
        self.G = None 
        self.p2i_map = None

    def set_surfaces(self): 
        for x in self.shape: 
            pgs = ParallelGraphSurface(self.index,self.prg,self.parallel_length_range,self.is_dsg)

            for _ in range(x): 
                pgs.one_new_parallel()
            self.surfaces.append(pgs)  
            self.index = pgs.current_index
        return

    def merge_surfaces(self): 
        self.G = MicroGraph(defaultdict(set))

        for surface in self.surfaces: 
            self.G = self.G + surface.to_MicroGraph()
        self.G = self.G.dg 
        return 

    #-------------------------------------- functions to retrieve information 

    def surface_to_nodeset_map(self,is_parallel_seq:bool=False): 
        d = {} 
        for (i,s) in enumerate(self.surfaces): 
            q = deepcopy(s.parallels_nodeset)
            if is_parallel_seq: 
                d[i] = q 
            else: 
                d[i] = flatten_setseq(q)
        return d 

    def surface_to_node_heads_map(self):
        d = {} 
        for (i,s) in enumerate(self.surfaces): 
            d[i] = deepcopy(s.parallel_heads) 
        return d 

    """
    surface 1 index -> parallel 1 index -> 
    surface 2 index -> parallel 2 index -> 
        {intercepted nodeset of (surface 2,parallel 2) index}
    """
    def surface_parallels_to_interception_map(self): 

        dx = dict()
        for i in range(len(self.surfaces)): 
            dx[i] = self.surface_parallels_to_interception_map_(i)
        return dx 

    def surface_parallels_to_interception_map_(self,surface_index): 
        s = self.surfaces[surface_index] 

        d = defaultdict(None)
        for (i,p) in enumerate(s.parallels):
            d[i] = dict() 

            base_nodes = set(p.keys())
            total_nodes = flatten_setseq([v for v in p.values()]) | base_nodes 
            diff_nodes = total_nodes - base_nodes 
            
            q2 = [list(self.sp_index_of_node(n2)) + [n2] for n2 in diff_nodes]

            for q2_ in q2: 
                if q2_[0] not in d[i]: 
                    d[i][q2_[0]] = dict() 
                if q2_[1] not in d[i][q2_[0]]: 
                    d[i][q2_[0]][q2_[1]] = set() 
                d[i][q2_[0]][q2_[1]] |= {q2_[2]} 
        return d 


    """
    (surface,parallel) indices for the node `n`
    """
    def sp_index_of_node(self,n):
        for i,s in enumerate(self.surfaces): 
            q = s.node_to_parallel_index(n) 
            if q != -1: 
                return i,q 
        return -1,-1

    """
    return: 
    - (surface index,parallel index) -> number of nodes connected to node n (n is target node in (source,target) edge format)
    """
    def node_interception_map(self,n): 

        assert type(self.p2i_map) != type(None) 
        
        d = defaultdict(int)
        # surface 1 -> parallel 1 -> surface 2 -> parallel 2 -> {nodeset} 
        for k,v in self.p2i_map.items(): 
            # parallel 1 -> surface 2 -> parallel 2 -> {nodeset}
            for k2,v2 in v.items(): 
                # surface 2 -> parallel 2 -> {nodeset}
                for k3,v3 in v2.items(): 
                    # parallel 2 -> {nodeset}
                    for k4,v4 in v3.items(): 
                        if n in v4: 
                            d[(k,k2)] += 1 
        return d 

"""
Variably connected lattice graph generator. 

Graph outputs can be asymmetric in mesh geometry. 

N-dimensional vector `shape` specifies the number of parallels for 
every `ParallelGraphSurface`, a sequence of paths with no edge shared 
between any path at initial state. 
"""
class VCLatticeGraphGen(LatticeGraphGen): 

    def __init__(self,shape,prg,parallel_length_range,connection_density,\
        is_dsg:bool):   

        super().__init__(shape,prg,parallel_length_range,is_dsg) 
        self.connection_density = connection_density

    #-------------------------------------- constructor functions 

    """
    main method 
    """
    def make(self): 
        self.set_surfaces()
        self.connect_surfaces() 
        self.merge_surfaces()
        self.p2i_map = self.surface_parallels_to_interception_map() 

    def connect_surfaces(self): 
        for i in range(len(self.surfaces)): 
            self.connect_one_surface(i) 
        return

    def connect_one_surface(self,index): 
        q = self.surfaces[index] 

        other_surface_indices = [] 
        if self.is_dsg: 
            other_surface_indices = [i for i in range(len(self.surfaces)) if i != index] 
        else: 
            other_surface_indices = [i for i in range(index+1,len(self.surfaces))] 

        for other_index in other_surface_indices: 
            self.connect_surface2surface(index,other_index)
        return

    def connect_surface2surface(self,index1,index2): 

        s0 = self.surfaces[index1] 
        s1 = self.surfaces[index2] 

        num_parallels = ceil(self.connection_density * len(s0))
        candidates = [i for i in range(len(s0))] 
        parallel_indices = prg_choose_n(candidates,num_parallels,prg__single_to_int(self.prg),True)  

        #print("INDICES: ",index1,index2) 
        #print("-- parallels: ",num_parallels)
        #print("-- indices: ", parallel_indices)
        for parallel_index in parallel_indices:
            num_heads = ceil(self.connection_density * len(s0[parallel_index])) 
            num_other_parallels = ceil(self.connection_density * len(s1)) 
            s0.connect_to_surface(parallel_index,num_heads,s1,num_other_parallels)  

"""
Uniformly connects n surfaces, each surface possibly of different 
node dimension to each other. 

For two parallels, P1 and P2, from surfaces S1 and S2, respectively, 
the node-to-node connection goes as follows: 
- let m = max([|P1|,|P2|])
- connect P1[i % |P1|] to P2[i % |P2|] for every index i in range [0,m). 
"""
class SymmetricLatticeGraphGen(LatticeGraphGen):

    def __init__(self,shape,prg,parallel_length_range,\
        is_dsg:bool):   

        super().__init__(shape,prg,parallel_length_range,is_dsg) 
    
    def make(self): 
        self.set_surfaces()
        self.connect_surfaces() 
        self.merge_surfaces() 
        self.p2i_map = self.surface_parallels_to_interception_map() 

    def connect_surfaces(self): 
        for i in range(len(self.surfaces)): 
            self.connect_one_surface(i) 
        return

    def connect_one_surface(self,index): 
        q = self.surfaces[index] 

        other_surface_indices = [] 
        if self.is_dsg: 
            other_surface_indices = [i for i in range(len(self.surfaces)) if i != index] 
        else: 
            other_surface_indices = [i for i in range(index+1,len(self.surfaces))] 

        for other_index in other_surface_indices: 
            self.connect_surface2surface(index,other_index)
        return

    def connect_surface2surface(self,index1,index2): 
        s0 = self.surfaces[index1] 
        s1 = self.surfaces[index2] 

        for i in range(len(s0)):
            s0.uniform_connect_to_surface(i,s1)
        return 
