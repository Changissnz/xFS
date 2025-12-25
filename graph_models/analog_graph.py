from .analog_schemes_aux import * 

DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS = [2,6] 

# TODO: test this. 
class AnalogGraph: 

    def __init__(self,reference_graph,isomap,prg,isomorphic_subgraph_radius=DEFAULT_ANALOG_GRAPH_SUBGRAPH_RADIUS):  
        assert type(reference_graph) == defaultdict 
        assert type(isomap) == dict
        assert type(prg) in {MethodType,FunctionType} 
        assert is_valid_range(isomorphic_subgraph_radius,True,False)

        self.reference_graph = reference_graph 
        self.isomap = isomap 
        self.prg = prg 
        self.iso_sg_radius = isomorphic_subgraph_radius
        self.preproc() 
        return 

    def preproc(self): 
        self.sg_rad_fetcher = RadialSubgraphFetcher(self.reference_graph)
        return

    def draw_analogy_to(self,ag:AnalogGraph,exact_node_mapping_ratio:float): 
        assert type(ag) == AnalogGraph
        assert 0.0 <= exact_node_mapping_ratio <= 1.0 
        assert AnalogGraph.graph_is_analogical(self.reference_graph,ag.reference_graph,self.isomap) 
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
            mg2 = MicroGraph(ag)
            Q = mg2.subgraph_isomorphism(mg,all_iso=True,size_limit=200,search_candidate_limit=None) 

            # choose an isomorphism 
            index = int(self.prg()) % len(Q) 
            isomorphism = Q[index] 
            return isomorphism[n] 

        for k in self.isomap.keys(): 
            node_analogy[k] = analogical_node(k)
        return node_analogy

    def subgraph_for_node(self,n): 
        radius = modulo_in_range(int(self.prg()),self.iso_sg_radius)
        return self.sg_rad_fetcher.subgraph(n,radius)

    @staticmethod 
    def graph_is_analogical(ref_graph,analogy_graph,isomap): 
        for k,v in isomap.items(): 
            if k not in ref_graph: return False 
            if k not in analogy_graph: return False 
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

    
