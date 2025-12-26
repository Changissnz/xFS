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
    assert not G1_ == G1 
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

    gaa = GraphAnalogAdder(DX,is_dsg=False,prg=prg,gen_scheme_one_types={"tree","random"},connect_components=True,store_isomaps=True)
    for _ in range(5): 
        gaa.extend() 

    D = gaa.d 
    return D,prg,prg2 

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
        objectives = {100,105,115}

        non = NodeObjectiveNavigator(0,avoid,take,objectives,prg) 
        non.receive_context(D) 

        i0 = 0 
        while non.loc not in {100,105,115}: 
            non.make_choice()
            i0 += 1 
        assert i0 == 44 

        while i0 < 100: 
            non.make_choice() 
            i0 += 1 
        assert non.loc == 115
        return 

    """
    demonstrates <NodeObjectiveNavigator> navigation to objective 
    nodes with information on nodes of shortest paths provided. 
    """
    def test__NodeObjectiveNavigator__make_choice__case2(self):
        D,_,prg2 = graph__sample_NONOPON() 

        # add preferred nodes (from shortest paths info.)
        X0,X1 = BDFSCache.BFS_full(D,return_type="paths",prg=prg2)
        Q = [12,38,65,80,100,115] 
        take_nodeset = [] 
        for i in range(len(Q) -1): 
            q0,q1 = Q[i],Q[i+1]
            px = X0[(q0,q1)].p 
            take_nodeset.extend(px) 
        take_nodeset = set(take_nodeset) - {3,5,6,12} - {100,105,115} 
        #print("TAKE")
        #print(take_nodeset)

        # declare navigator 
        non2 = NodeObjectiveNavigator(0,{3,5,6,12},take_nodeset,{100,105,115},prg2) 
        non2.receive_context(D)

        # navigate  
        i1 = 0 
        while non2.loc not in {100,105,115}: 
            non2.make_choice()
            i1 += 1 

        px = X0[(2,100)].p 

        for i in range(len(non2.path_log) - 1): 
            n0,n1 = non2.path_log[i],non2.path_log[i+1] 
            assert n1 in D[n0] 
        
        #print("PX: ",px) 
        #print("PATH: ",non2.path_log)
        assert len(non2.path_log) == 8 
        assert non2.path_log[-1] == 100



if __name__ == '__main__':
    unittest.main()