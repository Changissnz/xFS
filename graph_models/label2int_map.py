from .micrograph import SimpleCounter
from morebs2.matrix_methods import stringize_common_var,\
    destringize_common_var

DEFAULT_L2INT_STRINGIZE_FUNC = stringize_common_var

def DEFAULT_L2INT_DESTRINGIZE_FUNC(unit_type,output_set:bool=True): 

    def f(s): 
        return destringize_common_var(s,\
            unit_type,output_set)

    return f 

"""
every label that gets added to memory is assigned a 
unique integer. Integers assigned are in ordinal 
order. 
"""
class Label2IntMap: 

    def __init__(self,starting_label_set,\
        stringize_func,str_inversion_func,\
        enable_bimap:bool=False):  

        assert type(starting_label_set) in {set,list} 
        assert len(starting_label_set) == len(set(starting_label_set)) 
        assert type(enable_bimap) == bool 

        self.label_seq = starting_label_set 
        self.stringize_func = stringize_func
        self.str_inversion_func = str_inversion_func
        self.enable_bimap = enable_bimap 

        self.c = SimpleCounter(0)
        self.imap = dict() 
        self.imap_rev = dict() 

        self.preproc() 
        return 

    def preproc(self): 
        for x in self.label_seq: 
            self.add_element(x) 
        return

    def add_element(self,element): 
        s = self.stringize_func(element) 
        if s in self.imap: return

        i = next(self.c) 
        self.imap[s] = i

        if self.enable_bimap: self.imap_rev[i] = s 
        return

    def element_to_int_label(self,element): 
        s = self.stringize_func(element) 
        if s not in self.imap: return -1  
        return self.imap[s] 

    def int_label_to_element(self,i): 
        assert type(i) == int and i >= 0 

        if self.enable_bimap: 
            return self.str_inversion_func(self.imap_rev[i]) 

        for k,v in self.imap.items(): 
            if v == i: return self.str_inversion_func(k) 
        return