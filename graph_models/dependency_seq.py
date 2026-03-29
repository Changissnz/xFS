from morebs2.graph_basics import * 

def prg_to_set_selector(prg): 

    def f(S): 
        assert type(S) == set 
        q = sorted(S) 
        l = int(prg()) % len(q) 
        S_ = set()
        for _ in range(l): 
            i = int(prg()) % len(q) 
            q_ = q.pop(i) 
            S_ |= {q_} 
        return S_ 
    return f 

"""
setseq := list<set>. 
"""
class DependencySequence: 

    def __init__(self,setseq): 
        q = flatten_setseq(setseq)
        c = 0 
        for s in setseq: c += len(s) 
        assert c == len(q) 

        self.setseq = setseq 
        self.unique_elements = q 

    def __len__(self): 
        return len(self.setseq) 

    def len_at(self,index): 
        return len(self.setseq[index]) 

    def move_set(self,set_index,new_index): 
        s = self.setseq.pop(set_index)
        self.setseq.insert(new_index,s) 
        return
    
    def transfer_to_set(self,to_set_index,from_set_index,selector_func):  
        s0 = self.setseq[to_set_index] 
        s1 = self.setseq[from_set_index] 
        select = selector_func(s1) 
        assert select.issubset(s1) 
        s0 = s0 | select 
        s1 = s1 - select
        return

    def add_to_set(self,set_index,num_new,new_func): 
        s0 = self.setseq[set_index] 
        q = [] 
        for _ in range(num_new): 
            q.append(new_func()) 
        q = set(q) 
        assert len(q) == num_new 
        assert q.intersection(self.unique_elements) == set() 
        s0 = s0 | q 
        self.unique_elements |= q 
        return