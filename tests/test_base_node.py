from graph_models.analog_schemes import * 
from graph_models.base_node import * 
from morebs2.numerical_generator import prg__LCG 
import unittest 

def graph__sample_NONOPON(): 
    prg = prg__LCG(567,321,-5656,9131) 
    prg2 = prg__LCG(63,131,567,-878) 

    # component 1 
    G1 = GraphGen(False,prg,is_realtime_gen=True,\
            vertex_degree=15,edge_connectivity=0.3) 
    G1.full_run() 
    G1 = G1.d 

    G1_ = graph_to_one_component(deepcopy(G1),prg)
    assert G1_ == G1 
    G1 = G1_

    # component 2 
    G2 = GraphGen(False,prg2,is_realtime_gen=True,\
            vertex_degree=18,edge_connectivity=0.27)  
    G2.full_run() 
    G2 = G2.d 

    ctr = SimpleCounter(len(G1)).__next__ 
    G2_,_ = graph_automorphism(G2,ctr)
    G2 = graph_to_one_component(deepcopy(G2_),prg)
    assert G2_ == G2

    DX = (MicroGraph(G1) + MicroGraph(G2)).dg 

    gaa = GraphAnalogAdder(DX,is_dsg=False,prg=prg,gen_scheme_zero_types={"tree","random"},connect_components=True,store_isomaps=True)
    for _ in range(5): 
        gaa.extend() 

    D = gaa.d
    D = graph_to_one_component(D,prg,True) 
    return D,prg,prg2 

def graph__sample_NONAVOID(): 
    prg = prg__LCG(51,321,-5656,9131) 

    tg = TreeGen(starting_nodeset = {0,1,2},is_dsg=False,prg=prg,branching_range=DEFAULT_TREE_BRANCHING_RANGE)

    for _ in range(8): 
        next(tg) 

    G = graph_to_one_component(tg.d,prg)
    return G,prg 

"""
py -m tests.test_base_node
"""
class NodeObjectiveNavigatorClass(unittest.TestCase):

    """
    demonstrates <NodeObjectiveNavigator> navigation to objective 
    nodes with limited information provided to it.
    """
    def test__NodeObjectiveNavigator__make_choice__case1(self):
        D,prg,_ = graph__sample_NONOPON() 

        avoid = {3,5,6,12}
        take = {2,7,9}
        objectives = {100,105,107}

        non = NodeObjectiveNavigator(0,avoid,take,objectives,prg) 
        non.receive_context(D) 

        i0 = 0 
        while non.loc not in {100,105,107}: 
            non.make_choice()
            i0 += 1 
        assert i0 == 31, "got {}".format(i0)

        while i0 < 99: 
            non.make_choice() 
            i0 += 1 
        assert non.loc == 100, "got {}".format(non.loc)
        return 

    """
    demonstrates <NodeObjectiveNavigator> navigation to objective 
    nodes with information on nodes of shortest paths provided. 
    """
    def test__NodeObjectiveNavigator__make_choice__case2(self):
        D,_,prg2 = graph__sample_NONOPON() 

        # add preferred nodes (from shortest paths info.)
        X0,X1 = BDFSCache.BFS_full(D,return_type="paths",prg=prg2)
        Q = [100,105,107] 
        take_nodeset = [] 
        for i in range(len(Q)):
            px = X0[(0,Q[i])].p 
            take_nodeset.extend(px) 
        take_nodeset = set(take_nodeset) - {3,5,6,12} - {100,105,107} 
        #print("TAKE")
        #print(take_nodeset)

        # declare navigator 
        non2 = NodeObjectiveNavigator(0,{3,5,6,12},take_nodeset,{100,105,107},prg2) 
        non2.receive_context(D)

        # navigate  
        i1 = 0 
        while non2.loc not in {100,105,107}: 
            non2.make_choice()
            i1 += 1 

        px = X0[(2,100)].p 

        for i in range(len(non2.path_log) - 1): 
            n0,n1 = non2.path_log[i],non2.path_log[i+1] 
            assert n1 in D[n0] 
        
        #print("PX: ",px) 
        #print("PATH: ",non2.path_log)
        #print("SHORTETH: ",X0[(0,107)].cost())
        #print(X0[(0,107)]) 
        assert len(non2.path_log) == 8, "got {}".format(len(non2.path_log)) 
        assert non2.path_log[-1] == 107, "got {}".format(non2.path_log) 

    """
    demonstrates navigator decisions in cases of no choice but to 
    take a node marked for avoidance. 
    """
    def test__NodeObjectiveNavigator__make_choice__case3(self): 
        G,prg = graph__sample_NONAVOID() 

        avoid_nodeset = {3,4,5}
        take_nodeset = set() 
        objective_nodeset = {100,105,115}

        # case: absolute_avoid == False 
        non = NodeObjectiveNavigator(0,avoid_nodeset,take_nodeset,objective_nodeset,prg) 
        non.receive_context(G) 

        for _ in range(20): 
            non.make_choice() 
        assert non.path_log == [0, 4, 7, 4, 6, 4, 8, 4, 6, 4, 7, 4, 0, 3, 0, 5, 12, 17, 12, 14, 12]

        # case: absolute_avoid == True 
        non2 = NodeObjectiveNavigator(0,avoid_nodeset,take_nodeset,objective_nodeset,prg,\
            absolute_avoid=True)
        non2.receive_context(G) 
        for _ in range(10): 
            non2.make_choice()

        assert non2.path_log == [0] 



if __name__ == '__main__':
    unittest.main()