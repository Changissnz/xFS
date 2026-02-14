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

    """
    main method #1 
    """
    # NOTE: not guaranteed to satisfy `length_min_threshold`, in cases where there 
    #       are not options to extend a path past its current tail. 
    #       The `stasis_count` variable breaks out of possible infinite loops. 
    def one_path(self,target,roundabout_first:bool=False,length_min_threshold = 0): 
        num_segments = modulo_in_range(int(self.prg()),self.num_segment_range)

        p_ = None
        p = self.one_path_(target,num_segments,roundabout_first)
        l = len(p) - 1  
        stat = length_min_threshold > l 
        go_backward = True 

        I = self.possible_intermediaries(target)
        stasis_count = -1 
        l_ = len(p) - 1 
        while stat: 
            l = len(p) - 1

            if l == l_: 
                stasis_count += 1 
            if stasis_count >= 15: break 
            l_ = l 

            stat = length_min_threshold > l 
            if not stat: continue 

            t = p.tail() 
            if go_backward: 
                p2 = self.backward_append(t,I)
                if type(p2) == type(None): break 
                p_ = deepcopy(p)
                p.add_path(p2) 
            else: 
                I = prg_seqsort(sorted(I),prg__single_to_int(self.prg))
                i_ = None 
                q = []  
                for i in I: 
                    q_ = self.node_in_target_paths(i,t) 
                    if len(q_) == 0: continue 
                    i_ = i 
                    q = q_
                    break 

                if len(q) == 0: 
                    return p_ 
                else: 
                    j = int(self.prg()) % len(q) 
                    p2 = q[j] 
                    k = p2.first_occurrence(i_)
                    p2 = p2.tail_subpath(k,True).invert() 
                    p.add_path(p2) 

            go_backward = not go_backward

        t = p.tail() 
        if t != target: 
            px = self.node_in_target_paths(t,target) 
            j = int(self.prg()) % len(px) 
            px = px[j] 
            j = px.first_occurrence(t)
            px = px.tail_subpath(j,True) 
            p.add_path(px)
        return p 

    def one_path_(self,target,num_segments,roundabout_first):
        p = NodePath.preload([],[]) 

        nth_source = None 
        I = self.possible_intermediaries(target)

        # add the first segment 
        if roundabout_first: 
            p.add_path(self.select_one_path_to_target(target)) 
        else: 
            i = int(self.prg()) % len(I) 
            t = sorted(I)[i] 
            p = self.select_one_path_to_target(t) 
        num_segments -= 1 

        if num_segments == 0: 
            return p 

        nth_source = p.tail() 

        # append remaining segments 
        while num_segments > 1: 
            p2 = self.next_segment(nth_source,I - {nth_source})
            if type(p2) == type(None): 
                break 
            
            p.add_path(p2)
            nth_source = p.tail() 
            if nth_source == target: return p 

            num_segments -= 1 

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

    def backward_append(self,target,intersection_nodes): 
        I = prg_seqsort(sorted(intersection_nodes),prg__single_to_int(self.prg)) 
        for n in I: 
            q = self.node_in_target_paths(n,target)
            if len(q) == 0: continue 

            j = int(self.prg()) % len(q)
            p = q[j]
            k = p.first_occurrence(n)
            return p.tail_subpath(k,True).invert() 
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

    #-------------------------------------------------------------------------- 

    # TODO: not fully tested yet. 
    """
    main method #2 

    if G is the reference graph for the paths given, uses G to check 
    if backtraced paths are valid. Otherwise, assumes reference graph 
    is undirected. 
    """
    def induce_paths_from_other_references(self,G:defaultdict): 
        D = dict() 

        keys = sorted(self.P.keys())
        for k in keys:
            #print("k: ",k) 
            v = self.P[k]  
            for v_ in v: 
                D = self.path_induction_by_backtrace(G,D,v_)  
        return D 

    def path_induction_by_backtrace(self,G,D,p): 

        def check_edge(s,t): 
            if type(G) != type(None): 
                if s not in G: return False 
                if t not in G[s]: return False 
            return True 
        
        p_ = p.invert() 

        for i in range(len(p_)): 
            q = p_.head_subpath(i,True)
            st = (q.head(),q.head())
            D[st] = q 
        
            for j in range(1,len(q)): 
                if not check_edge(q[j-1],q[j]): 
                    print("edge {},{} does not exist".format(q[j-1],q[j]))
                    break 
                
                st = (q.head(),q[j]) 
                subq = q.head_subpath(j,True)
                if st not in D: 
                    D[st] = subq 
                else: 
                    c = D[st].cost() 
                    if subq.cost() < c: 
                        D[st] = subq 
        return D 

#-------------------------------------------------------------------------------

class PathSelector: 

    def __init__(self,P,st_nodemap):
        # source node -> target node 
        self.st_nodemap = st_nodemap
        return
        