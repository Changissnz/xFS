from collections import defaultdict,deque
from copy import deepcopy
import numpy as np
import random
import pickle

"""
simple undirected graph designed for small-scale use (<= 5000 nodes)
"""
class MicroGraph:

    def __init__(self,dgraph=defaultdict(set)):
        assert type(dgraph) == defaultdict
        self.dg = dgraph
        return

    def __str__(self):
        return str(self.dg) 

    def subgraph_nodeset_exclusion(self,ns):
        dg2 = deepcopy(self.dg)
        for (k,v) in dg2.items():
            if k in ns:
                del self.dg[k]
            else:
                v_ = set([s for s in v if s not in ns])
                self.dg[k] = v

    def subgraph_by_nodeset_(self,ns):
        mg2 = deepcopy(self)
        q = set(mg2.dg.keys()) - ns
        mg2.subgraph_nodeset_exclusion(q) 
        return mg2

    """
    outputs the MicroGraph of minimal v,e-score based on the variables
    `wanted_nodes` and `wanted_edges`. 
    """
    @staticmethod
    def minimal_MG_by_nodes_and_edges(wanted_nodes,wanted_edges):
        dg = defaultdict(set)

        for x in wanted_nodes:
            dg[x] = set()

        for x in wanted_edges:
            q = x.split(",")
            assert len(q) == 2
            dg[q[0]] |= dg[q[1]]
        return MicroGraph(dg)

    @staticmethod
    def isotransform_MG(mg,isomap):
        dg = defaultdict(set)

        for (k,v) in mg.dg.items():
            v2 = set()
            for v_ in v:
                assert v_ in isomap
                v2 = v2 | {isomap[v_]}
            assert k in isomap 
            dg[isomap[k]] = v2
        return MicroGraph(dg) 

    def ve_score(self):
        # count up the number of nodes
        # count up the number of unique edges
        ns = len(self.dg) 
        es = self.edge_count()
        return (ns,es)

    def __add__(self,mg):
        q = deepcopy(self.dg)
        for (k,v) in mg.dg.items():
            q[k] = q[k] | v
        return MicroGraph(q) 

    def __sub__(self,mg):
        # delete all edges
        mg1 = deepcopy(self)
        for (k,v) in mg.dg.items():
            mg1.dg[k] = mg1.dg[k] - v
        
        # delete all nodes
        for k in mg.dg.keys():
            del mg1.dg[k] 
        return mg1

    # caution: not tested
    def __eq__(self,mg):
        if len(self.dg) != len(mg.dg): 
            return False
        for (k,v) in self.dg.items():
            if mg.dg[k] != v: return False
        return True

    def edge_set(self):
        es = set()
        for (k,v) in self.dg.items():
            for v_ in v:
                es = es | {k + "," + v_} 
        return es 

    def edge_count(self):
        return len(self.edge_set())

    # vertex-edge score of subtraction operation with mg
    def sub_ve_score(self,mg):
        # delete all edges of mg from self
        mg1 = deepcopy(self)
        for (k,v) in mg.dg.items():
            mg1.dg[k] = mg1.dg[k] - v 

        # count the edges
        es = mg1.edge_count() 

        # delete all nodes
        for k in mg.dg.keys():
            del mg1.dg[k]

        # count the nodes
        ns = len(mg1.dg)
        return (ns,es)

    """
    alternative subtraction scheme.

    return:
    - [0] node set of self not of mg 
    - [1] edge set of self not of mg
    """
    def alt_subtract(self,mg):
        # node set
        ns = set(self.dg.keys()) - set(mg.dg.keys())

        # edge set
        es = self.edge_set() - mg.edge_set()
        return ns,es 

    def neighbor_count(self):
        q = defaultdict(int)
        for (k,v) in self.dg.items():
            q[k] = len(v)
        return q

    ################# component calculation 

    """
    calculates the sequence of components belonging to this
    MicroGraph.

    return: 
    - list<set<node identifier>>
    """
    def component_seq(self):
        remaining_nodeset = set(self.dg.keys())
        if len(remaining_nodeset) == 0:
            return []
        search_sol = []
        heads_and_component = [{remaining_nodeset.pop()},set()]

        while len(remaining_nodeset) > 0 or\
            len(heads_and_component[0]) > 0:

            if len(heads_and_component[0]) == 0:
                heads_and_component[0] = {remaining_nodeset.pop()}

            # pop one head and gather its neighbors
            nd = heads_and_component[0].pop()
            heads_and_component[1] |= {nd} 
            q = deepcopy(self.dg[nd])
            heads_and_component[1] = heads_and_component[1] | q
            q2 = set([q_ for q_ in q if q_ in remaining_nodeset])
            remaining_nodeset = remaining_nodeset - q2 - {nd}
            heads_and_component[0] = heads_and_component[0] | q2 

            if len(heads_and_component[0]) == 0:
                search_sol.append(deepcopy(heads_and_component[1]))
                heads_and_component[1].clear()
                if len(remaining_nodeset) == 0: continue 
                heads_and_component[0] = heads_and_component[0] | {remaining_nodeset.pop()}
        return search_sol


    ###################### the subgraph isomorphism problem

    """
    return:
    - if all_iso:
        list<dict, node self -> node other>
      otherwise: 
    """
    def subgraph_isomorphism(self,mg,all_iso=False,size_limit=None,search_candidate_limit=None):#,include_extra=0):
        search_candidates = []
        
        # get the initial candidates for each 
        q = {}
            # rank the nodes of dg from smallest to largest degree
            # element in l := (node, node degree) of mg
        l = [(k,len(v)) for (k,v) in mg.dg.items()]
        l = sorted(l, key=lambda x: x[1])
        lx = [l_[1] for l_ in l]
        dl = [l_ for (i,l_) in enumerate(lx) if lx[:i].count(l_) == 0]    
        mg2 = self 

            # do minumum deletion if no include_extras
        # case: 0 candidates, return
        if len(dl) == 0:
            return [] if all_iso else None 

        ml = dl[0]
        stat = True
        while stat:
            qx = set() 
            for (k,v) in mg2.dg.items():
                if len(v) < ml:
                    qx |= {k}
            stat = len(qx) != 0
            mg2.subgraph_nodeset_exclusion(qx)

            # iterate through mg and determine qualifying nodes of mg2
        qualifying = defaultdict(set) # node of mg -> set of nodes of mg2
        for l_ in l:
            for (k,v) in mg2.dg.items():
                if len(v) >= l_[1]:
                    qualifying[l_[0]] |= {k}
        
        # continue on with search 

        # each element is of the form
        ## node of mg2 --> node of mg
        ## remaining nodes of mg
        search_list = deque()
        l = l[::-1]

        # get the candidates for the first
        ## NOTE: SECTION BELOW FOR: unordered search candidates (non-deterministic)
        """
        for xs in qualifying[l[0][0]]:
            sl1 = [[xs,l[0][0]]]
            sl2 = set(mg.dg.keys()) - {l[0][0]}
            search_list.append([sl1,sl2])
        """

        ## NOTE: SECTION BELOW FOR: ordered search candidates (deterministic)
        xs = sorted(list(qualifying[l[0][0]]))
        for xs_ in xs:
            sl1 = [[xs_,l[0][0]]]
            sl2 = set(mg.dg.keys()) - {l[0][0]}
            search_list.append([sl1,sl2])

        # continue on with search
        stat = len(search_list) != 0 
        results = []
        c = 0 
        while stat:
            #print("* number of results: ", len(results))
            #print("* # candidates: ", c)
            
            # pop the first candidate
            candidate = search_list.popleft()
            cand_exc = set([cdes[0] for cdes in candidate[0]])
            stat2 = len(candidate[1]) != 0

            # case: 1st isomorphism found; return
            if not all_iso and not stat2:
                if len(candidate[1]) == 0:
                    return candidate[0] 
            # case: isomorphism found, add to results seq.
            if not stat2:
                results.append(candidate[0])
                stat = len(search_list) != 0
                continue
            
            # case: number of results exceeds `size_limit`; return 
            if all_iso and type(size_limit) != type(None):
                if len(results) >= size_limit:
                    stat = False
                    stat = len(search_list) != 0 
                    continue

            # case: number of search candidates exceeds `search_candidate_limit`
            #       continue on w/o finishing search w/ candidate. 
            if type(search_candidate_limit) != type(None): 
                if c >= search_candidate_limit:
                    stat = len(search_list) != 0 
                    continue

            ## SECTION BELOW FOR: unordered search candidates (non-deterministic)
            """
            q = candidate[1].pop()
            # get neighbors of candidate in mg
            nmg = mg.dg[q]
            # determine counterparts of mg neighbors to mg2 in candidate map
            counternmg = set([x[0] for x in candidate[0] if x[1] in nmg])

            # get possible counterparts of q to mg2
            qual = deepcopy(qualifying[q])
            qual -= cand_exc
            """

            ## SECTION BELOW FOR: ordered search candidates (deterministic)
            c1ordered = sorted(list(candidate[1]))
            q = c1ordered[0]
            candidate[1].remove(q)
            # get neighbors of candidate in mg
            nmg = mg.dg[q]
            # determine counterparts of mg neighbors to mg2 in candidate map
            counternmg = set([x[0] for x in candidate[0] if x[1] in nmg])
            # get possible counterparts of q to mg2
            qual = deepcopy(qualifying[q])
            qual -= cand_exc
            qual = sorted(list(qual))

            # iterate through the possible counterparts and determine 
            # which ones would work 
            for qn in qual:
                possible_neighbors = mg2.dg[qn]
                inter = counternmg.issubset(possible_neighbors)
                if inter:
                    cand1 = deepcopy(candidate[0])
                    cand2 = deepcopy(candidate[1])
                    cand1.append([qn,q])
                    search_list.appendleft([cand1,cand2])
                    c += 1
            stat = len(search_list) != 0

        if not all_iso:
            return None
        return results