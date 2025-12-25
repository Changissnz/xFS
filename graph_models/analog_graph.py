from .analog_schemes_aux import * 

class AnalogGraph: 

    def __init__(self,reference_graph,isomap): 
        assert type(reference_graph) == defaultdict 
        assert type(isomap) == dict
        self.reference_graph = reference_graph 
        self.isomap = isomap  
        return 

    def draw_analogy_to(self,ag:AnalogGraph): 
        assert type(ag) == AnalogGraph 
        
        return -1 

class AnalogGraphGroup: 

    def __init__(self,analog_graphs,isomaps): 
        assert len(analog_graphs) > 1 
        assert len(analog_graphs) == len(isomaps) + 1 

        for x in analog_graphs: assert type(x) == AnalogGraph
        for x in isomaps: assert type(x) == dict 
        self.analog_graphs = analog_graphs 
        self.isomaps = isomaps 
        return

    
