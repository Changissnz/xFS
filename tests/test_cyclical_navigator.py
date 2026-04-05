from graph_models.cyclical_navigator import * 
from graph_models.node_navigator_handler import * 
from graph_models.graph_gen import * 
import time 
import unittest

def CyclicalNodeNavigatorTypeSM__sample_CNN(prg=prg__LCG(55.7,32.17,-1467.5,2222.5959),skew_frequency=False): 

    G = GraphGen(False,prg,False,100,0.09)
    G.full_run()
    G = G.d  

    loc = 5 
    frequency_range = [3,15]
    max_drift = 5 
    path_log_length = 150 

    csm = CyclicalNodeNavigatorTypeSM(loc,prg,frequency_range,\
        max_drift,skew_frequency,path_log_length)
    return csm,G,prg

def CyclicalNodeNavigatorTypeSM__sample_UNI(): 

    prg = prg__LCG(12.45,54.4,-600,1000.33)  
    G = generate_graph__path(10,0,is_dsg=True) 

    loc = 0  
    frequency_range = [3,15]
    max_drift = 5 
    skew_frequency = True 
    path_log_length = 150 

    csm = CyclicalNodeNavigatorTypeSM(loc,prg,frequency_range,\
        max_drift,skew_frequency,path_log_length)

    return csm,G,prg 


"""
py -m tests.test_cyclical_navigator
"""
class CyclicalNodeNavigatorTypeSMClass(unittest.TestCase):

    """
    demonstrates correct number of cycle iterations for a moderately connected graph 
    """
    def test__CyclicalNodeNavigatorTypeSM__make_choice__case_1(self):
        csm,G,prg = CyclicalNodeNavigatorTypeSM__sample_CNN() 

        nh = NavigatorGraphHandler(G,radius=1,navigator=csm,prg=prg) 

        csm.set_roaming_mode(True)

        NavigatorGraphHandler.iterate_n_rounds(nh,15) 

        csm.set_roaming_mode(False)

        next(nh) 
        L = len(csm.cycle_objective.current_target)
        C0 = [5, 42, 92, 39, 51, 40, 85, 64, 24, 12, 8, 34, 82, 26, 21, 36]
        assert csm.cycle_objective.current_target == C0 

        for _ in range(csm.cycle_objective.target_frequency + 1): 
            assert csm.cycle_objective.current_target == C0 
            NavigatorGraphHandler.iterate_n_rounds(nh,L)

        C1 = [36, 5]
        assert csm.cycle_objective.current_target == C1, "got {}".format(csm.cycle_objective.current_target)

    """
    demonstrates the `drift` effect of navigator on a unidirectional path 
    """
    def test__CyclicalNodeNavigatorTypeSM__make_choice__case_2(self):
        csm,G,prg = CyclicalNodeNavigatorTypeSM__sample_UNI() 
        nh = NavigatorGraphHandler(G,radius=1,navigator=csm,prg=prg) 

        csm.set_roaming_mode(False)

        for _ in range(15): 
            next(nh) 
            assert csm.drift_count == min([9,_+1])
            print("drift count: ",csm.drift_count)

        csm.set_roaming_mode(False)

    """
    checks that `skew_frequency` works. When set to True, possible for navigator 
    to repeat travel of cycle after target frequency has been reached. 
    """
    def test__CyclicalNodeNavigatorTypeSM__make_choice__case_3(self):
        prg = prg__LCG(-22.7,13.17,460.5,-1220.5959) 
        csm,G,prg = CyclicalNodeNavigatorTypeSM__sample_CNN(prg,skew_frequency=True)
        nh = NavigatorGraphHandler(G,radius=1,navigator=csm,prg=prg) 

        csm.verbose = True 
        csm.set_roaming_mode(True)

        for _ in range(15): 
            next(nh) 

        csm.set_roaming_mode(False)

        next(nh) 
        L = len(csm.cycle_objective.current_target)

        C0 = [11,36]
        assert csm.cycle_objective.current_target == C0,"got {}".format(csm.cycle_objective.current_target)        
        for _ in range(csm.cycle_objective.target_frequency + 1): 
            NavigatorGraphHandler.iterate_n_rounds(nh,L)

        # additional frequency 
        assert csm.cycle_objective.current_target == C0,"got {}".format(csm.cycle_objective.current_target)

if __name__ == '__main__':
    unittest.main()