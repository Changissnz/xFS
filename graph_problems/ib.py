from quant.default_graph_introproc import * 

"""
Introspection Bot observes a graph 'introspection' process. The graphs of interest 
for this bot are simple, undirected graphs. 
NOTE: the code logistics for directed graphs take a significantly long time to process 
    method<graph_to_one_component>, due to dependency on  
    <morebs2.graph_basics.GraphComponentDecomposition>, a data structure that is not 
    suited for directed graphs of more than 50 nodes. 

Introspection process is based on breadth-first search or depth-first search graph 
traversal. There are two variants of introspection process: 
(I) `reactive`: uses class<ReactiveGraphIntrospectorTypeCNO>; allows for nodes and edges to be 
    added or subtracted to graph of pertinence. 
(II) `varmem`: uses class<StaticGraphIntrospectorTypeCNO>; allows for erasures of memory of edges 
    traveled and parent nodes of traversal to next nodes (neighbors). 

In the `reactive` type, the changes are of nodes and edges. In the `varmem` type, the changes 
are of traversal memory. These changes, in turn, alter the course of BFS|DFS traversal, yielding 
different results on shortest paths between nodes, cyclical node outputs, and travel costs.
These changes are decided on by the PRNG of the introspection process. 

To generate an instance of this bot, an important variable is the graph description: 
(I) "reactive",is_rule_constant:bool,maintain_connectivity:bool. 
(II) "varmem",edges_can_be_forgotten:float,ref_nodes_can_be_repeated:float,
    nodes_are_weighted:bool,edges_are_weighted:bool. 

Class variable<sequence> is a list, with elements of one of two forms: 
(I) (start reference node,number of traversals) 
(II) (*,number of traversals)
    * := PRNG selection of reference node in graph. 

Variable<sequence> specifies the primary steps of introspection. For every element, 
introspection processes a BFS|DFS from the starting reference node. Variables such as 
The output is 
(I) node output sequence: always even-numbered in length, 
    [0] node traveled to 
    [1] cyclical output of node 
(II) map of shortest paths, node -> {sequence of shortest paths}. 

The pertaining sequence Q of elements (node output sequence, map of shortest paths) is 
the output from the main method of this bot. 

The class variable<rlog> is the sequence Q_r, calculated using the introspector's original 
PRNG. The class variable<ilog> is another sequence Q_i, calculated by either the introspector's 
original PRNG, but with possibly different real numbers than the ones used to calculate Q_r, 
or another PRNG, set with method<set_prg>. 
""" 
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

    """
    main method 
    """
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