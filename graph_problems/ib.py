from quant.default_graph_introproc import * 

class IntrospectionBot(DefaultGraphIntrospectorProcess): 

    def __init__(self,introspector,sequence,num_minpaths):  
        self.introspector = introspector
        self.introspector_ = deepcopy(introspector) 

        self.sequence = sequence  
        self.num_minpaths = num_minpaths
        self.rlog = None 
        self.ilog = None 
        self.run(is_ref=True)
        return

    def run(self,is_ref:bool):
        node_output_sequence, X = super().run(self.sequence,self.num_minpaths)

        if not is_ref: 
            self.rlog = (node_output_sequence,X)
        else: 
            self.ilog = (node_output_sequence,X) 

        prg = self.introspector.prg 
        self.introspector = deepcopy(self.introspector_) 
        self.set_prg(prg) 

    @staticmethod 
    def generate_instance(introspector_description,is_bfs:bool,ascending_priority:bool,\
        sequence,num_minpaths:int,prg):  

        di = DefaultGraphIntrospectorProcess.generate_instance(introspector_description,is_bfs,\
            ascending_priority,prg)
        return IntrospectionBot(di.introspector,sequence,num_minpaths)