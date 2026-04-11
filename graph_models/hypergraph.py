from .shortest_paths import * 
from .graph_gen import * 
from morebs2.numerical_generator import prg_decimal,prg_choose_n

def is_valid_hypergraph(hg_rep:defaultdict,node2nodeset_map): 
    assert set(hg_rep.keys()) == set(node2nodeset_map.keys())

    # check that each nodeset is unique
    C = [] 
    for v in node2nodeset_map.values(): 
        if v in C: return False 
        C.append(v) 
    
    # check node intersection between every hypergraph neighbor 
    hg_nodes = set(hg_rep.keys())

    for n in hg_nodes:
        nodeset = node2nodeset_map[n]
        neighbors = hg_rep[n] 

        for n2 in neighbors: 
            nodeset2 = node2nodeset_map[n2] 
            inter = nodeset.intersection(nodeset2) 
            if len(inter) == 0: 
                return False 

    return True 

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

    def base_node_to_H_nodeset(self,b): 
        S = set() 
        for k,v in self.node2nodeset.items(): 
            if b in v: 
                S |= {k} 
        return S 

    def H_nodeset_intersection(self,n0,n1): 
        q0 = self.node2nodeset[n0] 
        q1 = self.node2nodeset[n1] 
        return q0.intersection(q1)  

    def H_node_density_map(self): 
        return {k:len(self.node2nodeset[k]) for k in self.rep.keys()} 

    def nodepair_exists(self,H_node,base_node): 
        if H_node not in self.rep: return False 

        if base_node not in self.node2nodeset[H_node]: 
            return False 

        return True 

    def select_nodepairs_with_PRNG(self,num_pairs,ext_prg): 

        hg_nodes = sorted(self.rep.keys()) 

        nodepairs = [] 
        for _ in range(num_pairs):
            i = int(ext_prg()) % len(hg_nodes) 
            h_node = hg_nodes[i] 

            nodeset = sorted(self.node2nodeset[h_node]) 
            i = int(ext_prg()) % len(nodeset) 
            label = nodeset[i] 

            nodepairs.append((h_node,label))
        return nodepairs

    """
    NOTE: number of base nodes, `approx_base_nodesize`, must be at least equal to that of HyperGraph nodesize. 

    NOTE: number of base nodes in generated HyperGraph does not have to equal  `approx_base_nodesize`.

    NOTE: generation scheme can exceed upper bound of `node2nodeset_sizerange`. 
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
        G = graph_to_one_component(G,prg) 

        # generate the node2nodeset map 
        base_nodes = [i for i in range(approx_base_nodesize)] 
        base_nodes = prg_seqsort(base_nodes,prg)
        
        node2nodeset_map = dict() 
        index = 0 

        S = sorted(G.keys()) 
        for s in S: 
            base_nodes,new_nodes,index = HyperGraph.generate_nodeset_for_HyperGraph_node__neighbors_inc(\
                G,node2nodeset_map,base_nodes,s,index,node2nodeset_sizerange,prg) 
            node2nodeset_map[s] = new_nodes  

        return HyperGraph(G,node2nodeset_map)

    """
    auxiliary method for method<generate_instance> 
    """
    @staticmethod 
    def generate_nodeset_for_HyperGraph_node__neighbors_inc(G,node2nodeset_map,
        base_nodes,k,index,node2nodeset_sizerange,prg): 

        # get all neighbors that have already been set into graph 
        q = set(node2nodeset_map.keys()).intersection(G[k]) 

        # case: no neighbors, add new nodes 
        if len(q) == 0: 
            return HyperGraph.generate_nodeset_for_HyperGraph_node__new_nodes(\
                node2nodeset_map,base_nodes,k,index,node2nodeset_sizerange,prg) 

        q = sorted(q) 

        # fetch nodesets for each present neighbor 
        q2 = [] 
        for q_ in q: 
            nodeset = node2nodeset_map[q_] 
            q2.append([q_,sorted(nodeset)])  
        neighbor_inter_stat = {q_:False for q_ in q} 

        ## scheme 1: results in nodeset sizes that might exceed upper bound of 
        ##           node2nodeset_sizerange
        # iterate through each present neighbor, and select at least 
        # 1 node from it.
        the_nodeset = set() 
        for q_ in q2: 
            x = q_[1] 
            if len(x) == 0: 
                continue 

            if len(x) == 1: 
                rx = [1,2] 
            else: 
                rx = [1,len(x)]

            num_inter = modulo_in_range(int(prg()),rx) 
            prg_ = prg__single_to_int(prg)
            intersect = prg_choose_n(x,num_inter,prg_,is_unique_picker=True) 
            intersect = set(intersect)
            the_nodeset |= intersect 

            for q2_ in q2: 
                i2 = intersect.intersection(set(q2_[1])) 
                q2_[1] = sorted(set(q2_[1]) - i2)


        # check that `the_nodeset` is unique 
        is_unique = True 
        for q_ in q: 
            nodeset = node2nodeset_map[q_] 
            if nodeset == the_nodeset: 
                is_unique = False 
                break 

        # case: not unique, add new nodes 
        if not is_unique: 
            base_nodes,new_nodes,index = HyperGraph.generate_nodeset_for_HyperGraph_node__new_nodes(\
                node2nodeset_map,base_nodes,k,index,node2nodeset_sizerange,prg) 
            the_nodeset |= new_nodes 

        # case: nodeset falls under lower threshold for node2nodeset size; add more 
        elif len(the_nodeset) < node2nodeset_sizerange[0]: 
            base_nodes,new_nodes,index = HyperGraph.generate_nodeset_for_HyperGraph_node__new_nodes(\
                node2nodeset_map,base_nodes,k,index,node2nodeset_sizerange,prg) 
            the_nodeset |= new_nodes 
        
        return base_nodes,the_nodeset,index 

    """
    auxiliary method for method<generate_nodeset_for_HyperGraph_node__neighbors_inc> 
    """ 
    @staticmethod 
    def generate_nodeset_for_HyperGraph_node__new_nodes(node2nodeset_map,base_nodes,k,index,\
        node2nodeset_sizerange,prg): 

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

        is_duplicate = False 
        for v in node2nodeset_map.values(): 
            if q == v: 
                is_duplicate = True 
                break 

        # case: duplicate nodeset, iterate and try another. 
        if is_duplicate: 
            return HyperGraph.generate_nodeset_for_HyperGraph_node__new_nodes(node2nodeset_map,\
                base_nodes,k,index,node2nodeset_sizerange,prg) 

        return base_nodes,q,index  