from .shortest_paths import * 
from .graph_gen import * 
from morebs2.numerical_generator import prg_decimal

# TODO: test this. 
class HyperGraph:

    def __init__(self,rep:defaultdict,node2nodeset_map): 
        assert type(rep) == defaultdict 
        assert type(node2nodeset_map) in {dict,defaultdict}
        assert set(rep.keys()) == set(node2nodeset_map.keys()) 

        self.rep = rep 
        self.node2nodeset = node2nodeset_map 

    def base_nodeset(self): 
        q = [v for v in self.node2nodeset.values()] 
        return flatten_setseq(q) 

    """
    NOTE: number of base nodes, `approx_base_nodesize`, must be at least equal to that of HyperGraph nodesize. 

    NOTE: number of base nodes in generated HyperGraph does not have to equal  `approx_base_nodesize`.
    """
    @staticmethod 
    def generate_instance(hg_nodesize,hg_connectivity,is_directed:bool,approx_base_nodesize,node2nodeset_sizerange,prg):
        assert is_valid_range(node2nodeset_sizerange,True,False) 
        assert node2nodeset_sizerange[0] > 0 

        # generate the hypergraph repr. 
        is_realtime_gen = prg_decimal(prg,[0.,1.]) >= 0.5 
        G = GraphGen(is_directed,prg,is_realtime_gen,vertex_degree=hg_nodesize,\
            edge_connectivity=hg_connectivity,verbose=False)
        G.full_run() 
        G = G.d 


        # generate the node2nodeset map 
        base_nodes = [i for i in range(approx_base_nodesize)] 
        base_nodes = prg_seqsort(base_nodes,prg)
        
        node2nodeset_map = dict() 
        nodesets = [] 
        index = 0 

        def nodeset_for_node(base_nodes,k,index): 
            num_nodes = modulo_in_range(int(prg()),node2nodeset_sizerange)
            r = len(base_nodes) - (index + num_nodes)  
            q = None 
            if r < 0: 
                q = base_nodes[index:len(base_nodes)] 
                q = q + base_nodes[0:-r]
                base_nodes = prg_seqsort(base_nodes,prg)
                index = -r 
            else: 
                q = base_nodes[index:index+num_nodes] 
                index = index + num_nodes

            q = set(q)

            # case: duplicate nodeset 
            if q in nodesets:  
                return nodeset_for_node(k,index) 

            return base_nodes,q,index  

        S = sorted(G.keys()) 
        for s in S: 
            base_nodes,nodeset,index = nodeset_for_node(base_nodes,s,index)
            nodesets.append(nodeset) 
            node2nodeset_map[s] = nodeset 

        return HyperGraph(G,node2nodeset_map)