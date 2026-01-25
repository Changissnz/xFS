from graph_problems.ptb import *
import time 
import unittest

def PTBot_sample_X(num_source_nodes,num_targets,num_poisons,relays_per_source,poison_matrix_square_dim=4): 
    poison2source_ratio_range = [1.,1.] 
    expressive_mode = False   
    prg = prg__LCG(56.54,-100.32,455.3,197.55)

    seed_pair = (34,34)
    relay_accuracy_range = [0.75,0.9]
    pdn = PTBot.generate_instance(num_source_nodes,num_targets,\
        num_poisons,poison2source_ratio_range,poison_matrix_square_dim,\
        expressive_mode,prg,seed_pair,relays_per_source=relays_per_source,verbose=False)

    prg2 = prg__LCG(-456.54,-32.32,1455.3,-3197.55)
    prngs = prg_to_prg__LCG_sequence(prg2,10,4.02) 
    prng_map = {}
    for i,k in enumerate(pdn.target_map.keys()): 
        prng_map[k] = prngs[i] 
    pdn.set_target_prngs(prng_map) 
    return pdn 

### lone file test 
"""
py -m tests.test_ptb  
"""
###
class PTBotClass(unittest.TestCase):

    """
    1 minute <= developer runtime <= 2 minutes 
    """
    def test__PTBot__next__case_1(self): 
        num_source_nodes = 10
        num_targets = 10
        num_poisons = 5
        relays_per_source = 2 
        pb = PTBot_sample_X(num_source_nodes,num_targets,num_poisons,relays_per_source)

        t = time.time() 
        for i in range(5000): 
            #print("ITER {}".format(i)) 
            #print("================================================")
            next(pb) 
            if i % 1000 == 0: 
                print("iter {}".format(i)) 

        print("case #1 runtime: ",time.time() - t)
        # (number of terminations, number of guesses, number of poisonings) 
        pb_target_measures = {0: (188, 37865, 327), 1: (180, 37790, 335), \
            2: (185, 38644, 324), 3: (190, 38600, 332), 4: (174, 38667, 326), \
            5: (188, 38513, 327), 6: (191, 38863, 329), 7: (195, 38866, 325), \
            8: (185, 37824, 340), 9: (176, 37677, 333)}

        '''
        {0: (195, 38464, 310), 1: (182, 37940, 332), \
            2: (191, 38447, 330), 3: (172, 38493, 334), 4: (182, 38344, 334), \
            5: (186, 38387, 335), 6: (200, 39299, 316), 7: (185, 38646, 327), \
            8: (182, 37459, 345), 9: (174, 37335, 340)}
        '''
        ###
        '''
        {0: (183, 37382, 333), 1: (186, 38687, 322), \
            2: (188, 38805, 321), 3: (186, 38717, 326), 4: (189, 38941, 321), \
            5: (185, 38736, 323), 6: (182, 38273, 336), 7: (188, 38516, 325), \
            8: (187, 37583, 324), 9: (171, 36980, 340)}
        '''

        got = pb.target_performances(False)
        assert got == pb_target_measures, "got {}".format(got)
        return 

    """
    developer runtime <= 30 seconds 

    target uses parameters of a lower scale (2 instead of 10 source nodes, 
    3 instead of 5 poisons) than in Case 1. 

    Ending target performance measures show the maximum mortality for a target 
    to be 6 = num_source_nodes * num_poisons = 2 * 3. 
    """
    def test__PTBot__next__case_2(self): 
        num_source_nodes = 2
        num_targets = 10
        num_poisons = 3
        relays_per_source = 2 

        pb = PTBot_sample_X(num_source_nodes,num_targets,num_poisons,relays_per_source)

        t = time.time() 
        for i in range(5000): 
            next(pb) 
            if i % 1000 == 0: 
                print("iter {}".format(i)) 

        print("case #2 runtime: ",time.time() - t)

        # (number of terminations, number of guesses, number of poisonings) 
        pb_target_measures = {5: (2, 2260, 143), 8: (6, 2518, 171), \
            9: (6, 2638, 181), 10: (5, 3018, 194), \
            11: (6, 2451, 168), 12: (4, 2905, 192), \
            13: (4, 2757, 168), 14: (4, 3010, 176), \
            15: (3, 3197, 182), 16: (5, 2183, 150)}

        got = pb.target_performances(False)
        assert got == pb_target_measures, "got {}".format(got)

    """
    1 minute <= developer runtime <= 2 minutes 

    all parameters for this test case are the same as that for Case 1, except for 
    matrix dimension 8 instead of 4. 

    The lower poison potency (lower matrix dimension is higher potency) of this test 
    case directly corresponds to an improvement in target mortality, demonstrated 
    by ending target performance measures. 
    """
    def test__PTBot__next__case_3(self): 
        num_source_nodes = 10
        num_targets = 10
        num_poisons = 5
        relays_per_source = 2 
        poison_matrix_square_dim = 8

        pb = PTBot_sample_X(num_source_nodes,num_targets,num_poisons,relays_per_source,poison_matrix_square_dim)
        
        t = time.time() 
        for i in range(5000): 
            next(pb) 
            if i % 1000 == 0: 
                print("iter {}".format(i)) 

        print("case #3 runtime: ",time.time() - t)

        # (number of terminations, number of guesses, number of poisonings) 
        pb_target_measures = {0: (11, 60890, 214), 1: (19, 53859, 210), \
            2: (13, 60661, 215), 3: (12, 56923, 240), 4: (15, 54892, 222), \
            5: (15, 54616, 222), 6: (13, 57826, 226), 7: (15, 54076, 223), \
            8: (14, 60865, 208), 9: (16, 51223, 223)}
        got = pb.target_performances(False)

        assert got == pb_target_measures, "got {}".format(got) 

    """
    1 minute <= developer runtime <= 2 minutes 
    """
    def test__PTBot__next__case_4(self): 
        num_source_nodes = 10
        num_targets = 10
        num_poisons = 5
        relays_per_source = 6 
        pb = PTBot_sample_X(num_source_nodes,num_targets,num_poisons,relays_per_source)

        t = time.time() 
        for i in range(5000): 
            #print("ITER {}".format(i)) 
            #print("================================================")
            next(pb) 
            if i % 1000 == 0: 
                print("iter {}".format(i)) 

        print("case #4 runtime: ",time.time() - t)
        # (number of terminations, number of guesses, number of poisonings) 
        pb_target_measures =  {0: (176, 37414, 333), 1: (185, 37902, 328), \
            2: (182, 38104, 331), 3: (192, 38533, 325), 4: (187, 38367, 334), \
            5: (193, 38860, 321), 6: (182, 39073, 324), 7: (183, 38266, 323), \
            8: (185, 37974, 323), 9: (184, 37213, 332)}

        got = pb.target_performances(False)
        assert got == pb_target_measures, "got {}".format(got)
        return 

if __name__ == '__main__':
    unittest.main()

# 2 relays 
# {0: (162, 37964, 350), 1: (154, 37361, 361), 2: (183, 38122, 345), 3: (185, 37967, 349), 4: (171, 37360, 353), 5: (177, 37655, 348), 6: (176, 38237, 351), 7: (172, 38447, 338), 8: (189, 38944, 340), 9: (182, 37748, 342)}

# 10 relays 
#{0: (179, 37547, 355), 1: (164, 37262, 354), 2: (172, 38350, 338), 3: (168, 37376, 354), 4: (171, 38193, 345), 5: (182, 38054, 330), 6: (164, 37248, 359), 7: (176, 38298, 343), 8: (176, 37935, 346), 9: (185, 38054, 340)}