from quant.cee_map import * 
import unittest 

def PRClassExpectedEffectTypeHL__sample__UNO(): 

    hg_nodesize = 10 
    hg_connectivity = 0.3 
    is_directed = False 
    base_nodesize = 30 
    node2nodeset_sizerange = [2,6]  
    prg = prg__LCG(43,-5444.6,19.55,4520.77) 

    hg = HyperGraph.generate_instance(hg_nodesize,\
        hg_connectivity,is_directed,base_nodesize,\
        node2nodeset_sizerange,prg)
    
    
    PRC = PRClassExpectedEffectTypeHL(hg,prg)
    return PRC 

"""
py -m tests.test_cee_map
"""
class PRClassExpectedEffectTypeHLClass(unittest.TestCase):

    def test__PRClassExpectedEffectTypeHL__case1(self):
        PRC = PRClassExpectedEffectTypeHL__sample__UNO() 
        hg = PRC.hg 
        prg = PRC.prg 

        # check that paths have equal tails. 
        base_nodes = sorted(hg.base_nodeset())
        h_nodes = prg_seqsort(sorted(hg.rep.keys()),prg) 

        for h in h_nodes: 
            # choose a base node in H-node 
            q = sorted(hg.node2nodeset[h])
            i = int(prg()) % len(q)
            n = q[i]

            tails = set() 

            p = PRC.categorical_label2label_path(n,n,h,prg) 
            assert len(p) == 1 
            tail = NodePath_sequence_to_1d_sequence(p)[-1] 

            for b in base_nodes: 
                p2 = PRC.categorical_label2label_path(b,n,h,prg)  
                tail2 = NodePath_sequence_to_1d_sequence(p2)[-1]
                assert tail == tail2 

        # check all that label identities yield paths of one segment
        for b in base_nodes: 
            # choose a base node in H-node 
            q = sorted(hg.base_node_to_H_nodeset(b))
            i = int(prg()) % len(q)
            h = q[i]

            p = PRC.categorical_label2label_path(b,b,h,prg) 
            assert len(p) == 1 
        return 

if __name__ == '__main__':
    unittest.main()