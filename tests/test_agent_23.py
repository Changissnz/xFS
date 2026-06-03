from quant.agent_23 import * 
import unittest

def AgentType2F3MTrifecta__sample_TREI(mo_type,uc=None): 
    agent_idns = [2,1,0] 
    num_categories = 8  
    label_size_range = [3,10] 
    attribute_bound_vec = None 
    prg = prg__LCG(45.55,-133.2,300.6,1599.6) 

    attribute_bound_vec = None 
    if mo_type == "compatible characterization":
        attribute_bound_vec = np.array([[0,10],\
            [0,10],[0,10],[0,10]]) 
    
    ATT = AgentType2F3MTrifecta.generate_instance(agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,prg)

    if type(uc) != type(None): 
        ATT.set_uniform_compatibility(uc,True) 
    return ATT 

"""
py -m tests.test_agent_23
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class AnalogGraphClass(unittest.TestCase):

    def test__AgentType2F3MTrifecta__next__case_1(self): 
        print("\t\tCASE 1: CC") 
        mo_type = "compatible characterization"
        ATT = AgentType2F3MTrifecta__sample_TREI(mo_type,None) 

        # check for exact scores 
        for _ in range(20): next(ATT) 
        S = ATT.scores()
        assert S == [(91, 160), (51, 160), (97, 160)]

        q0 = ATT.a0 
        cvec = q0.cat_vec() 

        # check for appropriate categories per other agent, in inbox variable
        assert len(q0.mo_container.other_char_recv) == 2 
        for other_agent in q0.mo_container.other_char_recv.keys(): 
            x = set(q0.mo_container.other_char_recv[other_agent].keys()) 
            assert x == set(cvec) 
        return 

    """
    checks for monotonically decreasing score from increasing trifecta uniform 
    compatibility 
    """
    def test__AgentType2F3MTrifecta__next__case_2(self): 
        print("\t\tCASE 2: CC") 
        mo_type = "compatible characterization"
        
        uc = [0.1 * i for i in range(11)] 
        
        S = defaultdict(list)
        for u in uc: 
            ATT = AgentType2F3MTrifecta__sample_TREI(mo_type,u) 
            for _ in range(10): next(ATT) 
            s = ATT.scores() 

            for (i,s_) in enumerate(s): 
                S[i].append(s_) 
            print("* {}".format(s))

        for v in S.values(): 
            q = sorted(v) 
            assert q == v[::-1]  
        return 

    """
    checks for monotonically decreasing score from increasing trifecta uniform 
    compatibility 
    """
    def test__AgentType2F3MTrifecta__next__case_3(self): 
        print("\t\tCASE 3: CC") 
        mo_type = "compatible characterization"
        
        uc = [0.5 * i for i in range(3)]  
        
        S = defaultdict(list)
        for u in uc: 
            ATT = AgentType2F3MTrifecta__sample_TREI(mo_type,u) 
            for _ in range(70): next(ATT) 
            s = ATT.scores() 

            for (i,s_) in enumerate(s): 
                S[i].append(s_) 
            print("* {}".format(s))

        for v in S.values(): 
            q = sorted(v) 
            assert q == v[::-1]  

        exact_sol = defaultdict(list,{0:[(356, 560),(271, 560),(121, 560)],\
            1:[(375, 560),(283, 560),(135, 560)],\
            2:[(383, 560),(308, 560),(120, 560)]})
        assert S == exact_sol 

    """
    checks for monotonically increasing score from increasing trifecta uniform 
    compatibility 
    """
    def test__AgentType2F3MTrifecta__next__case_4(self): 
        print("\t\tCASE 4: 3PC") 
        mo_type = "third-party contra"
        
        uc = [0.1 * i for i in range(11)]  
        
        S = defaultdict(list)
        for u in uc: 
            ATT = AgentType2F3MTrifecta__sample_TREI(mo_type,u) 
            for _ in range(100): next(ATT) 
            s = ATT.scores() 

            for (i,s_) in enumerate(s): 
                S[i].append(s_) 
            print("* {}".format(s))

        exact_sol = defaultdict(list, \
            {0: [(0, 800), (2, 800), (19, 800), (49, 800), (92, 800), (124, 800), \
                (154, 800), (189, 800), (222, 800), (238, 800), (260, 800)], \
            1: [(0, 800), (3, 800), (17, 800), (42, 800), (78, 800), (112, 800), \
                (141, 800), (165, 800), (192, 800), (208, 800), (233, 800)], \
            2: [(0, 800), (4, 800), (19, 800), (44, 800), (92, 800), (129, 800), \
                (166, 800), (202, 800), (222, 800), (240, 800), (252, 800)]})
        assert S == exact_sol 

    """
    checks for greater performance using different PRNG from the default 
    """
    def test__AgentType2F3MTrifecta__next__case_5(self): 
        print("\t\tCASE 5: CC") 

        prg_ = prg__LCG(-56.55,7666.5,416235.4,30166.6) 
        prg2_ = prg__LCG(62.2,65.6,32.2,3009.11) 
        prg3_ = prg__LCG(452.2,165.6,-6332.2,13456.11) 
        prg_ = merge_two_prgs(merge_two_prgs(prg_,prg2_,add),prg3_,sub) 

        mo_type = "compatible characterization"

        ATT0 =  AgentType2F3MTrifecta__sample_TREI(mo_type,0.0)
        ATT = AgentType2F3MTrifecta__sample_TREI(mo_type,0.0) 
        ATT.a0.set_prg(deepcopy(prg_))

        for _ in range(80):
            print("{}".format(_))
            next(ATT0)

        for _ in range(80): 
            print("{}".format(_))
            next(ATT) 

        S0 = ATT0.scores()
        S1 = ATT.scores()

        assert S0[0][0] == 415 < S1[0][0] == 458 

if __name__ == '__main__':
    unittest.main()