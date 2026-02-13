"""
simple implementation of a classic string metric 
"""
from collections import Counter 

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