from .micrograph import * 

GCS_SEARCH_TYPES = {"full neighbor fit- type 1",\
    "full neighbor fit- type 2",\
    "matching neighbor fit"}

"""
greatest common subgraph container is used to calculate
the subgraph shared by all members of arg<micrographs>.
"""
class GCSContainer:

    def __init__(self,micrographs,search_type="matching neighbor fit"):
        assert search_type in GCS_SEARCH_TYPES

        self.reference = None
        self.reference_index = None 
        self.ref_cs = None 
        # iterable<MicroGraph>
        self.mgs = micrographs

        ## each of the elements are of the form:
        # [0] SEQUENCE<INFO(m) in mgs> s.t. INFO(m) is 
        #           reference node -> target node
        # [1] edges of reference
        # [2] remaining nodes of component to be assigned
        # [3] remaining nodes of reference in component-set form
        self.cache = None
        self.cache_counter = 0

        # possible counterparts, used to improve each candidate solution
        self.pc = None
        self.search_type = search_type
        #
        return 

    """
    sets one MicroGraph in `mgs` as the reference.
    The reference has the smallest ve-score
    """
    def set_reference(self):
        j = None
        x = float('inf')
        for i in range(len(self.mgs)):
            ves = self.mgs[i].ve_score()
            if ves[0] + ves[1] <= x: j = i
        
        if j == None: return
        self.reference = self.mgs.pop(j)
        self.reference_index = j

        # obtain the components and sort them in
        # descending order by degree
        self.ref_cs = self.reference.component_seq()
        self.ref_cs = sorted(self.ref_cs,key=lambda x: len(x),reverse=True) 
        assert len(self.mgs) > 0
        
    """
    initializes members of the cache used for
    searching
    """
    def initialize_cache(self):
        # set the reference
        self.set_reference() 

        # add the first element to cache
        self.cache = deque()

        # 
        e1 = [defaultdict(str) for i in range(len(self.mgs))]
        e2 = []
        e4 = deepcopy(self.ref_cs)
        e3 = deque(e4.pop(0))
        self.cache.append([e1,e2,e3,e4])
        self.cache_counter = 1

    """
    return:
    - [0] SEQUENCE<INFO(m) in mgs> s.t. INFO(m) is 
        reference node -> target node
      [1] edges of reference
    - score of match, number of vertices + number of edges 
    """
    def search(self,candidate_search_size_limit):
        best_soln = None
        best_score = 0
        cssl = 0 
        while len(self.cache) > 0:
            ##print("len cache: ", len(self.cache)) 
            ##print("cache counter: ",self.cache_counter)
            c = self.cache.popleft()
            q = self.improve_search_candidate(c,candidate_search_size_limit)

            # case: candidate with component of interest cannot be
            #       improved.
            #       Either move on to the next component or terminate,
            #       if none remaining.
            if type(q) != type(None):                
                # case: no more components, score
                if len(c[3]) == 0:
                    score = self.score_candidate(c) ##self.score_candidate_by_component(c)
                    if score > best_score:
                        best_score = score
                        best_soln = c
                # case: move on to the next component
                else:
                    c[2] = c[3].pop(0)

                    # case: cache limit has already been reached. 
                    if type(candidate_search_size_limit) != type(None):
                        if self.cache_counter >= candidate_search_size_limit:
                            continue

                    self.cache.append(c)
                    self.cache_counter += 1 
        if type(best_soln) != type(None):    
            best_soln = best_soln[:2]
        return best_soln, best_score

    def score_candidate(self,candidate):
        if len(candidate[0][0]) == 0:
            return 0

        return len(candidate[0][0]) + len(candidate[1]) 

    def score_candidate_by_component(self,candidate):
        index = len(self.ref_cs) - len(candidate[3]) - 1

        # get the number of assigned nodes
        nc = len(self.ref_cs[index]) - len(candidate[2])

        # get the number of assigned edges
        cs = deepcopy(self.ref_cs[index])
        ec = 0
        for q in candidate[1]:
            sq = q.split(",")
            if sq[0] in cs or sq[1] in cs:
                ec += 1
        return nc + ec 

    """
    [0] SEQUENCE<INFO(m) in mgs> s.t. INFO(m) is 
        reference node -> target node
    [1] edges of reference
    [2] remaining nodes of component to be assigned
    [3] remaining nodes of reference in component-set form
    """
    def improve_search_candidate(self,candidate,candidate_search_size_limit):
        # case: no more nodes in component
        if len(candidate[2]) == 0:
            return candidate

        if type(candidate_search_size_limit) != type(None):
            if self.cache_counter >= candidate_search_size_limit:
                return candidate

        # crawl on one of the heads in e3 to determine
        # its counterparts on the other MicroGraphs
        h = candidate[2].pop()
        if self.search_type == "full neighbor fit- type 1":
            return self.improvement_type__full_neighbor_fit(candidate,h,False)
        elif self.search_type == "full neighbor fit- type 2":
            return self.improvement_type__full_neighbor_fit(candidate,h,True)
        else:
            return self.improvement_type__matching_neighbor_fit(candidate,h) 

    def improvement_type__full_neighbor_fit(self,candidate,h,neighbor_count_stat:bool):
        neighbors = self.reference.dg[h] 
        assigned_neighbors_r = set()
        q = defaultdict(list)
        for ns in neighbors:
            for x in candidate[0]:
                if ns in x:
                    q[ns].append(x[ns])
                    assigned_neighbors_r |= {ns}

        ### TODO: full-neighbors fit 
        # gather all the possible counterparts for each MicroGraph
        self.pc = []
        for (i,x) in enumerate(candidate[0]):
            # get the remaining nodes
            rem = set(self.mgs[i].dg.keys()) - set(x.values())
            
            # get the subset of nodes that are neighbors with the requirements
            q_ = set([v[i] for v in q.values()])
            ##print("q_: ",q_)
            rem_ = None
            if not neighbor_count_stat:
                rem_ = set([r for r in rem if q_.issubset(self.mgs[i].dg[r])])
            else: 
                rem_ = set([r for r in rem if len(self.mgs[i].dg[r]) >= len(neighbors) and \
                    q_.issubset(self.mgs[i].dg[r])])
            self.pc.append(list(rem_))

        # if any of the MicroGraphs have zero candidates, then terminate
        for pc_ in self.pc:
            if len(pc_) == 0:
                return candidate
    
        # make neighbors for all assigned neighbors of h
        for anr in assigned_neighbors_r:
            candidate[1].extend([h + "," + anr,\
                anr + "," + h])
        
        index_seq = [0 for i in range(len(self.pc))]
        self.recursive_add(h,candidate,index_seq,len(index_seq) - 1,False)
        return None
        
    def improvement_type__matching_neighbor_fit(self,candidate,h):
        # gather all the possible counterparts for each MicroGraph
        self.pc = []
        for (i,x) in enumerate(candidate[0]):
            # get the remaining nodes
            rem = set(self.mgs[i].dg.keys()) - set(x.values())
            self.pc.append(list(rem))

        index_seq = [0 for i in range(len(self.pc))]
        self.recursive_add(h,candidate,index_seq,len(index_seq) - 1,draw_edges=True)
        return None        

    """
    Helper method for `improve_search_candidate`. 
    Adds every possible new candidate stemming from the original argument `candidate`
    to the cache

    h := node of reference
    candidate := a possible solution
    i := first index of `self.pc`
    j := second index of `self.pc`
    """
    # NOTE: careful with stack overflow
    def recursive_add(self,h,candidate,index_seq,delta_index,draw_edges:bool):
        
        if delta_index == -1:
            return

        # case: reset delta_index
        if index_seq[delta_index] >= len(self.pc[delta_index]):
        
            # case: reset value of `delta_index` to 0, and 
            index_seq[delta_index] = 0
            if delta_index == 0:
                return

            index_seq[delta_index - 1] += 1
            # recursive on the next
            return self.recursive_add(h,candidate,index_seq,delta_index - 1,draw_edges)
        
        delta_index = len(self.pc) - 1
        candidate_ = deepcopy(candidate)
        
        for i in range(len(self.pc)):
            candidate_[0][i][h] = self.pc[i][index_seq[i]]
        
        if draw_edges:
            candidate_ = self.draw_candidate_edges(h,candidate_)
        self.cache.appendleft(candidate_)
        self.cache_counter += 1

        index_seq[delta_index] += 1
        return self.recursive_add(h,candidate,index_seq,delta_index,draw_edges)

    """
    helper method for the `matching neighbors fit` approach.  
    """
    def draw_candidate_edges(self,h,candidate):
        # get the neighbors for h
        neighbors = self.reference.dg[h]
        # contains assigned neighbor references for each
        # MicroGraph
        nxs = []

        for i in range(len(candidate[0])):
            # get the neighbors of the counterpart
            q = candidate[0][i][h]
            nx = self.mgs[i].dg[q]

            # determine the references of the neighbors 
            # that have satisified
            knx = set()
            for (k,v) in candidate[0][i].items():
                if v in nx:
                    knx |= {k}
            nxs.append(knx) 

        # get the intersection of the neighbors w/ those
        # already assigned
        qx = nxs.pop(0)
        while len(nxs) > 0:
            qx = qx & nxs.pop(0)

        for qx_ in qx:
            candidate[1].extend([h + "," + qx_,\
                qx_ + "," + h])
        return candidate

    @staticmethod
    def solution_to_MG(s):
        ##print("** S.0")
        ##print(s[0])
        ##print()
        ##print("** S.1")
        ##print(s[1])
        ##print()

        assert len(s) == 2
        assert len(s[0]) > 0

        dg = defaultdict(set)
        # add all the nodes first
        nodes = set(s[0][0].keys())
        for x in s[0]:
            if type(x) != type(None):
                assert nodes == set(x.keys())

        for n in nodes:
            dg[n] = set()

        for x in s[1]:
            q = x.split(",")
            dg[q[0]] = dg[q[0]] | {q[1]}
        
        return MicroGraph(dg)