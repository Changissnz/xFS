from graph_models.graph_gen import * 
from graph_models.shortest_paths_approx import * 
from graph_models._mg_sample import base_graph_sample_G
from morebs2.numerical_generator import prg__LCG
import time 
import unittest

def generated_graph_sample_1000(vertex_degree=1000,edge_connectivity=0.001): 
    is_dsg = False 
    prg = prg__LCG(55.6,63.44,-1174.1174,19199.5) 
    is_realtime_gen = True 
    #vertex_degree = 1000
    #edge_connectivity = 0.001
    
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity,verbose=False) 
    gg.full_run() 
    
    D = gg.d 
    D2 = graph_to_one_component(deepcopy(gg.d),prg)
    return D2 

def spa_timetest_query(): 
    stat,user_input = False,None
    while not stat: 
        user_input = input("[ShortestPathsApproximator] run time test?\n  (Y)es or (N)o: ").lower() 
        stat = user_input in {"y","n"}
    return user_input 

### lone file test 
"""
py -m tests.test_shortest_paths_approx
"""
###
class ShortestPathsApproximatorClasses(unittest.TestCase):

    """
    small graph, small subgraph radius=1 for approximator 
    """
    def test__ShortestPathsApproximator__paths__case1(self):

        D = base_graph_sample_G()
        prg = prg__LCG(57,112,-336,1001.4)
        R = 1

        spa = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=R,prg=prg,verbose=False)
        spa.exec() 

        path_ans = [[0, 2, 3, 4, 5],\
                    [0, 1, 3, 4, 5]]

        X = spa.paths(0,5)
        for x,p in zip(X,path_ans): 
            assert x.p == p 

        for p in spa.nodepair_path_info.values(): 
            assert p.cost() <= R 

    """
    small graph, small subgraph radius=2 for approximator 
    """
    def test__ShortestPathsApproximator__paths__case2(self): 

        D = base_graph_sample_G()
        R2 = 2 
        prg = prg__LCG(57,112,-336,1001.4)

        spa2 = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=R2,prg=prg,verbose=False)
        spa2.exec() 

        X2 = spa2.paths(0,5)
        X3 = spa2.paths(0,11) 

        path_ans2 = [\
            [0, 2, 3, 4, 6, 7, 5],\
            [0, 1, 3, 4, 6, 7, 5]] 

        for x,p in zip(X2,path_ans2): 
            assert x.p == p 

        path_ans3 = [\
            [0, 2, 3, 4, 6, 7, 8, 9, 11],\
            [0, 1, 3, 4, 6, 7, 8, 9, 11]]

        for (x,p) in zip(X3,path_ans3): 
            assert x.p == p 

        for p in spa2.nodepair_path_info.values(): 
            assert p.cost() <= R2 


    """
    large graph, subgraph radius=10 for approximator. 

    Demonstrates shortest path deduction for 160 nodes with 
    node=553. 
    """
    def test__ShortestPathsApproximator__paths__case3(self): 
        D = generated_graph_sample_1000()
        print("generated D of size=",len(D)) 

        prg = prg__LCG(0,1,3,10000)

        t0 = time.time() 
        spa = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=10,prg=prg,verbose=False)
        spa.exec() 
        print("exec time: ",time.time() - t0)

        q = 553 
        no_paths = [] 
        for i in range(1000): 
            PX = spa.paths(553,i) 
            if len(PX) == 0: 
                no_paths.append(i) 
        assert len(no_paths) == 160 

        for p in no_paths:
            PX = spa.deduce_path(553,p) 
            assert len(PX) > 0 

    """
    large graph, subgraph radius=4 for approximator. 

    Demonstrates shortest path deduction for 236 nodes with 
    node=553. 
    """
    def test__ShortestPathsApproximator__paths__case3(self): 

        D = generated_graph_sample_1000()#10000,10**-5)  
        print("generated D of size=",len(D)) 

        prg = prg__LCG(0,1,3,10000)

        t0 = time.time() 
        spa = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=4,prg=prg,verbose=False)
        spa.exec() 
        print("exec time: ",time.time() - t0)

        q = 553 
        no_paths = [] 
        for i in range(1000): 
            PX = spa.paths(553,i) 
            if len(PX) == 0: 
                no_paths.append(i) 
        assert len(no_paths) == 236 

        for p in no_paths:
            PX = spa.deduce_path(553,p) 
            assert len(PX) > 0 

    """
    shows runtime of calculation for generated graph of 10000 nodes and 
    approximator of max subgraph radius=10. 
    """
    def test__ShortestPathsApproximator__paths__timetest_case1(self):  
        user_input = spa_timetest_query() 
        if user_input == "n": return 

        D = generated_graph_sample_1000(10000,10**-5)  
        print("generated D of size=",len(D)) 

        prg = prg__LCG(0,1,3,10000)

        t0 = time.time() 
        spa = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=10,\
            prg=prg,verbose=False)
        spa.exec() 
        print("exec time: ",time.time() - t0)

    """
    shows runtime of calculation for generated graph of 10000 nodes and 
    approximator of max subgraph radius=5. 
    """
    def test__ShortestPathsApproximator__paths__timetest_case2(self):  
        user_input = spa_timetest_query() 
        if user_input == "n": return 

        D = generated_graph_sample_1000(10000,10**-5)  
        print("generated D of size=",len(D)) 

        prg = prg__LCG(0,1,3,10000)

        t0 = time.time() 
        spa = ShortestPathsApproximator(D,is_dfs=False,max_subgraph_radius=5,\
            prg=prg,verbose=False)
        spa.exec() 
        print("exec time: ",time.time() - t0)

if __name__ == '__main__':
    unittest.main()