from graph_models.hg_obj_path import * 
import unittest 

def NodeActivationFunctionTypeMT__sample_RYQN(activation_type): 
    node_idn = 4
    prior_dependencies = {0,1,2} 
    node_value_range_map = {0:[-10,0],1:[5,25],2:[50,100],4:[23,56]}  
    #activation_type = "linexp" 
    max_path = NodePath.preload([0,7,1,3,8,2,4,9],[1]*7) 
    add_activation_node = True 

    prg = prg__LCG(45.55,67.77,-4848.5,9654.1) 

    nt = NodeActivationFunctionTypeMT.generate_instance(\
        node_idn,prior_dependencies,node_value_range_map,activation_type,\
        max_path,add_activation_node,prg)
    return nt,node_value_range_map

### lone file test 
"""
py -m tests.test_hg_obj_path
""" 
###
class NodeActivationFunctionTypeMTClass(unittest.TestCase):

    def test__NodeActivationFunctionTypeMT__register__case_1(self): 
        
        nt,node_value_range_map = NodeActivationFunctionTypeMT__sample_RYQN(activation_type="linexp")

        for k,v in nt.n2mt_map.items(): 
            r = node_value_range_map[k]
            assert r[0] <= v < r[1] 

        d = defaultdict(float,{0:-5,1:5,2:50,4:23})

        d2 = nt.n2mt_map
        q = sum([d[k] * d2[k] for k in d.keys()]) 

        assert q < nt.lin_exp_value
        assert not nt.register(d)[1]  

        d3 = defaultdict(float,{0:-2,1:20,2:65,4:30})
        q = sum([d2[k] * d3[k] for k in d2.keys()]) 
        assert q < nt.lin_exp_value, "q={}".format(q)
        assert not nt.register(d)[1]  

        d4 = defaultdict(float,{0:-2,1:20,2:95,4:40})
        q = sum([d2[k] * d4[k] for k in d2.keys()])  
        assert q >= nt.lin_exp_value, "q={}".format(q)
        assert not nt.register(d)[1] 

    def test__NodeActivationFunctionTypeMT__register__case_2(self): 

        nt,node_value_range_map = NodeActivationFunctionTypeMT__sample_RYQN(activation_type="single")

        for k,v in nt.n2mt_map.items(): 
            r = node_value_range_map[k]
            assert r[0] <= v < r[1] 

        d = defaultdict(float,{0:-5,1:5,2:50,4:23})

        d2 = nt.n2mt_map
        print("single threshold: {}".format(d2))

        assert not nt.register(d)[1] 

        d3 = defaultdict(float,{0:-5,1:12,2:50,4:56}) 
        assert not nt.register(d3)[1]  

        d3[2] = 90 
        assert nt.register(d3)[1]  

if __name__ == '__main__':
    unittest.main()
