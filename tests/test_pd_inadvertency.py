from quant.pd_inadvertency import * 
import unittest

def PRNGProactionInadvertentEffect__sample_SUDOSTD(): 

    start_node_idn = 5 
    inadvertency_ratio_range = [0.05,0.15]
    node_value_range = [30.,350.]
    inadvertency_size_range = [2,6] 
    info_mode = 0 
    prg = prg__LCG(67.66,-56.77,455.5,931.1) 

    PIE,_ = PRNGProactionInadvertentEffect.generate_instance(start_node_idn,inadvertency_ratio_range,\
        node_value_range,inadvertency_size_range,info_mode,prg)
    return PIE 

### lone file test 
"""
py -m tests.test_pd_inadvertency  
"""
class PRNGProactionInadvertentEffectClass(unittest.TestCase):

    """
    pass w/ inadvertency of 12 
    """    
    def test__PRNGProactionInadvertentEffect__next__case_1(self): 
        PIE = PRNGProactionInadvertentEffect__sample_SUDOSTD() 

        i = 0 
        while not PIE.fin_stat:
            next(PIE)
            i += 1 

        assert i == 11 
        assert PIE.iscore() == defaultdict(int, {5: 8, 7: 3, 6: 1})

    """
    pass w/ inadvertency of 8 
    """
    def test__PRNGProactionInadvertentEffect__next__case_2(self): 
        PIE = PRNGProactionInadvertentEffect__sample_SUDOSTD() 
        prg2 = prg__LCG(54.66,-764.55,76.88,9033.5)
        PIE.set_prg(prg2)

        i = 0 
        while not PIE.fin_stat and i < 100:
            next(PIE)
            i += 1 

        assert i == 11, "got {}".format(i)
        D = PIE.iscore() 
        assert D == defaultdict(int, {5: 7, 6: 1, 7: 0})

    """
    cannot pass 
    """
    def test__PRNGProactionInadvertentEffect__next__case_3(self): 
        PIE = PRNGProactionInadvertentEffect__sample_SUDOSTD() 
        prg2 = prg__LCG(0,2,3,4)
        PIE.set_prg(prg2)

        i = 0 
        while not PIE.fin_stat and i < 1000:
            next(PIE)
            ##print("i: {}".format(i)) 
            i += 1 

        D = PIE.iscore() 
        assert D == defaultdict(int, {5: 0}), "got {}".format(D) 

class PRNGProactionInadvertentEffectChainClass(unittest.TestCase): 

    def test__PRNGProactionInadvertentEffectChain__next__case_1(self): 
        prior_connectivity_pr = 0.3 
        inadvertency_ratio_range = [0.05,0.15]
        node_value_range = [30.,350.]
        inadvertency_size_range = [2,6] 
        info_mode = 0 
        chain_prg = prg__LCG(-456.5,116.5,-5415.3,-8085.5) 
        solver_prg = prg__LCG(2.36,156.6,-906.3,9156.3) 
        ec = PRNGProactionInadvertentEffectChain(prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
                inadvertency_size_range,info_mode,chain_prg,solver_prg)

        for _ in range(2500): 
            next(ec) 

            ##if not _ % 10: 
            ##    print("score: ",ec.iscore_prev()) 
        
        s = ec.iscore_full()
        ##print("SS: ",s)
        assert s == 203342
        
        l = len(ec) 
        assert l == 115, "got {}".format(l)

if __name__ == '__main__':
    unittest.main()