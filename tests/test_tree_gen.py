from morebs2.graph_basics import * 
from morebs2.numerical_generator import prg__LCG 
from graph_models.tree_gen import * 
import unittest

### lone file test 
"""
py -m tests.test_tree_gen
"""
###
class TreeGenClass(unittest.TestCase):

    def test__TreeGen__next__case_1(self):
        # case 1 
        prg = prg__LCG(87,354,675456,9999) 
        tg = TreeGen(starting_nodeset = {0},is_dsg=True,prg=prg,branching_range=DEFAULT_TREE_BRANCHING_RANGE)

        next(tg) 
        assert tg.d == defaultdict(set, {0: {1, 2, 3, 4}})

        next(tg)
        assert tg.d == defaultdict(set, {0: {1, 2, 3, 4}, 4: {5, 6, 7, 8, 9}})

        assert tg.leaves == [1, 2, 3, 5, 6, 7, 8, 9]

        for _ in range(10): 
            next(tg) 

        ans_leaves = [1, 2, 3, 5, 7, 10, 13, 16, 17, 18, 19, 20, 21,\
            22, 23, 24, 25, 27, 28, 29, 32, 30, 34, 35, 36, 37, 38, \
            39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
        assert tg.leaves == ans_leaves 
        return

    def test__TreeGen__next__case_2(self):
        prg2 = prg__LCG(8711,754,-675456,9999) 
        tg2 = TreeGen(starting_nodeset = {0,1,2},is_dsg=False,prg=prg2,branching_range=DEFAULT_TREE_BRANCHING_RANGE)
        next(tg2) 
        assert tg2.d == defaultdict(set, \
            {0: set(), 1: set(), 2: {3}, 3: {2}})

        for _ in range(10): 
            next(tg2) 

        assert is_undirected_graph(tg2.d) 

        gc = GraphComponentDecomposition(tg2.d)
        gc.decompose()
        assert len(gc.components) == 3 


if __name__ == '__main__':
    unittest.main()