from morebs2.numerical_generator import * 
from morebs2.graph_basics import * 

CYCLE_CATEGORIES = {"closed","sub-cycle"}

def travel_io_map_till_repeat(m,k):
    q = [k]
    stat = True 
    while stat: 
        v = m[k]
        if v in q: break 
        q.append(v) 
        k = v 
    return q 

class CycleDescriptor:

    def __init__(self):
        self.d = defaultdict(None)

    def __str__(self):
        s = "closed: " + str(self.d["closed"]) + "\n" 
        s += "sub-cycle heads: " + \
            str(self.d["sub-cycle"]) + "\n"
        return s 

    def update(self,k,v): 

        assert k in CYCLE_CATEGORIES
        if k == "closed":
            assert type(v) == bool 
        else:
            assert type(v) in {type(None),set}

        self.d[k] = v 
        return

    def is_closed(self):
        return self.d["closed"] 

    def is_continuous(self):
        return type(self.d["sub-cycle"]) == type(None)

'''
converging linear congruential generator 

0 := choose subcycle of length equal to convergence cycle length. if none found, use type 1.
1 := ranged modulo adjustment to accomodate for convergence cycle length. 
'''
class CLCG:

    def __init__(self,start,m,a,n0,n1,convergence_index,convergence_cycle_length,convergence_type,prg): 
        assert n0 < n1
        assert not (m == 0 and a == 0)
        assert convergence_index < n1 - n0 
        assert convergence_cycle_length < convergence_index + 1 
        assert convergence_type in {0,1}

        self.s = start
        self.s_ = start  
        self.m = m 
        self.a = a 
        self.r = [n0,n1]

        self.cindex = convergence_index
        self.ccycle_length = convergence_cycle_length
        self.ctype = convergence_type
        self.prg = prg 

        self.c = 0 
        self.converged = False 

        self.current_cycle = set()  

        self.map_io = dict()
        self.gd = None 
        self.cycle_descriptors = [] 

        self.gd_preproc() 
        return

    def __next__(self):

        if self.c >= self.cindex:
            if not self.converged:
                self.converged = True 
                self.convergence_fix() 
                return self.s_ 
        
        if self.converged: 
            self.c += 1 
            return self.next_() 
        
        ci = self.component_of(self.s_)

        self.current_cycle |= {self.s_} 
        
        # case: current cycle equals full component, switch to another component 
        if self.gd.components[ci] == self.current_cycle:
            self.current_cycle.clear() 
            x = self.choose_alt_component({ci})
            if x != -1: 
                self.s_ = self.choose_element_in_component(x)
                return self.s_ 
            # subcase: no alternative component exists

        s_ = self.next_() 
        self.c += 1 
        return s_

    def next_(self): 
        s_ = self.s_ * self.m + self.a
        s_ = modulo_in_range(s_,self.r) 
        s_,self.s_ = self.s_,s_ 
        return s_ 

    def gd_preproc(self):
        self.io_map()
        self.io_map_partition()
        self.io_map_summary()

    def io_map(self):
        self.map_io.clear()
        for x in range(self.r[0],self.r[1]): 
            y = modulo_in_range(x * self.m + \
                self.a,self.r) 
            self.map_io[x] = y 

    def io_map_partition(self): 
        qx = defaultdict(set)
        for k,v in self.map_io.items():
            qx[k] = set([v]) 

        self.gd = GraphComponentDecomposition(qx) 
        self.gd.decompose()

    def io_map_summary(self):
        for i in range(len(self.gd.components)):
            cd = self.component_index_summary(i)
            self.cycle_descriptors.append(cd) 

    def component_index_summary(self,i):
        q = self.gd.components[i] 
        q = flatten_setseq(q) 

        is_closed = True
        sub_cycle = set()
        for q_ in q:
            p = travel_io_map_till_repeat(self.map_io,q_)
            px = set(p)

            if px != q: 
                sub_cycle |= {q_} 

            if not is_closed: continue 

            if not px.issubset(q): 
                is_closed = False

        if len(sub_cycle) == 0: 
            sub_cycle = None

        cd = CycleDescriptor()
        cd.update("closed",is_closed) 
        cd.update("sub-cycle",sub_cycle)
        return cd

    def convergence_fix(self):
        if self.ctype == 0: 
            i = self.choose_converging_component() 
            if i != -1: 
                self.s_ = self.choose_element_in_component(i) 
                return 

        self.s_ = self.convergence_fix_type_1() 
        return

    def convergence_fix_type_1(self): 
        if self.m < 0: 
            self.m = -self.m 
        if self.a < 0: 
            self.a = -self.a  

        if self.s_ < 0: 
            self.s_ = -self.s_ 

        s = None 
        while True: 
            s = self.attempt_cfix_type_1() 
            if type(s) == type(None): 
                self.m += 1 
                self.a += 1 
            else: 
                break 

        self.r[0] = 0 
        self.r[1] = s[-1] - self.s_ 
        return s[-2]  

    def attempt_cfix_type_1(self):
        s = [self.s_] 
        for i in range(self.ccycle_length): 
            x = s[-1] * self.m + self.a 
            s.append(x) 

        diff = s[-1] - self.s_ 
        if diff <= s[-2]: 
            return None 
        return s 

    def component_of(self,s): 

        for (i,x) in enumerate(self.gd.components):
            if s in x: 
                return i 
        return -1 
    
    def choose_alt_component(self,exclude_components:set): 
        cx = [i for i in range(len(self.gd.components))]

        while len(cx) > 0: 
            q = int(self.prg()) % len(cx) 
            cx_ = cx.pop(q) 
            if cx_ not in exclude_components:
                return cx_ 
        return -1 

    def choose_converging_component(self): 
        for i in range(len(self.gd.components)): 
            l = len(self.gd.components[i]) 
            if l == self.ccycle_length and "sub-cycle" \
                not in self.cycle_descriptors[i]: 
                return i 
        return -1 

    def choose_element_in_component(self,i):
        cx = sorted(self.gd.components[i])
        return int(self.prg()) % len(cx) 