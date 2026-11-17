from graph_models.label2int_map import * 
import unittest

### lone file test 
"""
py -m tests.test_label2int_map
"""
###
class Label2IntMapClass(unittest.TestCase):

    """
    checks for deletion of node 10 after one jam. 
    """
    def test__Label2IntMap__add_element__case_1(self):

        starting_label_set = {5,6,12,31,23423} 
        s_func = DEFAULT_L2INT_STRINGIZE_FUNC
        s_inv = DEFAULT_L2INT_DESTRINGIZE_FUNC(str,True)

        L0 = Label2IntMap(starting_label_set,\
            stringize_func=s_func,\
            str_inversion_func=s_inv,\
            enable_bimap=False)

        new_elements = [(5,6,12),\
            (5,12),"abx"] 

        for x in new_elements: L0.add_element(x) 

        results = []
        for x in new_elements: 
            results.append((x,L0.element_to_int_label(x)))
        assert results == [((5, 6, 12), 5), ((5, 12), 6), ('abx', 7)]

        results2 = [] 
        for q in range(8): 
            results2.append((q,L0.int_label_to_element(q))) 

        assert results2 == [(0, {'5'}), (1, {'6'}), (2, {'23423'}), \
            (3, {'12'}), (4, {'31'}), (5, {'(5', ' 12)', ' 6'}), \
            (6, {'(5', ' 12)'}), (7, {'abx'})]
        return 

if __name__ == '__main__':
    unittest.main()