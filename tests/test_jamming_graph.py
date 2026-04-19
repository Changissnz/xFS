from graph_models.jamming_graph import * 
import unittest

def JammingGraphTypeC__sample_JC1(): 
    p = [3,10,14] 
    pw = [1,1]
    nodepath = NodePath.preload(p,pw)

    prg = prg__LCG(-155.4,1313.1,-431.66,-10656.33)
    jg = JammingGraphTypeC(nodepath,{10},prg,is_path_directed=False,jam_nodesize_range=[2,5]) 
    return jg 

def JammingGraphTypeO__sample_OO(): 
    p = [3,10,14] 
    pw = [1,1]
    nodepath = NodePath.preload(p,pw)

    prg = prg__LCG(-155.4,1313.1,-431.66,-10656.33)
    jg = JammingGraphTypeO(nodepath,{10},prg,is_path_directed=False,jam_nodesize_range=[5,10]) 
    return jg 

### lone file test 
"""
py -m tests.test_jamming_graph 
"""
###
class JammingGraphTypeCClass(unittest.TestCase):

    """
    checks for deletion of node 10 after one jam. 
    """
    def test__JammingGraphTypeC__one_jam__case_1(self):
        jg = JammingGraphTypeC__sample_JC1() 
        jg.one_jam(10,True) 

        assert jg.G == defaultdict(set, {3: {15}, 14: {17}, 15: {16, 3}, 16: {17, 15}, 17: {16, 14}})
        assert jg.node2nodesets == defaultdict(list, {3: [{3}], 10: [{16, 17, 15}], 14: [{14}]})
        assert 10 not in jg.entire_nodeset_for_node(10) 
        return 

    def test__JammingGraphTypeC__one_jam__case_2(self):
        jg = JammingGraphTypeC__sample_JC1()             
        jg.one_jam(10,False) 

        assert jg.G == defaultdict(set, {3: {18}, 14: {17}, 10: {16, 18}, 16: {17, 10}, 17: {16, 14}, 18: {10, 3}})
        assert jg.node2nodesets == defaultdict(list, {3: [{3}], 10: [{16, 17, 18, 10}], 14: [{14}]})

        jg.one_jam(10,False)

        assert jg.G == defaultdict(set, {3: {18}, 14: {17}, 10: {16, 18}, 16: {17, 20, 10}, 17: {16, 14}, 18: {10, 3}, 20: {16, 21}, 21: {20}})
        assert jg.node2nodesets == defaultdict(list, {3: [{3}], 10: [{16, 17, 18, 20, 21, 10}], 14: [{14}]})

        jg.one_jam(10,True)

        assert jg.G == defaultdict(set, \
            {3: {18}, 14: {18}, 10: {16, 18}, \
            16: {10, 20}, 18: {10, 3, 14}, \
            20: {16, 21, 22}, 21: {20}, 22: {20, 23}, \
            23: {24, 22}, 24: {23}})
        assert jg.node2nodesets == defaultdict(list, \
            {3: [{3}], \
            10: [{16, 18, 20, 21, 10}, {24, 22, 23}], \
            14: [{14}]})

    """
    checks for crashless execution of method<one_jam> for 20 iterations. 
    """
    def test__JammingGraphTypeC__one_jam__case_3(self):
        jg = JammingGraphTypeC__sample_JC1()

        for _ in range(20): 
            jg.one_jam(10,bool(_ % 2)) 
        return 

    def test__JammingGraphTypeC__delete_nodeset__case_1(self): 
        jg = JammingGraphTypeC__sample_JC1()
        jg.one_jam(10,True) 
        jg.one_jam(10,False)
        jg.one_jam(10,False)
        jg.one_jam(10,False)
        jg.one_jam(10,True)
        jg.one_jam(10,True)

        # initial check 
        q = jg.node2nodesets[10] 
        ans = [{15, 17, 19, 21, 23, 24, 26, 27, 28, 29}, {32, 33, 30, 31}, {34, 35, 36}]
        assert q == ans 

        # delete one nodeset 
        x = ans[1] 
        jg.delete_nodeset(x) 

        q2 = jg.node2nodesets[10] 
        assert q2 == [{15, 17, 19, 21, 23, 24, 26, 27, 28, 29}, {34, 35, 36}]

        y = set(jg.G.keys()).intersection(x)
        assert y == set() 

        # delete another nodeset 
        x2 = {34,36} 
        jg.delete_nodeset(x2) 

        q2 = jg.node2nodesets[10] 
        assert q2 == [{15, 17, 19, 21, 23, 24, 26, 27, 28, 29}, {35}]

        y2 = set(jg.G.keys()).intersection(x2)
        assert y2 == set() 

    def test__JammingGraphTypeC__IS_DETERMINISTIC(self): 

        def fx(jg): 

            l = [len(jg.G)]
            jg.one_jam(10,True) 
            l.append(len(jg.G))
            jg.one_jam(10,False)
            l.append(len(jg.G))
            jg.one_jam(10,False)
            l.append(len(jg.G))
            jg.one_jam(10,False)
            l.append(len(jg.G))
            jg.one_jam(10,True)
            l.append(len(jg.G))
            jg.one_jam(10,True)
            l.append(len(jg.G))
            return l 

        jg = JammingGraphTypeC__sample_JC1()
        l = fx(jg) 

        for _ in range(10): 
            jg = JammingGraphTypeC__sample_JC1()
            l2 = fx(jg) 
            assert l == l2 


class JammingGraphTypeOClass(unittest.TestCase):

    """
    checks for deletion of node 10 after one jam. 
    """
    def test__JammingGraphTypeO__one_jam__case_1(self):
        jg = JammingGraphTypeO__sample_OO()

        jg.one_jam(10,False) 
        assert jg.G == defaultdict(set, \
            {3: {16}, 14: {16}, 10: {15}, \
            15: {16, 18, 10}, 16: {3, 14, 15}, \
            17: {18, 19}, 18: {17, 15}, 19: {17}}), "got {}".format(jg.G)
            
        assert jg.node2nodesets == defaultdict(\
            list, {3: [{3}], 10: [{16, 17, 18, 19, 10, 15}], 14: [{14}]})
        assert jg.dead_nodes == set(), "got {}".format(jg.dead_nodes)   

        jg.one_jam(10,True) 
        assert jg.G == defaultdict(set, \
            {3: {16}, 14: {16}, 10: {22, 15}, \
            15: {16, 18, 10}, 16: {3, 14, 15}, \
            17: {18}, 18: {17, 15}, 20: {24, 21}, \
            21: {20, 22, 23}, 22: {10, 21}, \
            23: {21}, 24: {20}}),"got {}".format(jg.G)

        assert jg.node2nodesets == defaultdict(list, \
             {3: [{3}], 10: [{16, 17, 18, 10, 15}, {20, 21, 22, 23, 24}], 14: [{14}]}), "got {}".format(jg.node2nodesets)
        assert jg.dead_nodes == {19}, "got {}".format(jg.dead_nodes)   

    """
    checks for crashless execution of method<one_jam> for 20 iterations. 
    """
    def test__JammingGraphTypeO__one_jam__case_2(self):
        jg = JammingGraphTypeO__sample_OO()

        for _ in range(20): 
            jg.one_jam(10,bool(_ % 2)) 
        return 


    """
    demonstrates subgraph alteration, with possibility for graph disconnection 
    """
    def test__JammingGraphTypeO__alter_nodeset__case_1(self): 
        jg = JammingGraphTypeO__sample_OO()
        jg.one_jam(10,False) 
        jg.one_jam(10,True) 

        mg0 = MicroGraph(jg.G)
        jg.alter_nodeset(True) 
        mg1 = MicroGraph(jg.G)

        qx = mg0.sub_ve_score(mg1)
        qx2 = mg1.sub_ve_score(mg0)
        assert qx == (4,8),"got {}".format(qx) 
        assert qx2 == (4,4), "got {}".format(qx2)

        gd = GraphComponentDecomposition(jg.G)
        gd.decompose() 
        assert len(gd.components) == 3, "got {}".format(len(gd.components)) 

    """
    demonstrates subgraph alteration that maintains fully connected graph. 
    """
    def test__JammingGraphTypeO__alter_nodeset__case_2(self): 
        jg = JammingGraphTypeO__sample_OO()
        jg.one_jam(10,False) 
        jg.one_jam(10,True) 

        mg0 = MicroGraph(jg.G)
        jg.alter_nodeset(False) 
        mg1 = MicroGraph(jg.G)

        qx = mg0.sub_ve_score(mg1)
        qx2 = mg1.sub_ve_score(mg0)
        assert qx == (4, 8), "got {}".format(qx)
        assert qx2 == (4, 16),"got {}".format(qx2)

        gd = GraphComponentDecomposition(jg.G)
        gd.decompose() 
        assert len(gd.components) == 1, "got {}".format(len(gd.components))

    """
    checks for correct number of components after method<disconnect_neighbors>.  
    """
    def test__JammingGraphTypeO__disconnect_neighbors__case_1(self): 

        jg = JammingGraphTypeO__sample_OO()
        jg.one_jam(10,False) 
        jg.one_jam(10,True) 
        jg.one_jam(10,False) 
        gd = GraphComponentDecomposition(jg.G)
        gd.decompose() 
        assert len(gd.components) == 1 

        jg.disconnect_neighbors(10,3) 
        gd = GraphComponentDecomposition(jg.G)
        gd.decompose() 
        assert len(gd.components) > 1 

        


if __name__ == '__main__':
    unittest.main()