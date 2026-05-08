"""
simple implementation of a classic string metric 
"""
from collections import Counter 
from morebs2.seq_repr import contiguous_cyclical_difference

def levenschtein_distance(s1,s2): 
    if len(s1) == 0: 
        return len(s2)
    
    if len(s2) == 0: 
        return len(s1) 

    if s1[0] == s2[0]: 
        return levenschtein_distance(s1[1:],s2[1:]) 
    
    return 1+min([levenschtein_distance(s1[1:],s2),\
        levenschtein_distance(s1,s2[1:]),\
        levenschtein_distance(s1[1:],s2[1:])])

"""
difference between set elements of s1 & s2 
PLUS 
difference between string element frequencies of s1 & s2 
"""
def simple_string_cmp_metric(s1,s2): 
    q1 = set(s1) 
    q2 = set(s2) 

    l0 = len(q1 - q2)
    l1 = len(q2 - q1) 

    d0 = Counter(s1) 
    d1 = Counter(s2) 
    dx0 = sum((d0 - d1).values()) 
    dx1 = sum((d1 - d0).values()) 

    return l0 + l1 + dx0 + dx1 

"""
Two-sided version checking, with the respect to the lengths of the two vector parameters, 
of the original from project<morebs2>.
"""
def contiguous_cyclical_difference_(v0,v1,diff_type="bool"):

    if len(v0) == 0: 
        return len(v1) if diff_type == "bool" else sum(v1) 
    
    if len(v1) == 0: 
        return len(v0) if diff_type == "bool" else sum(v0) 

    if len(v0) < len(v1): 
        v0,v1 = v1,v0 
    
    return contiguous_cyclical_difference(v0,v1,diff_type) 

