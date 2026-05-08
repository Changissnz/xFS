"""
File contains a process that operates a <GraphIntrospectorTypeCNO>. 
For simplification in instantiation, generator scheme for 
<GraphIntrospectorTypeCNO> rests on default variables.
"""  
from .reactive_graph_introspector import * 
from .static_graph_introspector import * 
from graph_models.graph_gen import * 

DEFAULT_INTROSPECTOR_INIT_NODESIZE_RANGE = [25,300] 
DEFAULT_INTROSPECTOR_NODECHANGE_ABSMAX = 8
DEFAULT_INTROSPECTOR_EDGECHANGE_ABSMAX = 8 
DEFAULT_INTROSPECTOR_PERIOD_RANGE = [1,8] 
DEFAULT_INTROSPECTOR_CYCLE_LENGTH_RANGE = [3,11] 
DEFAULT_INTROSPECTOR_NODE_WEIGHT_RANGE = [1.,6.]
DEFAULT_INTROSPECTOR_EDGE_WEIGHT_RANGE = [1.,6.]

class DefaultGraphIntrospectorProcess: 

    def __init__(self,introspector): 
        assert issubclass(type(introspector),GraphIntrospectorTypeCNO)  
        self.introspector = introspector 
        return 

    def set_prg(self,prg): 
        self.introspector.set_prg(prg)
        return

    def run_(self,ref_node,num_rounds): 
        # case: node does not exist 
        if ref_node not in self.introspector.G: 
            return [] 

        self.introspector.set_ref_node(ref_node) 
        c = 0 

        node_output_sequence = []  
        while not self.introspector.introspector.fin_stat and c < num_rounds: 
            M,ref,traversal_cost = next(self.introspector)

            k = sorted(M.keys()) 
            M_ = [] 
            for k_ in k: 
                M_.extend([k_,M[k_]]) 
            node_output_sequence.extend(M_) 
            c += 1 
        return node_output_sequence

    """
    sequence := list, all elements are one of 
        (start reference node,number of traversals) 
        XOR 
        (*,number of traversals)

        * := PRNG selection of reference node in graph. 

    num_minpaths := int, max number of min. paths per node. 
    """
    def run(self,sequence,num_minpaths):
        assert len(sequence) > 0 

        node_output_sequence = [] 
        for s in sequence: 
            s0,s1 = None,None 
            if type(s) != int: 
                assert len(s) == 2 
                s0,s1 = s[0],s[1] 
            else: 
                k = sorted(self.introspector.G.keys()) 
                i = int(self.introspector.prg()) % len(k)
                s0 = k[i] 
                s1 = s 
            nos = self.run_(s0,s1) 
            node_output_sequence.append(nos) 

        X = self.introspector.output_minpaths(num_minpaths) 
        return node_output_sequence, X 

    """
    introspector_description := 
        ("reactive",is_rule_constant:bool,maintain_connectivity:bool) 
            OR 
        ("varmem",edges_can_be_forgotten:float,ref_nodes_can_be_repeated:float,nodes_are_weighted:bool,edges_are_weighted:bool) 

    is_dsg := ?is directed simple graph? 
    is_bfs := ?is breadth-first search? 
    ascending_priority := ?order next nodes for travel by ascending order? 
    """
    @staticmethod 
    def generate_instance(introspector_description,is_bfs:bool,ascending_priority:bool,prg):  

        assert introspector_description[0] in {"reactive","varmem"} 

        vertex_degree = modulo_in_range(int(prg()),DEFAULT_INTROSPECTOR_INIT_NODESIZE_RANGE)

        edge_connectivity = 0.02 
        if vertex_degree < 20: 
            edge_connectivity = modulo_in_range(prg(),[0.02,0.2]) 
        elif vertex_degree < 100: 
            edge_connectivity = modulo_in_range(prg(),[0.007,0.07])  
        else: 
            edge_connectivity = modulo_in_range(prg(),[0.007,0.045]) 

        print("generating {},{}".format(vertex_degree,edge_connectivity)) 
        G = GraphGen(is_dsg=False,is_realtime_gen=False,vertex_degree=vertex_degree,\
            edge_connectivity=edge_connectivity,prg=prg) 
        G.full_run()

        print("TO ONE COMPONENT") 
        G = graph_to_one_component(G.d,prg) 
        print("generated graph of {} nodes".format(vertex_degree))
        
        if introspector_description[0] == "reactive": 
            assert len(introspector_description) == 3  

            n0 = modulo_in_range(int(prg()),[-DEFAULT_INTROSPECTOR_NODECHANGE_ABSMAX,0])
            n1 = modulo_in_range(int(prg()),[1,DEFAULT_INTROSPECTOR_NODECHANGE_ABSMAX+1]) 
            nodechange_range = [n0,n1]

            e0 = modulo_in_range(int(prg()),[-DEFAULT_INTROSPECTOR_EDGECHANGE_ABSMAX,0])
            e1 = modulo_in_range(int(prg()),[1,DEFAULT_INTROSPECTOR_EDGECHANGE_ABSMAX+1]) 
            edgechange_range = [e0,e1] 

            maintain_connectivity = introspector_description[2] 
            is_rule_constant = introspector_description[1]
            S = ReactiveGraphIntrospectorTypeCNO.generate_instance(\
                G,nodechange_range,edgechange_range,DEFAULT_INTROSPECTOR_PERIOD_RANGE,\
                maintain_connectivity,is_rule_constant=is_rule_constant,node_weight_range=None,\
                is_dsg=False,is_bfs=is_bfs,ascending_priority=ascending_priority,\
                cycle_length_range=DEFAULT_INTROSPECTOR_CYCLE_LENGTH_RANGE,prg=prg) 
        else: 
            assert len(introspector_description) == 5

            if introspector_description[3]: 
                node_weight_range = DEFAULT_INTROSPECTOR_NODE_WEIGHT_RANGE
            else: 
                node_weight_range = None 

            if introspector_description[4]: 
                edge_weight_range = DEFAULT_INTROSPECTOR_EDGE_WEIGHT_RANGE
            else: 
                edge_weight_range = None 

            edges_can_be_forgotten = introspector_description[1] 
            ref_nodes_can_be_repeated = introspector_description[2] 
            S = StaticGraphIntrospectorTypeCNO.generate_instance(G,\
                node_weight_range=node_weight_range,edge_weight_range=edge_weight_range,\
                is_dsg=is_dsg,is_bfs=is_bfs,ascending_priority=ascending_priority,\
                cycle_length_range=DEFAULT_INTROSPECTOR_CYCLE_LENGTH_RANGE,\
                edges_can_be_forgotten=edges_can_be_forgotten,\
                ref_nodes_can_be_repeated=ref_nodes_can_be_repeated,\
                prg=prg)
        print("S: ",S)
        return DefaultGraphIntrospectorProcess(S) 