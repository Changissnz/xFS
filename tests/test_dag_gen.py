from graph_models.dag_gen import * 
import unittest

def DAGraphGen__sample_QSTD(gen_scheme,multiparent_pr_range,intralayer_conn_range,uniform_depth): 

    num_node_range_per_layer = [5,10] 
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
    - uniform_depth = True 
    """
    def test__DAGraphGen__next__case_1(self): 

        dagg = DAGraphGen__sample_QSTD(gen_scheme="constant",\
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

        assert parent_count_freq == defaultdict(int, {1: 33, 4: 5, 5: 1, 2: 15, 3: 10}),\
            "got {}".format(parent_count_freq)
        assert children_count_freq == defaultdict(int, {7: 1, 0: 26, 4: 5, 3: 10, \
            5: 3, 6: 3, 2: 8, 1: 4, 8: 1}),\
            "got {}".format(children_count_freq)
        return 

if __name__ == '__main__':
    unittest.main()
