from .analog_schemes_aux import * 
from .radial_subgraph import * 

DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE = [1,3] 

# NOTE: duplicate code? 
def dict_diff(ref_dict, other_dict): 
    c = 0 
    for k,v in ref_dict.items(): 
        if k not in other_dict: 
            c += 1 
            continue 
        v2 = other_dict[k] 
        if v != v2: 
            c += 1 
    return c 


# TODO: test this. 
class AnalogGraph: 

    def __init__(self,reference_graph,isomap,prg,isomorphic_subgraph_radius_range=DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS_RANGE):  
        assert type(reference_graph) == defaultdict 
        assert type(isomap) == dict
        assert type(prg) in {MethodType,FunctionType} 
        assert is_valid_range(isomorphic_subgraph_radius_range,True,False)

        self.reference_graph = reference_graph 
        # node of reference graph -> node of another graph
        self.isomap = isomap 
        self.prg = prg 
        self.iso_sg_radius_range = isomorphic_subgraph_radius_range
        self.preproc() 
        return 

    def preproc(self): 
        self.sg_rad_fetcher = RadialSubgraphFetcher(self.reference_graph)
        return

    def draw_analogy_to(self,G,exact_node_mapping_ratio:float): 
        assert type(G) == defaultdict
        assert 0.0 <= exact_node_mapping_ratio <= 1.0 
        assert AnalogGraph.graph_is_analogical(self.reference_graph,G,self.isomap) 
        candidates = sorted(self.isomap.keys()) 
        
        def prg_(): return int(self.prg())

        num_exact_mapping = ceil(len(candidates) * exact_node_mapping_ratio) 
        exact_nodes = prg_choose_n(candidates,num_exact_mapping,prg_,is_unique_picker=True)

        node_analogy = {} 

        def analogical_node(n): 
            if n in exact_nodes: 
                return self.isomap[n] 

            # fetch the subgraph 
            ref_sg = self.subgraph_for_node(n) 

            # calculate the isomorphisms
            mg = MicroGraph(ref_sg) 
            mg2 = MicroGraph(G)

            Q = mg2.subgraph_isomorphism(mg,all_iso=True,size_limit=200,search_candidate_limit=None) 
            if len(Q) == 0: return None 

            # choose an isomorphism 
            index = int(self.prg()) % len(Q) 
            isomorphism = Q[index] 
            isomorphism = {v:k for k,v in isomorphism} 

            if n not in isomorphism: return None 
            return isomorphism[n]

        for k in self.isomap.keys(): 
            x = analogical_node(k)
            if type(x) != type(None): 
                node_analogy[k] = x 

        return node_analogy

    def subgraph_for_node(self,n): 
        radius = modulo_in_range(int(self.prg()),self.iso_sg_radius_range)
        return self.sg_rad_fetcher.subgraph(n,radius)

    @staticmethod 
    def graph_is_analogical(ref_graph,analogy_graph,isomap): 
        for k,v in isomap.items(): 
            if k not in ref_graph: return False 
            if v not in analogy_graph: return False 
        return True 

class AnalogGraphGroup: 

    def __init__(self,analog_graphs,isomaps): 
        assert len(analog_graphs) > 1 
        assert len(analog_graphs) == len(isomaps) + 1 

        for x in analog_graphs: assert type(x) == AnalogGraph
        for x in isomaps: assert type(x) == dict 
        self.analog_graphs = analog_graphs 
        self.isomaps = isomaps 
        return