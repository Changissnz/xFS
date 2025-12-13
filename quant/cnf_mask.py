from graph_models.node_path import * 
from .bool_rules import * 
from types import MethodType,FunctionType
from morebs2.graph_basics import is_undirected_graph
from morebs2.numerical_generator import prg_choose_n,default_std_Python_prng

# TODO: test this. 
"""
Given an undirected graph `G` and a path `npath` found in it, masking procedure produces a 
subgraph that contains `npath` according to specifications set by `prior_connectivity` 
and `prior_potential`. 

In this algorithm, the starting neighbor set of n in `G` is the set of nodes connected 
to n minus the set of nodes comprising `npath`. 

These starting neighbor set is reduced in size to satisfy the parameters of class instance. 

In masking algorithm, there are two classes of connectivities.
The first class applies when `prior_connectivity`= None. The 
variable of `prior_connectivity` applies to the selection of neighbor sets for 
each node in `npath`. 
    1 -> a node q_i is included in a neighbor set N_i of node n_i in `npath` if 
        q_i is connected to n_{i+1}.  
    2 -> a node q_i is included in a neighbor set N_i of node n_i in `npath` if 
        for the neighbor set N_{i+1}, 
            ceil(`prior_connectivity * |N_{i+1}|`)
        of those nodes of N_{i_1} are connected to q_i. 
"""
class CNFGraphMask:

    def __init__(self,npath:NodePath,G:defaultdict,\
        prior_connectivity:float,prior_potential:float,conn_type:int,prng=None):

        assert type(npath) == NodePath
        assert type(G) == defaultdict 
        assert is_undirected_graph(G)  

        if type(prior_connectivity) == type(None): 
            self.conn_type = 1
        else: 
            assert type(prior_connectivity) == float 
            assert 0 <= prior_connectivity <= 1.0
            self.conn_type = 2 

        assert float == type(prior_potential)
        assert 0 < prior_potential <= 1.0
        assert type(prng) in {MethodType,FunctionType,type(None)} 

        if type(prng) == type(None): 
            prng = default_std_Python_prng()

        for n in npath: 
            assert n in G 

        self.npath = npath 
        self.G = G 
        self.G_ = defaultdict(set) 
        self.pconn = prior_connectivity
        self.ppotential = prior_potential
        self.prng = prng 

        self.neighbor_sets = [] 
        return  

    def mask(self): 
        self.connect_phase_1() 
        self.connect_phase_2() 

    def connect_phase_1(self): 
        self.neighbor_sets.clear() 
        for n in self.npath: 
            ns = self.neighbor_set_for_node(n) 
            self.neighbor_sets.append(ns) 

        for i in range(len(self.neighbor_sets)-1,0,-1): 
            self.connectivity_filter(i) 
        return

    def connect_phase_2(self): 
        for (i,x) in enumerate(self.neighbor_sets): 
            X = sorted(x) 
            n = ceil(self.ppotential * len(X))
            X_ = prg_choose_n(X,n,self.prng,is_unique_picker=True)
            self.neighbor_sets[i] = set(X_) 
        return

    def neighbor_set_for_node(self,n): 
        return self.G[n] - set(self.npath.p) 

    """
    backward filter 
    """
    def connectivity_filter(self,neighborset_index): 
        assert 0 < neighborset_index < len(self.neighbor_sets)

        new_neighborset = [] 
        for prior_node in self.neighbor_sets[neighborset_index-1]: 
            stat = self.connectivity_filter_(prior_node,neighborset_index)
            if stat: 
                new_neighborset.append(prior_node) 
        new_neighborset = set(new_neighborset) 
        self.neighbor_sets[neighborset_index-1] = new_neighborset
        return

    """
    return: 
    - bool, ?accept in neighbor set? 
    """
    def connectivity_filter_(self,prior_node,neighborset_index): 
        ##assert 0 < neighborset_index < len(self.neighbor_sets)

        if self.conn_type == 1: 
            n = self.npath[neighborset_index]    
            return n in self.G[prior_node] 
         
        Q = {self.npath[neighborset_index]} | self.neighbor_sets[neighborset_index]
        c = 0 
        for q in Q: 
            c += int(q in self.G[prior_node]) 
        return c / len(Q) >= self.pconn

    def to_subgraph(self): 
        # collect all nodes 
        sq = [] 
        for i in range(len(self.npath)): 
            sq.append(self.npath[i]) 
            sq.extend(self.neighbor_sets[i]) 

        mg = MicroGraph(self.G)
        mg2 = mg.subgraph_by_nodeset_(sq) 
        return mg2.dg

    def to_cnf_expression(self):

        for i in range(len(self.npath)): 
            ex = self.to_cnf_expression_(i)
            ex = " + " 
        ex = ex[:-3] 
        return ex

    def to_cnf_expression_(self,i): 
        rx = self.neighbor_sets[i] 
        rx = sorted([str(self.npath[i])] + [str(rx_) for rx_ in rx]) 
        qx = "|".join(rx) 
        return "(" + qx + ")"
