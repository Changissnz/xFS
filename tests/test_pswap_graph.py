from graph_models.pswap_graph import * 
from graph_models.graph_gen import * 
import unittest 
import time 

def PSwapGraph__sample_VAR(num_nodes,ratio,prg): 

    g = GraphGen(False,prg,True,num_nodes,ratio) 
    g.full_run() 
    graph_to_one_component(g.d,prg) 

    P = PSwapGraph.generate_token_placement(len(g.d),prg)
    return g.d,P,prg 



### lone file test 
"""
py -m tests.test_pswap_graph 
"""
###
# NOTE: the results in these test cases rely on Python/Numpy random. 
#       The specific Python version is Python 3.14.2. 
#       User output may differ from this output. 
class PSwapGraphClass(unittest.TestCase):

    """
    case: 400 node graph 
    """
    def test__PSwapGraph__module_route_one_round__case_1(self): 
        num_nodes = 400 
        ratio = 0.0005
        prg = prg__LCG(24.31,625.52,6226.3,91766.4)
        G,P,prg = PSwapGraph__sample_VAR(num_nodes,ratio,prg) 

        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=True)  

        t = time.time() 
        pg.preswap_analysis()
        print("case #1 pre-analysis")
        print("time elapsed: {}".format(time.time() - t)) 

        t = time.time() 
        c = pg.cumulative_token_distance()[1] 
        num_route_iter = 0 
        while c < num_nodes: 
            pg.module_route_one_round() 
            num_route_iter += 1 
            c = pg.cumulative_token_distance()[1] 
        print("num iter: ",num_route_iter)
        assert num_route_iter == 3 
        print("swap time: ",time.time() - t)
        print("--" * 25) 

        return

    """
    case: 100 node graph 
    """
    def test__PSwapGraph__module_route_one_round__case_2(self): 
        num_nodes = 100 
        ratio = 0.005
        prg = prg__LCG(-1124.31,625.52,6226.3,-91766.4)
        G,P,prg = PSwapGraph__sample_VAR(num_nodes,ratio,prg) 

        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=True)  

        t = time.time() 
        pg.preswap_analysis()
        print("case #2 pre-analysis")
        print("time elapsed: {}".format(time.time() - t)) 

        t = time.time() 
        c = pg.cumulative_token_distance()[1] 
        num_route_iter = 0 
        while c < num_nodes: 
            pg.module_route_one_round() 
            num_route_iter += 1 
            c = pg.cumulative_token_distance()[1] 
        print("num iter: ",num_route_iter)
        assert num_route_iter == 3 
        print("swap time: ",time.time() - t)
        print("--" * 25) 
        
        return

    """
    case: 500 node graph 
    """
    def test__PSwapGraph__module_route_one_round__case_3(self): 
        num_nodes = 500 
        ratio = 0.0005
        prg = prg__LCG(24.31,625.52,6226.3,91766.4)
        G,P,prg = PSwapGraph__sample_VAR(num_nodes,ratio,prg) 

        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=True)  

        t = time.time() 
        pg.preswap_analysis()
        print("case #3 pre-analysis")
        print("time elapsed: {}".format(time.time() - t)) 

        t = time.time() 
        c = pg.cumulative_token_distance()[1] 
        num_route_iter = 0 
        while c < num_nodes and num_route_iter < 15: 
            pg.module_route_one_round() 
            num_route_iter += 1 
            c = pg.cumulative_token_distance()[1] 
        print("num iter: ",num_route_iter)
        assert num_route_iter == 3 
        print("final score: {}/{}".format(c,num_nodes))
        print("swap time: ",time.time() - t)
        print("--" * 25) 
        
        return

    """
    case: 1000 node graph 
    """
    def test__PSwapGraph__module_route_one_round__case_4(self): 
        num_nodes = 1000 
        ratio = 0.009
        prg = prg__LCG(24.31,625.52,6226.3,91766.4)
        G,P,prg = PSwapGraph__sample_VAR(num_nodes,ratio,prg) 

        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=True)  

        t = time.time() 
        pg.preswap_analysis()
        print("case #4 pre-analysis")
        print("time elapsed: {}".format(time.time() - t)) 

        t = time.time() 
        c = pg.cumulative_token_distance()[1] 
        num_route_iter = 0 
        while c < num_nodes and num_route_iter < 15: 
            pg.module_route_one_round() 
            num_route_iter += 1 
            c = pg.cumulative_token_distance()[1] 
        print("num iter: ",num_route_iter)
        print("final score: {}/{}".format(c,num_nodes))
        print("swap time: ",time.time() - t)
        print("--" * 25) 
        
        return


class PSGraphHandlerClass(unittest.TestCase):

    """
    demonstrates a complete solution to the 1000-node graph 
    in test method<test__PSwapGraph__module_route_one_round__case_4>. 
    """
    def test__PSGraphHandler__auto_solution_search__case_1(self): 

        print("handler case #1")

        num_nodes = 1000 
        ratio = 0.009 #0.0005 #0.009
        prg = prg__LCG(24.31,625.52,6226.3,91766.4)
        G,P,prg = PSwapGraph__sample_VAR(num_nodes,ratio,prg) 

        prg = prg__LCG(4.31,-625.52,226.3,1766.4)
        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=True)  
        ph = PSGraphHandler(pg)

        c = 0 
        while not ph.fin_stat: 
            ph.auto_solution_search() 
            c += 1 

        print("num handler iter: ",c)
        print("--" * 25)


if __name__ == '__main__':
    unittest.main()