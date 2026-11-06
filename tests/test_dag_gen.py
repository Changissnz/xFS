from graph_models.dag_gen import * 
import unittest

def DAGraphGen__sample_QSTD(gen_scheme,num_node_range_per_layer,\
    multiparent_pr_range,intralayer_conn_range,uniform_depth): 

    prg = prg__LCG(6235.54,-6234,3252.6346,547632.1) 

    dagg = DAGraphGen(num_node_range_per_layer,gen_scheme,multiparent_pr_range,\
        intralayer_conn_range,prg,uniform_depth)
    return dagg,prg 

"""
py -m tests.test_dag_gen
"""
class DAGraphGenClass(unittest.TestCase): 

    """
    demonstrates proper child/parent connectivity for case 
    of: 
    - gen. scheme = "constant", 
    - multi-parent connectivity in range [0.,0.2],
    - intralayer conn. range in range [0.1,0.2],
    - uniform_depth = True.
    """
    def test__DAGraphGen__next__case_1(self): 

        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.,0.2],\
            intralayer_conn_range = [0.1,0.2],uniform_depth = True)

        next(dagg) 
        assert len(dagg.intralayer_edges(dagg.level-1)) > 0
        next(dagg) 

        for _ in range(10): 
            if len(dagg.l2n_map[dagg.level -1]) > 1: 
                assert len(dagg.intralayer_edges(dagg.level-1)) > 0

            l = dagg.level - 1 
            nodes_l1 = dagg.l2n_map[l] 

            for n in nodes_l1: 
                parents = dagg.parents_of_node(n) 
                assert len(parents) >= 1 

            nodes_l0 = dagg.l2n_map[l-1] 
            for n in nodes_l0: 
                children = dagg.children_of_node(n) 
                assert len(children) >= 1 

            next(dagg) 

        assert len(dagg.G) == 82, "got {}".format(len(dagg.G))
        assert dagg.level == 12 

        return 

    '''
    demonstrates proper child/parent connectivity for case 
    of: 
    - identical to case #1 except for multiparent_pr_range set 
      to [0.,0.8] and uniform_depth set to False. 
    '''
    def test__DAGraphGen__next__case_2(self):
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.0,0.8],\
            intralayer_conn_range = [0.1,0.2],uniform_depth = False)

        next(dagg) 
        assert len(dagg.intralayer_edges(dagg.level-1)) > 0
        next(dagg) 

        parent_count_freq = defaultdict(int) 
        children_count_freq = defaultdict(int) 

        for _ in range(10): 
            assert len(dagg.intralayer_edges(dagg.level-1)) > 0

            l = dagg.level - 1 
            nodes_l1 = dagg.l2n_map[l] 

            for n in nodes_l1: 
                parents = dagg.parents_of_node(n) 
                parent_count_freq[len(parents)] += 1 

            nodes_l0 = dagg.l2n_map[l-1] 
            for n in nodes_l0: 
                children = dagg.children_of_node(n) 
                children_count_freq[len(children)] += 1 

            next(dagg) 
        assert len(dagg.G) == 83, "got {}".format(len(dagg.G))

        assert parent_count_freq == defaultdict(int, {1: 28, 3: 13, 2: 19, 4: 5, 5: 4}),\
            "got {}".format(parent_count_freq)

        assert children_count_freq ==  defaultdict(int, \
            {7: 2, 0: 32, 1: 3, 4: 11, 3: 12, 8: 1, 5: 4, 6: 3, 2: 1}),\
            "got {}".format(children_count_freq)

        return 

    '''
    demonstrates proper child/parent connectivity for case 
    of: 
    - gen. scheme = "mult",
    - no multiple parents,
    - no intra-layer connections,
    - uniform depth = True.
    '''
    def test__DAGraphGen__next__case_3(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="mult",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.0,0.0],\
            intralayer_conn_range = [0.0,0.0],uniform_depth = True)

        next(dagg) 
        assert len(dagg.intralayer_edges(dagg.level-1)) == 0 
        next(dagg) 

        for _ in range(5): 
            next(dagg) 
            print("{}".format(_))
        assert len(dagg.G) == 783463, "got {}".format(len(dagg.G))

        l3 = dagg.l2n_map[3] 
        d = defaultdict(int) 

        for n in l3: 
            lp = len(dagg.parents_of_node(n)) 
            d[lp] += 1 

        assert d == {1:1966}

        I = dagg.intralayer_edges(3) 
        assert len(I) == 0 

    def test__DAGraphContainer__n_paths_with_node__case_1(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.5,1.0],\
            intralayer_conn_range = [0.1,0.35],uniform_depth = True)

        next(dagg) 
        next(dagg) 

        for _ in range(15): 
            next(dagg) 
            print("{}".format(_))

        assert len(dagg.G) == 98, "got {}".format(len(dagg.G))

        target_node = 95 
        num_paths = 12
        proper_paths_only = True 
        P = dagg.n_paths_with_node(target_node,num_paths,proper_paths_only,dagg.prg)

        # check for uniqueness 
        P_ = set() 
        for p in P: 
            P_ |= {str(p)}
        assert len(P_) == num_paths, "got {}\t\t".format(len(P_))

        for p in P: 
            l = p.p 
            assert target_node in l 
            assert does_path_exist(dagg.G,l) 

    def test__DAGraphGen__n_paths_with_node__case_2(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
        num_node_range_per_layer = [2,4],\
        multiparent_pr_range = [0.05,0.15],\
        intralayer_conn_range = [0.0,0.4],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        Q = dagg.n_paths_with_node(19,10,True,dagg.prg)
        Q2 = dagg.n_paths_with_node(19,10,False,dagg.prg) 

        L = [len(q) for q in Q] 
        L2 = [len(q) for q in Q2] 

        assert L == [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        assert L2 == [13, 13, 13, 14, 14, 14, 12, 12, 12, 12], "got {}".format(L2)

    """
    NOTE: verification is relatively long process. 
    """
    def test__DAGraphContainer__verify__case_1(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="mult",\
        num_node_range_per_layer = [2,4],\
        multiparent_pr_range = [0.05,0.1],\
        intralayer_conn_range = [0.01,0.3],uniform_depth = True)

        next(dagg) 
        next(dagg) 

        for _ in range(5): 
            next(dagg) 
            print("{}".format(_))

        # check that verification works for good info., over 10 rounds 
        l2n_map = deepcopy(dagg.l2n_map) 
        G2 = deepcopy(dagg.G)

        for _ in range(10): 
            C = DAGraphContainer(G2,l2n_map,True) 
            assert type(C.erroneous_node) == type(None) 

        G2 = deepcopy(dagg.G)
        G3 = deepcopy(dagg.G)

        # mismatch node 22 
        l2n_map = deepcopy(dagg.l2n_map) 
        l2n_map[2] -= {22} 
        l2n_map[1] |= {22} 
        C = DAGraphContainer(G2,l2n_map,True)  
        assert C.erroneous_node == 22, "got {}".format(C.erroneous_node)

        # mismatch node 9 
        l2n_map = deepcopy(dagg.l2n_map) 
        l2n_map[1] -= {9} 
        l2n_map[3] |= {9} 
        C = DAGraphContainer(G3,l2n_map,True)  
        assert C.erroneous_node == 9, "got {}".format(C.erroneous_node)

    """
    demonstrates an erroneous DAG (layer 0 is circular)
    """
    def test__DAGraphContainer__intrasets_of_layer__case_1(self): 
        Gx = defaultdict(set, {83: {1, 50, 3}, 64: {80, 50, 3, 87}, \
            2: {50, 83, 30}, 87: {1, 43, 79, 80, 56, 30}, 41: {3, 43, 45, 87}, \
            56: {64, 2, 43, 49, 50}, 49: {64, 1, 3}, 82: {3, 50, 43, 30}, \
            32: {1, 3, 45, 50, 30}, 80: {2, 41, 43, 50, 30}, 30: {35, 43, 51, 54, 28}, \
            1: {77, 45, 17, 51, 54}, 50: {46, 17, 77, 54}, \
            43: {1, 35, 77, 17, 50, 28}, 45: {3, 43, 35, 54}, 3: {43, 77, 46}, \
            79: {45, 50, 35, 77}, 51: set(), 35: set(), 17: {77}, 54: set(), \
            77: set(), 28: {35}, 46: {51}})

        l2n_map = {0: {64, 32, 2, 41, 80, 49, 82, 83, 87, 56}, \
            1: {1, 50, 3, 43, 45, 30, 79}, 2: {17, 35, 51, 54, 28, 77, 46}}

        try: 
            C = DAGraphContainer(Gx,l2n_map,True) 
            assert False 
        except: 
            assert True 

    def test__DAGraphContainer__permute_nodes__case_1(self):
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
        num_node_range_per_layer = [2,4],\
        multiparent_pr_range = [0.05,0.15],\
        intralayer_conn_range = [0.0,0.0],uniform_depth = True)

        for _ in range(5): 
            next(dagg) 

        leaf_nodes = deepcopy(dagg.leaf_nodes)

        G_ = deepcopy(dagg.G)
        dagg.permute_nodes() 

        leaf_nodes2 = deepcopy(dagg.leaf_nodes)

        assert leaf_nodes == [11, 12, 13]
        assert leaf_nodes2 == [1, 6, 8]

        proper_paths_only = True 
        for k in dagg.G.keys(): 
            P = dagg.n_paths_with_node(k,1,proper_paths_only,dagg.prg)[0] 
            level = P.p.index(k)    
            assert k in dagg.l2n_map[level] 

    def test__DAGraphContainer__children_of_node__case_1(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [7,16],\
            multiparent_pr_range = [0.05,0.15],\
            intralayer_conn_range = [0.4,0.8],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        assert dagg.intrasets_of_layer(0) == \
            [{0}, {1}, {2}, {2, 3, 12}, {9, 3, 4}, {5}, {2, 6}, {7}, {8, 7}, {10}, {11}, {13}]

        s5_1 = dagg.siblings_of_node(5,True)
        assert s5_1.issubset(dagg.children_of_node(5,False)) 
        s5_0 = dagg.siblings_of_node(5,False)
        assert s5_0.issubset(dagg.parents_of_node(5,False)) 
        assert s5_1 == s5_0 == set() 

        s7_1 = dagg.siblings_of_node(7,True)
        assert s7_1.issubset(dagg.parents_of_node(7,False))
        assert s7_1 == {8} 

        s12_1 = dagg.siblings_of_node(12,True)
        assert s12_1.issubset(dagg.parents_of_node(12,False))
        assert s12_1 == {3} 

        s12_0 = dagg.siblings_of_node(12,False)
        assert s12_0.issubset(dagg.children_of_node(12,False)) 
        assert s12_0 == {2}  
        
    """
    the DAG is the same as that from 
        <test__DAGraphContainer__children_of_node__case_1>. 
    """
    def test__DAGraphContainer__intralayer_node2node_path__case_1(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [7,16],\
            multiparent_pr_range = [0.05,0.15],\
            intralayer_conn_range = [0.4,0.8],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        P0_1 = dagg.intralayer_node2node_path(0,1)
        assert type(P0_1) == type(None) 

        P3_12 = dagg.intralayer_node2node_path(3,12)
        assert type(P3_12) == NodePath 
        assert {3,12}.issubset(set(P3_12.p)) 
        assert does_path_exist(dagg.G,P3_12.p)

        P12_3 = dagg.intralayer_node2node_path(12,3)
        assert type(P12_3) == NodePath 
        assert {3,12}.issubset(set(P12_3.p)) 
        assert does_path_exist(dagg.G,P12_3.p)

        P3_4 = dagg.intralayer_node2node_path(3,4)
        assert type(P3_4) == NodePath 
        assert {3,4}.issubset(set(P3_4.p)) 
        assert does_path_exist(dagg.G,P3_4.p)

        P4_3 = dagg.intralayer_node2node_path(4,3)
        assert type(P4_3) == NodePath 
        assert {3,4}.issubset(set(P4_3.p)) 
        assert does_path_exist(dagg.G,P4_3.p)

        P7_10 = dagg.intralayer_node2node_path(7,10)
        assert type(P7_10) != NodePath 

        P10_7 = dagg.intralayer_node2node_path(10,7)
        assert type(P10_7) != NodePath 

    """
    the DAG is the same as that from 
        <test__DAGraphContainer__children_of_node__case_1>. 
    """
    def test__DAGraphContainer__intralayer_nodeset_path__case_1(self): 
        dagg,_ = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [7,16],\
            multiparent_pr_range = [0.05,0.15],\
            intralayer_conn_range = [0.4,0.8],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        assert dagg.intrasets_of_layer(0) == \
            [{0}, {1}, {2}, {2, 3, 12}, {9, 3, 4}, {5}, {2, 6}, {7}, {8, 7}, {10}, {11}, {13}]

        S0 = {2,3,12,4,9} 
        P_S0 = dagg.intralayer_nodeset_path(S0) 
        assert type(P_S0) == type(None)

        S1 = {2,3,12} 
        P_S1 = dagg.intralayer_nodeset_path(S1) 
        assert S1.issubset(set(P_S1.p))
        assert does_path_exist(dagg.G,P_S1.p)

        S2 = {3,4,9} 
        P_S2 = dagg.intralayer_nodeset_path(S2) 
        assert S2.issubset(set(P_S2.p))
        assert does_path_exist(dagg.G,P_S2.p)

    def test__DAGraphContainer__n_paths_with_intra_nodeset__case_1(self): 

        dagg,prg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [7,16],\
            multiparent_pr_range = [0.05,0.15],\
            intralayer_conn_range = [0.4,0.8],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        N0 = {2,3}
        X = dagg.n_paths_with_intra_nodeset(N0,5) 
        assert len(X) == 5 

        N1 = {33, 34, 35, 29, 30}
        X1 = dagg.n_paths_with_intra_nodeset(N1,5) 
        assert len(X1) == 5 

        N2 = {33, 34, 35, 29, 30,31}
        X2 = dagg.n_paths_with_intra_nodeset(N2,5) 
        assert len(X2) == 0 

    def test__DAGraphContainer__n_paths_with_nodeset__case_1(self): 
        dagg,prg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [7,16],\
            multiparent_pr_range = [0.05,0.15],\
            intralayer_conn_range = [0.4,0.8],uniform_depth = True)

        for _ in range(10): 
            next(dagg) 

        # subcase 1 
        N0 = {2,3}
        X = dagg.n_paths_with_nodeset(N0,5)
        assert len(X) == 5 
        for x in X: 
            assert N0.issubset(set(x.p))
        assert not dagg.trav_error

        # subcase 2 
        N1 = {2,3,17,14,21,44,48,50,45}
        X2 = dagg.n_paths_with_nodeset(N1,5)
        assert len(X) == 5 
        for x in X2: 
            assert N1.issubset(set(x.p))
        assert not dagg.trav_error

        # subcase 2.1 
        X2_ = dagg.n_paths_with_nodeset(N1,5,False)
        assert len(X2_) == 5 
        dcount = 0 
        for (i,x) in enumerate(X2_): 
            assert N1.issubset(set(x.p))
            p2 = X2[i]
            if p2 != x: 
                dcount += 1  
        assert X2 != X2_ 
        assert not dagg.trav_error

        # subcase 2.2: consistency -> equal to subcase 2
        X2__ = dagg.n_paths_with_nodeset(N1,5)
        assert len(X2__) == 5 
        for (x,x2) in zip(X2,X2__): 
            assert x == x2 
        assert not dagg.trav_error

        # subcase 2: different paths using PRNG 
        X2___ = dagg.n_paths_with_nodeset(N1,5,prg=prg)
        assert len(X2___) == 5 
        for (x,x2) in zip(X2,X2___): 
            assert x != x2 
        assert not dagg.trav_error

        # subcase 3: no paths have that nodeset 
        X3 = dagg.n_paths_with_nodeset({15,16,48,50},5) 
        assert X3 == [] 
        assert dagg.trav_error


if __name__ == '__main__':
    unittest.main()
