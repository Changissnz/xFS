from graph_models.dag_gen import * 
import unittest

def DAGraphGen__sample_QSTD(gen_scheme,num_node_range_per_layer,\
    multiparent_pr_range,intralayer_conn_range,uniform_depth): 

    prg = prg__LCG(6235.54,-6234,3252.6346,547632.1) 

    dagg = DAGraphGen(num_node_range_per_layer,gen_scheme,multiparent_pr_range,\
        intralayer_conn_range,prg,uniform_depth)
    return dagg 

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

        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.,0.2],\
            intralayer_conn_range = [0.1,0.2],uniform_depth = True)

        next(dagg) 
        assert len(dagg.intralayer_edges(dagg.level-1)) > 0
        next(dagg) 

        for _ in range(10): 
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

        assert len(dagg.G) == 76, "got {}".format(len(dagg.G))
        assert dagg.level == 12 

        return 

    '''
    demonstrates proper child/parent connectivity for case 
    of: 
    - identical to case #1 except for multiparent_pr_range set 
      to [0.,0.8] and uniform_depth set to False. 
    '''
    def test__DAGraphGen__next__case_2(self):
        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
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
        assert len(dagg.G) == 77, "got {}".format(len(dagg.G))

        assert parent_count_freq == defaultdict(int, {1: 33, 4: 5, 5: 1, 2: 15, 3: 10}),\
            "got {}".format(parent_count_freq)
        assert children_count_freq == defaultdict(int, {7: 1, 0: 26, 4: 5, 3: 10, \
            5: 3, 6: 3, 2: 8, 1: 4, 8: 1}),\
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
        dagg = DAGraphGen__sample_QSTD(gen_scheme="mult",\
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
        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
            num_node_range_per_layer = [5,10],\
            multiparent_pr_range = [0.5,1.0],\
            intralayer_conn_range = [0.1,0.35],uniform_depth = True)

        next(dagg) 
        next(dagg) 

        for _ in range(15): 
            next(dagg) 
            print("{}".format(_))

        assert len(dagg.G) == 125, "got {}".format(len(dagg.G))

        target_node = 110 
        num_paths = 12
        proper_paths_only = True 
        P = dagg.n_paths_with_node(target_node,num_paths,proper_paths_only,dagg.prg)

        # check for uniqueness 
        P_ = set() 
        for p in P: 
            P_ |= {str(p)}
        assert len(P_) == num_paths 

        for p in P: 
            l = p.p 
            assert target_node in l 
            assert does_path_exist(dagg.G,l) 

    def test__DAGraphGen__n_paths_with_node__case_2(self): 
        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
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
        assert L2 == [12, 14, 13, 13, 13, 15, 12, 14, 17, 15]

    """
    NOTE: verification is relatively long process. 
    """
    def test__DAGraphContainer__verify__case_1(self): 
        dagg = DAGraphGen__sample_QSTD(gen_scheme="mult",\
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
        assert C.erroneous_node == 22 

        # mismatch node 9 
        l2n_map = deepcopy(dagg.l2n_map) 
        l2n_map[1] -= {9} 
        l2n_map[3] |= {9} 
        C = DAGraphContainer(G3,l2n_map,True)  
        assert C.erroneous_node == 4  

    def test__DAGraphContainer__permute_nodes__case_1(self):
        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
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

        

if __name__ == '__main__':
    unittest.main()
