from graph_models.path_induction import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg__LCG 
import time 
import unittest

def min_paths_sample_R(vertex_degree,num_paths_per_node): 
    prg = prg__LCG(67.4,-100,89.6,9196.66)
    is_realtime_gen = True 
    #vertex_degree = 12 
    edge_connectivity = 0.2   
    gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity,\
            verbose=False)
    gg.full_run() 
    G = graph_to_one_component(gg.d,prg)

    start_node = 3 
    bc = BDFSCache(start_node,G,is_bfs=True,prg=prg,\
        edge_cost_function=lambda u,v:1,num_paths_per_node=num_paths_per_node,\
        max_search_radius=float('inf'),verbose=False)
    bc.exec()
    return bc.min_paths,prg  
    
### lone file test 
"""
py -m tests.test_path_induction 
"""
class PathInductionClass(unittest.TestCase):

    def test__PathInduction__one_path_case_1(self): 
        P,prg = min_paths_sample_R(12,3)
        PI = PathInduction(3,P,prg,num_segment_range=[1,2])
        PX = [] 

        ans = set([(3, 7, 6),\
            (3, 1, 6),\
            (3, 7, 6, 5, 6)]) 

        S = set()

        for i in range(100): 
            q = PI.one_path(6,True,0)
            PX.append(q)
            S |= {tuple(q.p)}
        assert ans == S 

    def test__PathInduction__one_path_case_2(self):
        P,prg = min_paths_sample_R(30,6)
        PI = PathInduction(6,P,prg,num_segment_range=[3,7])
        PX = [] 

        ans = {(3, 9, 18, 17, 19, 17, 12, 17), \
            (3, 13, 23, 17, 19, 17), \
            (3, 19, 17, 12, 17, 12, 17), \
            (3, 13, 23, 17, 23, 17), \
            (3, 13, 23, 17, 23, 13, 23, 17), \
            (3, 9, 23, 17, 23, 17), \
            (3, 9, 23, 17, 28, 1, 21, 19, 17, 12, 17), \
            (3, 1, 28, 17, 28, 1, 3, 19, 17, 28, 17), \
            (3, 1, 28, 17, 23, 13, 23, 17), \
            (3, 9, 18, 17, 28, 1, 28, 17), \
            (3, 19, 17, 19, 17, 23, 13, 23, 17), \
            (3, 13, 23, 17, 19, 17, 12, 17), \
            (3, 9, 23, 17, 19, 27, 28, 17), \
            (3, 13, 23, 17, 12, 17), \
            (3, 13, 23, 17, 19, 17, 23, 17), \
            (3, 19, 17, 23, 13, 1, 28, 1, 28, 17), \
            (3, 9, 18, 17, 28, 17), \
            (3, 1, 28, 17, 19, 17, 23, 17), \
            (3, 19, 17, 12, 17, 23, 13, 23, 17), \
            (3, 19, 17, 19, 1, 13, 1, 28, 17), \
            (3, 9, 18, 17, 19, 17), \
            (3, 19, 17, 12, 17, 19, 17, 23, 13, 1, 28, 17), \
            (3, 9, 23, 17, 19, 1, 14, 18, 9, 23, 17), \
            (3, 9, 23, 17, 19, 17, 12, 17), \
            (3, 19, 17, 12, 17, 28, 1, 28, 17), \
            (3, 1, 28, 17, 28, 17), \
            (3, 19, 17, 12, 17, 19, 17, 12, 17), \
            (3, 19, 17, 12, 17, 19, 17, 23, 17), \
            (3, 9, 18, 17, 12, 17), \
            (3, 9, 18, 17, 23, 13, 1, 28, 17), \
            (3, 19, 17, 12, 17, 28, 1, 3, 6, 1, 28, 17), \
            (3, 19, 17, 28, 17), \
            (3, 9, 18, 17, 23, 17), \
            (3, 9, 18, 17, 19, 27, 28, 1, 28, 17), \
            (3, 19, 17, 12, 17, 19, 1, 28, 17), \
            (3, 1, 28, 17, 12, 17), \
            (3, 1, 28, 17, 23, 17), \
            (3, 9, 18, 17, 28, 1, 5, 18, 17), \
            (3, 1, 28, 17, 19, 27, 28, 17), \
            (3, 19, 17, 12, 17, 28, 17), \
            (3, 19, 17, 19, 1, 28, 1, 28, 17), \
            (3, 19, 17, 19, 17), \
            (3, 9, 23, 17, 28, 17), \
            (3, 19, 17, 23, 13, 23, 17), \
            (3, 9, 23, 17, 19, 17), \
            (3, 1, 28, 17, 28, 1, 28, 17), \
            (3, 19, 17, 12, 17), \
            (3, 19, 17, 23, 17), \
            (3, 1, 28, 17, 19, 17, 12, 17), \
            (3, 19, 17, 28, 1, 28, 17), \
            (3, 9, 18, 17, 19, 1, 28, 17), \
            (3, 9, 23, 17, 12, 17), \
            (3, 19, 17, 19, 17, 12, 17)}

        S = set()

        for i in range(100): 
            q = PI.one_path(17,True,0)
            PX.append(q)
            S |= {tuple(q.p)}

        assert ans == S 

    def test__PathInduction__one_path_case_3(self):
        P,prg = min_paths_sample_R(30,6)
        PI = PathInduction(3,P,prg,num_segment_range=[3,7])
        PX = [] 
        lengths = set()
        target = 17
        for i in range(100): 
            q = PI.one_path(target,True,100)
            assert q.tail() == target 
            lengths |= {len(q)}
        assert lengths == {101, 102, 103, 104, 105},"got {}".format(lengths)

    def test__PathInduction__one_path_case_4(self):
        prg = prg__LCG(0,0,1,2)

        start_node = 0 
        G = generate_graph__path(2,0,False) 
        bc = BDFSCache(start_node,G,is_bfs=True,prg=prg,\
            edge_cost_function=lambda u,v:1,num_paths_per_node=6,\
            max_search_radius=float('inf'),verbose=False)
        bc.exec()
        P = bc.min_paths 

        PI = PathInduction(0,P,prg,num_segment_range=[3,7])
        PX = [] 
        S = set()

        for i in range(100): 
            q = PI.one_path(1,True,100)
            S |= {tuple(q.p)}

        assert S == {(0,1)} 

if __name__ == '__main__':
    unittest.main()