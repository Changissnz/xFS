from quant.mvec_agent import *
import unittest

def MVTrackingGroupTypeSO__sample_USUK(): 
    num_agents = 7 
    vector_bound_range = np.array([\
        [12,39],\
        [45,79],\
        [0,32],\
        [-21,112],\
        [89,205]])

    prg = prg__LCG(45,45,31,1156.66)
    weight_range = [10,45]
    point_dispersal_max_float = 0.005 

    q = MVTrackingGroupTypeSO.generate_instance(num_agents,\
        vector_bound_range,weight_range,\
        point_dispersal_max_float,prg)

    return q 

### lone file test 
"""
py -m tests.test_mvec_agent 
"""
class MVTrackingGroupTypeSOClass(unittest.TestCase):

    def test__MVTrackingGroupTypeSO__move_one__case_1(self): 
        q = MVTrackingGroupTypeSO__sample_USUK() 

        target_loc = np.zeros((5,))
        partial_derivative = np.array([3,14,56,93,110]) 
        total_derivative_sum = np.sum(partial_derivative) + 5 

        # check for predicted location being close enough to actual 
        q.move_one(target_loc,partial_derivative,\
                total_derivative_sum,ext_prg=prg__constant(x=0))

        assert np.all(q.predicted_next_location == \
            np.array([3.69491,17.8506,57.98597,95.82071,105.64781])) 

        # calculation of the symmetric imbalance 
        assert q.cumulative_balance == 35.47622 

    def test__MVTrackingGroupTypeSO__move_one__case_2(self): 
        q = MVTrackingGroupTypeSO__sample_USUK() 
        
        target_loc = np.zeros((5,))
        partial_derivative = np.array([133,4,556,3,-110]) 

        # check for predicted location being close enough to actual 
        remaining_sum = 0.005 
        total_derivative_sum = np.sum(partial_derivative) + remaining_sum 

        q.move_one(target_loc,partial_derivative,\
                total_derivative_sum,ext_prg=prg__constant(x=0))

        x = euclidean_point_distance(q.predicted_next_location,\
            partial_derivative)

        assert x < remaining_sum * 2 

        # check for balance log 
        prgv = prg__single_to_nvec(q.predictor.prg,5) 
        total_derivative_sum = 50 
        for _ in range(9): 
            target_loc = prgv() 
            partial_derivative = prgv()
            q.move_one(target_loc,partial_derivative,total_derivative_sum)  
        assert len(q.balance_log) == 10 
        assert q.cumulative_balance == 507.68827



if __name__ == '__main__':
    unittest.main()