"""
simple implementation of a classic string metric 
"""

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