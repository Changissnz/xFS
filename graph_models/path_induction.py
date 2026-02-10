from .shortest_paths import * 
from morebs2.matrix_methods import is_valid_range
from morebs2.numerical_generator import modulo_in_range,prg__single_to_int

class PathInduction: 

    def __init__(self,reference,P,prg,num_segment_range): 
        assert type(prg) in {MethodType,FunctionType} 
        assert is_valid_range(num_segment_range,True,False) 
        assert num_segment_range[0] >= 1 

        self.reference = reference 
        # target node -> list<paths> 
        self.P = P 
        self.prg = prg 
        self.num_segment_range = num_segment_range 

    def one_path(self,target,roundabout_first:bool=False): 
        num_segments = modulo_in_range(int(self.prg()),self.num_segment_range)
        return self.one_path_(target,num_segments,roundabout_first)

    def one_path_(self,target,num_segments,roundabout_first):
        p = NodePath.preload([],[]) 

        nth_source = None 
        I = self.possible_intermediaries(target)
        if roundabout_first: 
            p.add_path(self.select_one_path_to_target(target)) 
        else: 
            i = int(self.prg()) % len(I) 
            t = sorted(I)[i] 
            p = self.select_one_path_to_target(t) 
        num_segments -= 1 

        nth_source = p.tail() 

        while num_segments > 1: 
            p2 = self.next_segment(nth_source,I - {nth_source})
            if type(p2) == type(None): 
                break 
            
            p.add_path(p2)
            nth_source = p.tail() 
            if nth_source == target: return p 

            num_segments -= 1 

        if len(p) == 0: 
            t = self.reference 
        else: 
            t = p.tail() 

        q = self.node_in_target_paths(t,target)
        assert len(q) > 0 

        i = int(self.prg()) % len(q) 
        p2 = q[i] 

        index = p2.first_occurrence(t)
        p2 = p2.tail_subpath(index,True)

        p.add_path(p2)
        return p 

    def next_segment(self,nth_source,intersection_nodes): 

        candidates = prg_seqsort(sorted(intersection_nodes),prg__single_to_int(self.prg)) 

        for c in candidates: 
            P = self.node_in_target_paths(nth_source,c)
            if len(P) == 0: continue 
            j = int(self.prg()) % len(P)
            p = P[j]
            i = p.first_occurrence(nth_source)
            p = p.tail_subpath(i,True)
            return p 

        return None 

    #---------------------------- calculations to find nodes available to be 
    #---------------------------- intermediaries to target nodes. 

    def possible_intermediaries(self,target_node): 
        if target_node not in self.P: 
            return None 

        S = self.involved_path_nodes_to_target(target_node) | {target_node}
        I = set()
        for s in S: 
            q = self.second_order_intermediaries(s,S - {s}) 
            if len(q) > 0: 
                I |= {s}
        return I 

    def second_order_intermediaries(self,intermediary,intersection_nodes): 
        assert intermediary in self.P 
        q = self.involved_path_nodes_to_target(intermediary)
        return q.intersection(intersection_nodes)

    def node_in_target_paths(self,node,target): 
        assert target in self.P 
        px = self.P[target] 
        q = [] 
        for p in px: 
            if node in p.p: 
                q.append(p) 
        return q  

    def involved_path_nodes_to_target(self,target_node): 
        px = self.P[target_node] 
        S = set()
        for p in px: 
            S |= set(p.p)
        S -= {self.reference,target_node} 
        return S 

    def select_one_path_to_target(self,target_node): 
        px = self.P[target_node] 
        i = int(self.prg()) % len(px) 
        return deepcopy(px[i])