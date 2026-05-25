from graph_models.hg_obj_path_op import * 
from morebs2.numerical_generator import * 
import unittest 

def DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,\
    prior_dependency_ratio,activation_type="single",info_mode=1,\
    prg=prg__LCG(34.55,-112.33,5433,91766.66),prg2 = prg__LCG(13.41,3+4/3,-55.5,4610.55),\
    verbose=False):

    G = generate_directed_implication_path(num_nodes,extra_edge_ratio,prg,start_node_idn=0)
    node_value_range_map = {i:[1,50] for i in range(num_nodes)} 

    optdi = ObjectivePathTypeDI.generate_instance(G,node_value_range_map,ratio_indirect_activation,\
        prior_dependency_ratio,activation_type,prg)

    dipn = DIPathNavigator.from_PathTypeDI(optdi,prg2)
    dipn.set_backtrack_pr(0.1,0.2)
    dipnh = DIPathNavigatorHandler(optdi,dipn,info_mode=info_mode,verbose=verbose) 
    return dipnh 

### lone file test 
"""
py -m tests.test_hg_obj_path_op 
""" 
###
class DIPathNavigatorClass(unittest.TestCase):

    """
    check for correct pending failure 
    """
    def test__DIPathNavigator__next__case_1(self):

        num_nodes = 10  
        extra_edge_ratio = 0.0 
        ratio_indirect_activation = 1.0  
        prior_dependency_ratio = 0.2 

        prg = prg__LCG(224.55,-232.33,433,1766.66)
        prg2 = prg__LCG(4424.55,-1232.33,1433,55766.66)

        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,prior_dependency_ratio,\
            prg=prg,prg2=prg2)


        dipn = dipnh.dipn 
        optdi = dipnh.ptdi 

        #while not dipn.fin_stat:
        for i in range(6): 
            #print("iter {}".format(i))
            #print(optdi.failure_record_map)
            next(dipnh)
            i += 1 

        assert dipn.loc == 4 
        next(dipnh)
        assert dipn.loc == 4 

        for i in range(7): 
            next(dipnh) 
        assert dipn.loc == 7
        next(dipnh)
        assert dipn.loc == 6 


    """
    check for correct pending failure 
    """
    def test__DIPathNavigator__next__case_2(self): 

        num_nodes = 50  
        extra_edge_ratio = 0.0# 0.05 
        ratio_indirect_activation = 0.75 
        prior_dependency_ratio = 0.5 

        prg = prg__LCG(79.55,-11232.33,5433,-99766.66)
        prg2 = prg__LCG(8424.55,-5232.33,1433,5566.66)

        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,prior_dependency_ratio,\
            prg=prg,prg2=prg2,verbose=False)
        dipn = dipnh.dipn 

        for i in range(975): 
            #print("iter {}".format(i))
            #print("DIPN: ",dipnh.dipn.loc) 
            next(dipnh) 
            #print("FAILURE RECORD MAP")
            #print(dipnh.ptdi.failure_record_map)

        assert dipn.loc == 32 
        next(dipnh)
        assert dipn.loc == 3 

    """
    check for correct number of iterations until completion 
    """
    def test__DIPathNavigator__next__case_3(self): 
        num_nodes = 8 #20  
        extra_edge_ratio = 0.0 #0.3 

        ratio_indirect_activation = 1.0 # 0.3 
        prior_dependency_ratio = 0.3 
        info_mode = 1 
        activation_type = "single" #"single" 

        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,info_mode) 
        dipn = dipnh.dipn 
        optdi = dipnh.ptdi 

        i = 0 

        while not dipn.fin_stat:
            #print("iter {}".format(i))
            #print(optdi.failure_record_map)
            next(dipnh)
            i += 1 
        assert i == 23, "got {}".format(i)  

        num_nodes = 13 
        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,info_mode)
        dipn = dipnh.dipn 
        optdi = dipnh.ptdi 
        i = 0 

        while not dipn.fin_stat:
            #print("iter {}".format(i))
            #print(optdi.failure_record_map)
            next(dipnh)
            i += 1 
        assert i == 801, "got {}".format(i)  

    """
    check for correct pending failure 
    """
    def test__DIPathNavigator__next__case_4(self): 
        num_nodes = 14 #20  
        extra_edge_ratio = 0.2 #0.3 

        ratio_indirect_activation = 1.0 # 0.3 
        prior_dependency_ratio = 0.3 
        info_mode = 0 
        activation_type = "linexp" #"single" 

        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,info_mode) 
        dipn = dipnh.dipn 
        optdi = dipnh.ptdi 

        i = 0 
        while not dipn.fin_stat:
            #print("iter {}".format(i))
            #print(optdi.failure_record_map)
            next(dipnh)
            i += 1 
        assert i == 264, "got {}".format(i)  

        info_mode == 1 
        dipnh = DIPathNavigator__sample__13(num_nodes,extra_edge_ratio,ratio_indirect_activation,\
            prior_dependency_ratio,activation_type,info_mode) 
        dipn = dipnh.dipn 
        optdi = dipnh.ptdi 
        i = 0 
        while not dipn.fin_stat and i < 5000:
            #print("iter {}".format(i))
            #print(optdi.failure_record_map)
            next(dipnh)
            i += 1 

        assert dipn.loc == 6 


if __name__ == '__main__':
    unittest.main()
