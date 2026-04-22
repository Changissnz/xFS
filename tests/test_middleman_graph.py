from quant.middleman_graph import * 
import unittest

def MiddleManNetwork__case_GRANGER(jamming_graph_type="c"): 
    prg1 = prg__LCG(-56.7,100.9,-677.6,-9176.3) 
    prg2 = prg__LCG(116.7,-2200.9,67.6,80176.3) 

    mm = MiddleManNetwork.generate_instance(jamming_graph_type,1.05,\
        allow_buyer_memoryless_navigation=True,\
        prg1=prg1,prg2=prg2)
    mm.verbose = False 
    return mm 

### lone file test 
"""
py -m tests.test_middleman_graph
"""
###
class MiddleManNetworkClass(unittest.TestCase):

    """
    demonstrates reproduction of high-frequency sellers 
    """
    def test__MiddleManNetwork___next__case_1(self): 
        print("case 1")

        mm = MiddleManNetwork__case_GRANGER("c")
        for _ in range(30): 
            next(mm) 

        # check for 8 reproducing 
        for k,v in mm.middle_agents.items(): 
            if k == 8: 
                assert len(v.intermediate_sellers) == 1 
            elif k == 2: 
                assert len(v.intermediate_sellers) > 1 
            else: 
                assert len(v.intermediate_sellers) == 0 

        # check buyer bought 30 units 
        assert mm.buying_agent.units_bought == 30 
        assert 25 < mm.buying_agent.cumulative_expenses <= 35

    """
    demonstrates auto-termination of dominant sellers 
    """
    def test__MiddleManNetwork___next__case_2(self): 
        print("case 2")
        mm = MiddleManNetwork__case_GRANGER("c")
        for _ in range(100): 
            next(mm) 

        print("LOG")
        print(mm.seller_idn_log)
        assert mm.eliminated_dominants == {30},"got {}".format(mm.eliminated_dominants)

        c = Counter(mm.seller_idn_log) 
        print("counter ")
        print(c) 
        assert DEFAULT_MIDDLE_AGENT_DOMINANT_SELLER_TERMINATION_RANGE[0] <= c[30] < DEFAULT_MIDDLE_AGENT_DOMINANT_SELLER_TERMINATION_RANGE[1] 

    """
    demonstrates termination of bankrupted sellers  
    """
    def test__MiddleManNetwork___next__case_3(self): 
        
        # NOTE: to demonstrate network determinism, change the integers of these seeds to whatever.
        random.seed(542) 
        np.random.seed(1112) 

        print("case 3")
        mm = MiddleManNetwork__case_GRANGER("c")

        assert len(mm.jg.G) == 29 
        assert len(mm.middle_agents) == 25 

        for _ in range(20): 
            next(mm) 
        assert len(mm.eliminated_bankrupts) == 0 
        assert len(mm.jg.G) == 34,"got {}".format(len(mm.jg.G))

        for _ in range(20): 
            next(mm) 
        assert len(mm.eliminated_bankrupts) == 0 
        assert len(mm.middle_agents) == 29 
        assert len(mm.jg.G) == 65, "got {}".format(len(mm.jg.G))

        for _ in range(20): 
            next(mm) 
        assert len(mm.eliminated_bankrupts) == 4,"got {}".format(len(mm.eliminated_bankrupts)) 
        assert len(mm.jg.G) == 66,  "got {}".format(len(mm.jg.G))

        q = mm.eliminated_bankrupts.intersection(set(mm.jg.G.keys()))
        assert len(q) == 0 



if __name__ == '__main__':
    unittest.main()