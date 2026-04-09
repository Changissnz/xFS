from graph_models.hypergraph import * 
from graph_models.lattice_graph_gen import * 

# TODO: delete or use. 
DEFAULT_MAX_CATEGORY_SIZE__LATTICE_REPR = 10 

# TODO: test this. 

"""
A category-centric structure used by class<PRClassExpectedEffectTypeHL>. 

Represents arbitrary category C with `label_set` as the property space. 
Graph `G` is a lattice graph. 
NOTE: `G` is not checked by program for being a lattice graph. 

Every label l_i is associated with a node pair (h_i,t_i), the corresponding 
head and tail nodes of the label's parallel P_i in `G`. Additionally, label 
l_i has an associated expected path P_i (the same mentioned parallel) found 
in `label2path_map`. 

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

    def fetch_shortest_paths(self,prg): 
        self.paths_info,_ = BDFSCache.BFS_full(self.G,return_type="paths",prg=prg,max_search_radius=float('inf'),\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False) 

    def path_for_label(self,label): 
        return self.label2path_map[label] 

    def path_for_label_substitution(self,ref_label,substituted_label):
        assert type(self.paths_info) != type(None) 

        if ref_label == substituted_label: 
            return self.path_for_label(ref_label)

        h0,t0 = self.label2ht_map[ref_label] 
        h1,t1 = self.label2ht_map[substituted_label] 
        return self.paths_info[(h0,t1)]

    @staticmethod 
    def generate_instance(label_set,prg): 

        shape = [1] * len(label_set)  
        parallel_length_range = (len(label_set),len(label_set)+1) 
        is_dsg = False 

        sgg = SymmetricLatticeGraphGen(shape,prg,parallel_length_range,\
            is_dsg)
        sgg.make()

        G = sgg.G 

        labels = sorted(label_set) 

        label2ht_map = dict() 
        label2path_map = dict()
        for (i,l) in enumerate(labels): 
            surface = sgg.surfaces[i]  
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

        return AssociativeCategoryLatticeRepr(label_set,G,label2ht_map,label2path_map) 

"""
Pseudo-Random Class Expected Effect, Type Hypergraph + Lattice Graph. 

Used for situations where there are expected effects from class. 

A connected hypergraph is used to associate n categories with each other. 
Each category c_i has l_i labels belonging to it. A label l_q can belong to 
more than one category.

In this specification, however, a label l_k that does not belong to the same 
category c_j of another label l_j still has a non-zero association with that 
category, given by the hypergraph category c_j being reachable from some 
category c_k of l_k. 

In this way, any label l_r can `substitute` for another label l_s of a category 
c_s, such that l_r not in c_s. This substitution comes with a cost associated 
with traversing a path P_rs such that 
    P_rs != P_s; P_s the expected (ideal) path for a label l_s. 
NOTE: see the description of class<AssociativeCategoryLatticeRepr> for more 
      information on the expected path difference. 
In other words, every label is interchangeable with every other, regardless of 
status of inclusion in an arbitrary category. This interchangeability is not 
agnostic, requiring non-zero costs. 

For every category c_i, there is an <AssociativeCategoryLatticeRepr> R_i that 
contains the label-to-path info for the labels of c_i. There is 0 cost for 
a label l_j to operate for l_j in the context of category c_i, via its expected path 
in R_i (see variable<label2path_map>). A label l_k, not equal to l_j but is 
of the same category of c_i, can substitute for l_j via function<R_i.path_for_label_substitution>. 
This path P_kj will have a non-zero cost associated with it, since P_kj != P_j, 
the expected path for label l_j. In the extended case of l_k not being of the same 
category c_j of l_j, the path is piecewise (multiple disconnected paths), from one 
category c_{i} to the next connected category c_{i+1}, up through the category c_j. 
""" 
# NOTE: this structure is a more complex variant of class<HomoScriptNetwork>, in regards 
#       to its map, 
#           agent idn -> requirement idn -> path::list.   
class PRClassExpectedEffectTypeHL: 

    def __init__(self,hg,prg):   
        assert type(hg) == HyperGraph
        assert type(prg) in {MethodType,FunctionType} 

        self.hg = hg 
        self.prg = prg
        self.cat2lattice_map = dict() 
        self.preprocess()  
        return

    #-------------------------------------------------------------------------------

    def preprocess(self): 
        self.generate_lattices() 

        self.hg_paths_info,_ = BDFSCache.BFS_full(self.hg.rep,return_type="paths",\
            prg=self.prg,max_search_radius=float('inf'),\
            edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2,verbose=False) 
        return

    def generate_lattices(self): 
        N = sorted(self.hg.rep.keys()) 
        for n in N: 
            self.generate_lattice_for_category(n) 
        return

    def generate_lattice_for_category(self,cat): 
        assert cat in self.hg.rep 

        labels = self.hg.node2nodeset[cat] 
        aclr = AssociativeCategoryLatticeRepr.generate_instance(labels,self.prg)
        aclr.fetch_shortest_paths(self.prg)  
        self.cat2lattice_map[cat] = aclr 

    #----------------------------------------------------------------------------------- 

    def categorical_label2label_path(self,l0,l1,l1_cat,ext_prg):    
        assert type(ext_prg) in {MethodType,FunctionType}

        cat_nodeset = self.hg.node2nodeset[l1_cat] 
        assert l1 in cat_nodeset

        # case: two labels equal each other
        if l0 == l1: 
            return [self.cat2lattice_map[l1_cat].path_for_label(l1)] 

        categories = self.hg.base_node_to_H_nodeset(l0) 
        
        # case: l1_cat is one of the categories for l0 
        if l1_cat in categories: 
            q = self.cat2lattice_map[cat].path_for_label_substitution(l0,l1) 
            return [q] 

        # choose a category c0 associated with l0 
        categories = sorted(categories) 
        i = int(ext_prg()) % len(categories) 
        c0 = categories[i]

        # calculate a path 
        return self.categorical_label2label_path_(l0,l1,c0,l1_cat,ext_prg) 

    def categorical_label2label_path_(self,l0,l1,l0_cat,l1_cat,ext_prg): 

        # get the Hypergraph path 
        hg_path = self.hg_paths_info[(l0_cat,l1_cat)] 

        current_cat = l0_cat 
        current_label = l0 

        N = NodePath.preload([],[])
        N = []
        index = 1 
        lx = len(hg_path)
        while index < lx:  
            next_cat = hg_path.p[index] 
            nodeset = sorted(self.hg.H_nodeset_intersection(current_cat,next_cat)) 

            # choose a node in intersection 
            i = int(ext_prg()) % len(nodeset)
            l1_ = nodeset[i] 

            # get the path 
            L = self.cat2lattice_map[l0_cat] 
            P = L.path_for_label_substitution(current_label,l1_) 
            N.append(P) 
            
            current_cat = next_cat 
            current_label = l1_ 
            index += 1 

        last = hg_path.p[-1] 
        L = self.cat2lattice_map[last] 
        P = L.path_for_label_substitution(current_label,l1) 

        # add the path 
        N.append(P)
        return N 