from graph_models.hypergraph import * 
from graph_models.lattice_graph_gen import * 

DEFAULT_MAX_CATEGORY_SIZE__LATTICE_REPR = 10 

"""
A category-centric structure used by class<PRClassExpectedEffectTypeHL>. 

Represents arbitrary category C with `label_set` as the property space. 
Graph `G` is a lattice graph. 
NOTE: `G` is not checked by program for being a lattice graph. 

Every label l_i is associated with a node pair (h_i,t_i), the corresponding 
head and tail nodes of `G`. Additionally, label l_i has an associated expected 
path P, found in `label2path_map`. 

A label l_j that is to substitute for label l_k must take a path P_jk such that 
head(P_jk) = h_j, the head of the expected path for label l_j  
    AND 
tail(P_jk) = t_k, the tail of the expected path for label l_k. 
"""
class AssociativeCategoryLatticeRepr: 

    def __init__(self,label_set,G,label2ht_map,label2path_map):  

        assert type(label_set) == set
        assert type(G) == defaultdict 
        assert label_set == set(label2ht_map.keys()) 
        q = [] 
        for v in label2ht_map.values(): 
            q.extend(v) 
        assert len(q) == len(set(q)) 
        
        for k,v in label2path_map.items(): 
            h,t = label2ht_map[k] 
            assert v.head() == h and v.tail() == t 
            assert does_path_exist(G,v.p) 

        self.labels = label_set 
        self.G = G 
        self.label2ht_map = label2ht_map
        self.label2path_map = label2path_map
        self.paths_info = None 

    def fetch_shortest_paths(self): 
        self.paths_info,_ = BDFSCache.BFS_full(self.G,return_type="paths",prg=prg,max_search_radius=float('inf'),\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False) 

    def path_for_label(self,label): 
        return self.label2path_map[label] 

    def path_for_label_substitution(self,ref_label,substituted_label,prg):
        if ref_label == substituted_label: 
            return self.path_for_label(ref_label)

        h0,t0 = self.label2ht_map[ref_label] 
        h1,t1 = self.label2ht_map[substituted_label] 
        return self.paths_info[(h0,t1)]

    @staticmethod 
    def generate_instance(label_set,prg): 

        shape = [1] * len(labels) 
        parallel_length_range = (len(labels),len(labels)+1) 
        is_dsg = False 

        sgg = SymmetricLatticeGraphGen(shape,prg,parallel_length_range,\
            is_dsg)
        sgg.make()

        G = sgg.G 

        labels = sorted(label_set) 

        label2ht_map = dict() 
        label2path_map = dict()
        for (i,l) in enumerate(labels): 
            surface = sgg.surfaces[0] 
            h,t = surface.parallel_heads[0],surface.parallel_tails[0]
            label2ht_map[l] = (h,t) 

            nodeset = surface.parallels_nodeset[0]
            G2 = MicroGraph(G).subgraph_by_nodeset_(nodeset).dg 

            bdfs = BDFSCache(h,G2,is_bfs=False,prg=prg,\
                edge_cost_function=lambda u,v:1,num_paths_per_node=1,max_search_radius=float('inf'),\
                verbose=False)
            bdfs.exec() 

            p = bdfs.min_paths[t][0] 
            label2path_map[l] = p 

        return AssociativeCategoryLatticeReprs(label_set,G,label2ht_map,label2path_map) 

"""
Pseudo-Random Class Expected Effect, Type Hypergraph + Lattice Graph. 

Used for situations where there are expected effects from class. 
"""
class PRClassExpectedEffectTypeHL: 

    def __init__(self,hg,prg):   
        assert type(hg) == HyperGraph
        assert type(prg) in {MethodType,FunctionType} 

        self.hg = hg 
        self.prg = prg
        self.attribute2lattice_map = dict() 
        self.preprocess()  
        return

    def preprocess(self): 
        return -1 

    def generate_lattices(self): 

        return -1 

    def generate_lattice_for_category(self,cat): 
        assert cat in self.hg.rep 

        labels = self.hg.node2nodeset[cat] 