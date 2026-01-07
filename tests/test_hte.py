from graph_models.graph_gen import * 
from graph_problems.hte import * 
import time 
import unittest 

def count_success_in_increments(stat_vec,part_size): 

    x = int(len(stat_vec) / part_size)

    counts = [] 
    for i in range(part_size): 
        c = stat_vec[i* x:(i+1) * x].count(True) 
        counts.append(c) 
    return counts  

def HTEBot_sample_QWAS(D:defaultdict,threat_mobility_ratio):  
    num_entry_points = 8 
    num_objective_points = 8
    threat_ratio = 0.1  
    threat_nodes_include_entry_points = False  

    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 

    print("GENERATING <HTEBOT>")
    htes = HTESurface.generate_instance(D,num_entry_points,num_objective_points,\
        threat_ratio,threat_mobility_ratio,threat_nodes_include_entry_points,\
        prg)

    hteb = HTEBot(htes,None,navigator_remembers_past_encounters=False,verbose=False)
    return hteb 

### lone file test 
"""
py -m tests.test_hte
"""
###
class HTEBotClass(unittest.TestCase):

    '''
    runs 100 navigators, with <HTEBot> set to these parameters: 
    - navigator_remembers_past_encounters: False 
    - navigator_uses_isomorphic_prediction: True 
    - memory_less navigator: False  
    - `contra_risk`: 0.5 
    '''
    def test__HTEBot__run_navigator__case_1(self): 
        print("\t\tCASE 1")
        D = generated_graph_sample_1000()
        threat_mobility_ratio = 0.75 
        hteb = HTEBot_sample_QWAS(D,threat_mobility_ratio) 

        t = time.time()

        stats,P = HTEBot.run_n_navigators(hteb,100,1,True)
        S = count_success_in_increments(stats,10) 
        assert sum(S) == 49 
        assert S == [4, 3, 5, 2, 5, 3, 5, 8, 5, 9]
        assert (hteb.bot_mode() == np.array([0. , 1. , 0. , 0.5])).all() 
        print("total runtime: ",time.time() - t) 

    '''
    runs 100 navigators, with <HTEBot> set to these parameters: 
    - navigator_remembers_past_encounters: True (no difference) 
    - navigator_uses_isomorphic_prediction: True (no difference)
    - memory_less navigator: True (makes difference)
    - `contra_risk`: 0.0 (makes difference)
    '''
    def test__HTEBot__run_navigator__case_2(self): 
        print("\t\tCASE 2")
        D = generated_graph_sample_1000() 
        threat_mobility_ratio = 0.75 
        hteb = HTEBot_sample_QWAS(D,threat_mobility_ratio) 
        bmode = np.array([1. , 1. , 1. , 0.0])
        hteb.set_bot_mode(bmode)

        t = time.time() 
        stats,P = HTEBot.run_n_navigators(hteb,50,1,True)
        print("total runtime: ",time.time() - t) 
        S = count_success_in_increments(stats,10) 
        assert sum(S) == 12 
        assert S == [1, 1, 1, 2, 2, 1, 0, 2, 1, 1]
        assert (hteb.bot_mode() == np.array([1., 1., 1., 0.])).all()

    """
    demonstrates a case where navigator variable `memory_less` set to 
    True performs worse than it set to False. 
    """
    def test__HTEBot__run_navigator__case_3(self):
        print("\t\tCASE 3")
        D = generated_graph_sample_1000(500,0.01)
        threat_mobility_ratio = 0. 
        hteb = HTEBot_sample_QWAS(D,threat_mobility_ratio) 
        hteb_ = deepcopy(hteb)

        bmode = np.array([1. , 1. , 0. , 0.])
        hteb.set_bot_mode(bmode)

        t = time.time() 
        stats,P = HTEBot.run_n_navigators(hteb,50,1,True)
        S = count_success_in_increments(stats,10)  

        bmode = np.array([1. , 1. , 1. , 0.])
        hteb_.set_bot_mode(bmode)
        stats2,P2 = HTEBot.run_n_navigators(hteb_,50,1,True)
        S2 = count_success_in_increments(stats2,10)  

        assert sum(S) > sum(S2) 
        return

    """
    demonstrates a <HTEBot> case, with 75% of the threats 
    being mobile (contra). Navigator `contra_risk` set to 
    0 performs better than that with `contra_risk` set to 0.5. 
    """
    def test__HTEBot__run_navigator__case_4(self):
        print("\t\tCASE 4")
        D = generated_graph_sample_1000(500,0.01)
        threat_mobility_ratio = 0.75   
        hteb = HTEBot_sample_QWAS(D,threat_mobility_ratio) 
        hteb_ = deepcopy(hteb)

        bmode = np.array([1. , 1. , 0. , 0.5])
        hteb.set_bot_mode(bmode)

        t = time.time() 
        stats,P = HTEBot.run_n_navigators(hteb,50,1,True)
        S = count_success_in_increments(stats,10)  

        bmode = np.array([1. , 1. , 0. , 0.])
        hteb_.set_bot_mode(bmode)
        stats2,P2 = HTEBot.run_n_navigators(hteb_,50,1,True)
        S2 = count_success_in_increments(stats2,10)  

        assert sum(S) == 12 and sum(S2) == 17 

    """
    demonstrates a <HTEBot> case with one navigator 
    that performs slightly better than another, with 
    the use of isomorphic prediction. 

    HTEBOT_FEEDS_NAVIGATOR_ALL_ISOMORPHIC_NODES is set 
    to True. 
    """
    def test__HTEBot__run_navigator__case_5(self):
        print("\t\tCASE 5")
        D = generated_graph_sample_1000(500,0.01)
        threat_mobility_ratio = 0.75   
        hteb = HTEBot_sample_QWAS(D,threat_mobility_ratio) 

        bmode = np.array([1. , 1. , 0. , 0.5])
        hteb.set_bot_mode(bmode)

        t = time.time() 
        stats,P = HTEBot.run_n_navigators(hteb,50,1,True)
        S = count_success_in_increments(stats,10)  

        hteb_ = deepcopy(hteb)
        q = set(hteb.hte_surf.base_graph.keys())
        hteb.reproduce_surface(False) 
        q2 = set(hteb.hte_surf.base_graph.keys())

        assert q.intersection(q2) == set() 
        assert hteb.hte_nav.objectives == hteb.hte_surf.objective_points 
        assert hteb.hte_nav.loc in q2  

        stats2,P2 = HTEBot.run_n_navigators(hteb,50,1,True)
        S2 = count_success_in_increments(stats2,10)  

        bmode = np.array([1. , 0. , 0. , 0.5])
        hteb_.set_bot_mode(bmode)
        hteb_.reproduce_surface(False) 

        stats3,P3 = HTEBot.run_n_navigators(hteb_,50,1,True)
        S3 = count_success_in_increments(stats3,10) 

        assert sum(S2) == 17 and sum(S3) == 15,"got {},{}".format(sum(S2),sum(S3)) 

if __name__ == '__main__':
    unittest.main()