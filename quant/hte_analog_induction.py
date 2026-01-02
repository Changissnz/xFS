from graph_models.analog_graph import *

class HTEAnalogInducer:

    """
    ref_threat_set := set, of node identifiers for `ref_graph`. 
    next_graph_hyp_map := ref threat node -> (next graph center node,next graph radius) 
    """
    def __init__(self,ref_graph,next_graph,ref_threat_set,next_graph_hyp_map,\
        isomorphic_subgraph_radius_range=DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE,\
        prg = None): 
        assert type(ref_graph) == defaultdict
        assert type(next_graph) == defaultdict
        assert type(ref_threat_set) == set
        assert type(next_graph_hyp_map) == dict

        assert is_valid_range(isomorphic_subgraph_radius_range,True,False)
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        self.ref_graph = ref_graph 
        self.next_graph = next_graph 
        self.ref_threat_set = ref_threat_set
        self.next_graph_hyp_map = next_graph_hyp_map
        self.isomorphic_subgraph_radius_range = isomorphic_subgraph_radius_range
        self.prg = prg 
        return

    @staticmethod
    def generate_instance(ref_graph,next_graph,ref_threat_map,\
        isomorphic_subgraph_radius_range=DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE,\
        hyp_node_distance_range=[0,3],hyp_node_radius_range=None,prg=None): 

        assert is_valid_range(hyp_node_distance_range,True,False)
        if type(prg) == type(None): 
            prg = default_std_Python_prng() 
        assert type(prg) in {MethodType,FunctionType}

        qsf = QuickSubgraphFetcher(next_graph)
        next_graph_hyp_map = {}
        for t,t2 in ref_threat_map.items(): 
            r = modulo_in_range(int(prg()),hyp_node_distance_range)
            sg = qsf.subgraph(t2,r)
            node_candidates = sorted(sg.keys()) 

            i = int(prg()) % len(node_candidates)
            n2 = node_candidates[i] 

            if type(hyp_node_radius_range) != type(None): 
                r2 = modulo_in_range(int(prg()),hyp_node_radius_range)
            else: 
                r2 = r 
            next_graph_hyp_map[t] = (n2,r2) 

        return HTEAnalogInducer(ref_graph,next_graph,set(ref_threat_map.keys()),\
            next_graph_hyp_map,isomorphic_subgraph_radius_range,prg)  

    def possible_threat_analogs(self,ref_threat_node): 
        assert ref_threat_node in self.ref_graph 
        assert ref_threat_node in self.next_graph_hyp_map

        # get subgraph for next graph 
        center_suspect,radius = self.next_graph_hyp_map[ref_threat_node]  
        ##assert radius >= 2 
        qsf = QuickSubgraphFetcher(self.next_graph)
        sg_other = qsf.subgraph(center_suspect,radius)

        # get subgraph for ref 
        r2 = modulo_in_range(int(self.prg()),self.isomorphic_subgraph_radius_range)
        qsf2 = QuickSubgraphFetcher(self.ref_graph) 
        sg_ref = qsf2.subgraph(ref_threat_node,r2)

        mg,mg2 = MicroGraph(sg_other),MicroGraph(sg_ref) 
        q = mg.subgraph_isomorphism(mg2,all_iso=True,size_limit=200,search_candidate_limit=None)

        suspect_nodes = set() 
        for q_ in q: 
            d = {v:k for k,v in q_} 
            if ref_threat_node in d: 
                suspect_nodes |= {d[ref_threat_node]}
        return suspect_nodes