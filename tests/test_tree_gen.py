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

    """
    demonstrates difference in two types of tree generation: ordered,distributed. 
    """
    def test__TreeGen__generate_tree__mroot_n_leaves__case_1(self): 

        # subcase 1 
        starting_nodeset = {1} 
        num_leaves = 40 
        prg = prg__LCG(-781.34,-566.7,7.79,-91996.2)

        T = TreeGen.generate_tree__mroot_n_leaves(starting_nodeset,num_leaves,prg,is_dsg=False,growth_type="distributed") 

        assert len(T.d) == 52 
        assert len(T.leaves) == num_leaves 
        assert T.d == defaultdict(set,\
                {1: {2, 3, 4}, \
                2: {1, 17, 18, 19, 20, 21, 22, 23, 24}, \
                3: {1, 5, 6, 7, 8, 9, 10}, \
                4: {1, 37, 38, 39, 40, 41, 42}, \
                5: {3}, 6: {3, 11, 12, 13, 14}, \
                7: {3, 46, 47, 48, 49, 50, 51, 52}, \
                8: {3}, 9: {16, 3, 15}, 10: {3}, \
                11: {6}, 12: {6}, 13: {6}, 14: {6}, \
                16: {9}, 15: {32, 33, 34, 35, 36, 9, 29, 30, 31}, \
                17: {2, 45}, 18: {2}, 19: {2, 28}, \
                20: {2}, 21: {2}, 22: {2}, 23: {27, 25, 2, 26}, \
                24: {2}, 25: {23}, 26: {23}, 27: {23}, 28: {19}, \
                32: {15}, 33: {15}, 34: {15}, 35: {15}, 36: {15}, \
                29: {15}, 30: {15}, 31: {43, 44, 15}, 37: {4}, \
                38: {4}, 39: {4}, 40: {4}, 41: {4}, 42: {4}, \
                43: {31}, 44: {31}, 45: {17}, 46: {7}, 47: {7}, \
                48: {7}, 49: {7}, 50: {7}, 51: {7}, 52: {7}})  

        # subcase 2 
        starting_nodeset2 = {0,1,2} 
        num_leaves2 = 35 
        T2 = TreeGen.generate_tree__mroot_n_leaves(starting_nodeset2,num_leaves2,prg,is_dsg=False,growth_type="distributed") 

        assert len(T2.leaves) == num_leaves2
        assert len(T2.d) == 49
        assert T2.d == defaultdict(set, \
            {0: {3}, 1: {40, 41}, \
            2: {16, 11, 12, 13, 14, 15}, \
            3: {0, 4, 5, 6}, 4: {8, 9, 3, 7}, \
            5: {17, 3}, 6: {18, 3, 19, 20, 21, 22}, \
            8: {10, 4}, 9: {4}, 7: {4}, \
            10: {32, 33, 34, 35, 36, 37, 38, 39, 8}, \
            11: {2}, 12: {2, 23, 24, 25, 26, 27, 28, 29, 30, 31}, \
            13: {2}, 14: {2}, 15: {2}, 16: {2}, 17: {5}, \
            18: {6}, 19: {48, 6, 47}, 20: {6}, 21: {6}, \
            22: {6}, 23: {12}, 24: {12}, 25: {12}, 26: {12}, \
            27: {12}, 28: {42, 43, 12}, 29: {12}, 30: {12}, \
            31: {12}, 32: {10}, 33: {10}, 34: {10}, 35: {10, 46}, \
            36: {10}, 37: {10}, 38: {10}, 39: {10}, 40: {1}, \
            41: {1, 44, 45}, 42: {28}, 43: {28}, 44: {41}, \
            45: {41}, 46: {35}, 48: {19}, 47: {19}})

        # subcase 3 
        T3 = TreeGen.generate_tree__mroot_n_leaves(starting_nodeset2,num_leaves2,prg,is_dsg=False,growth_type="ordered") 

        assert len(T3.leaves) == num_leaves2
        assert len(T3.d) == 42
        assert T3.d == defaultdict(set, \
            {0: {3, 4, 5, 6, 7}, \
            1: {12, 13, 14, 15, 16, 17, 18, 19, 20}, \
            2: {8, 9, 10, 11}, 3: {0, 33, 34, 35, 36, 37, 38}, \
            4: {0}, 5: {0, 21, 22, 23, 24}, \
            6: {0, 32, 25, 26, 27, 28, 29, 30, 31}, \
            7: {0, 41, 40, 39}, 8: {2}, 9: {2}, 10: {2}, \
            11: {2}, 12: {1}, 13: {1}, 14: {1}, 15: {1}, \
            16: {1}, 17: {1}, 18: {1}, 19: {1}, 20: {1}, \
            24: {5}, 21: {5}, 22: {5}, 23: {5}, 32: {6}, \
            25: {6}, 26: {6}, 27: {6}, 28: {6}, 29: {6}, \
            30: {6}, 31: {6}, 33: {3}, 34: {3}, 35: {3}, \
            36: {3}, 37: {3}, 38: {3}, 40: {7}, 41: {7}, \
            39: {7}})

        # subcase 4 
        branching_range = [1,2] 
        T4 = TreeGen.generate_tree__mroot_n_leaves(starting_nodeset2,num_leaves2,prg,\
            is_dsg=False,growth_type="ordered",branching_range=branching_range) 

        assert len(T4.d) == 65 
        assert T4.d == defaultdict(set, \
            {0: {7}, 1: {3}, 2: {4, 5, 6}, \
            3: {8, 1, 9}, 4: {11, 2, 10, 12}, \
            5: {2, 13, 14, 15}, 6: {16, 17, 2, 18}, \
            7: {0, 19, 20}, 8: {3, 21, 22}, \
            9: {24, 3, 23}, 10: {4, 30}, \
            11: {25, 26, 27, 4}, 12: {29, 4, 28}, \
            13: {32, 33, 5, 31}, 14: {37, 5}, \
            15: {34, 35, 36, 5}, 16: {43, 44, 6}, \
            17: {40, 38, 6, 39}, 18: {41, 42, 6}, \
            19: {46, 7}, 20: {45, 7}, 21: {8, 49}, \
            22: {8, 48, 47}, 24: {9, 50, 51}, \
            23: {9, 52, 53, 54}, 25: {11, 55}, \
            26: {56, 11}, 27: {57, 58, 11, 59}, \
            28: {64, 12, 63}, 29: {62, 12, 61, 60}, \
            30: {10}, 32: {13}, 33: {13}, 31: {13}, \
            34: {15}, 35: {15}, 36: {15}, 37: {14}, \
            40: {17}, 38: {17}, 39: {17}, 41: {18}, \
            42: {18}, 43: {16}, 44: {16}, 45: {20}, \
            46: {19}, 48: {22}, 47: {22}, 49: {21}, \
            50: {24}, 51: {24}, 52: {23}, 53: {23}, \
            54: {23}, 55: {25}, 56: {26}, 57: {27}, \
            58: {27}, 59: {27}, 60: {29}, 61: {29}, \
            62: {29}, 64: {28}, 63: {28}})

    def test__TreeGen__delete_n_nodes__case_1(self): 

        prg = prg__LCG(44.5,-99.8,-7777,9015)

        tg = TreeGen(starting_nodeset = {0},is_dsg=False,prg=prg,branching_range=DEFAULT_TREE_BRANCHING_RANGE,\
                growth_type="ordered")

        r = 100 

        while tg.node_count < r: 
            next(tg) 

        next(tg),next(tg),next(tg)  
        assert tg.node_count == 111 

        l_ = deepcopy(tg.leaves) 
        tg.delete_n_nodes(11) 
        l = tg.leaves
        assert tg.node_count == len(tg.d) == 100 
        
        assert len(l_) == 83 
        assert len(l) == 72 

if __name__ == '__main__':
    unittest.main()