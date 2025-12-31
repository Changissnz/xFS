from .micrograph import * 

"""
x--x
|  |
x--x
"""
def sample_MicroGraph_1():
    return MicroGraph(dgraph=defaultdict(set,{"0":{"1","2"},"1":{"0","3"},"2":{"0","3"},"3":{"1","2"}}))
    
"""
1--3--4
|  |  |
0--2--5
"""
def sample_MicroGraph_2():

    return MicroGraph(dgraph=defaultdict(set,{"0":{"1","2"},\
                                            "1":{"0","3"},\
                                            "2":{"0","3","5"},\
                                            "3":{"1","2","4"},\
                                            "4":{"3","5"},\
                                            "5":{"2","4"}}))

"""

  2- -3
  \\ //
    0
   //\\
  4- -1
"""
def sample_MicroGraph_3():
    return MicroGraph(dgraph=defaultdict(set,{"0":{"1","2","3","4"},\
                                            "1":{"0","4"},\
                                            "2":{"0","3"},\
                                            "3":{"0","2"},\
                                            "4":{"0","1"}}))

"""
  5   4 
  \\ //
    0--3
    |  |
    1--2 
"""
def sample_MicroGraph_4():

    return MicroGraph(dgraph=defaultdict(set,{"0":{"1","3","4","5"},\
                                            "1":{"0","2"},\
                                            "2":{"1","3"},\
                                            "3":{"0","2"},\
                                            "4":{"0"},
                                            "5":{"0"}}))

"""
0--1--2--3
"""
def sample_MicroGraph_5():

    return MicroGraph(dgraph=defaultdict(set,{"0":{"1"},\
                                            "1":{"0","2"},\
                                            "2":{"1","3"},\
                                            "3":{"2"}}))

"""
0--1
"""
def sample_MicroGraph_6():
    return MicroGraph(dgraph=defaultdict(set,{"0":{"1"},\
                                            "1":{"0"}}))

"""
0
"""
def sample_MicroGraph_7():
    return MicroGraph(dgraph=defaultdict(set,{"0":set()}))
    
"""
    0
  // \\
  1   2 
"""
def sample_MicroGraph_8():
    return MicroGraph(dgraph=defaultdict(set,{"0":{"1","2"},"1":{"0"},"2":{"0"}}))

#------------------------------------------------------------------------------------

def greatest_common_subgraph_case_1():
    mg4 = MicroGraph(defaultdict(set,\
            {"10":{"11","21"},\
            "11":{"10","21"},\
            "21":{"10","11"}}))

    mg3 = MicroGraph(defaultdict(set,\
            {"22":{"10","21","33","41"},\
            "10":{"21","22"},\
            "21":{"10","22"},\
            "33":{"22"},\
            "41":{"22"}}))

    mg2 = MicroGraph(defaultdict(set,\
            {"10":{"12"},\
            "12":{"10","22"},\
            "22":{"12","13","14"},\
            "13":{"22"},\
            "14":{"22"}}))

    mg1 = MicroGraph(defaultdict(set,\
            {"0":{"1","2"},\
            "1":{"0","2"},\
            "2":{"0","1"}}))
    
    return [mg1,mg2,mg3,mg4]

def greatest_common_subgraph_case_2():

    mg1 = MicroGraph(defaultdict(set,\
            {"1":{"2","3"},\
            "2":{"1","3"},\
            "3":{"1","2","4"},\
            "4":{"3"},\
            "6":set()})) 

    mg2 = MicroGraph(defaultdict(set,\
            {"1":{"2","3"},\
            "2":{"1"},\
            "3":{"1","4","5"},\
            "4":{"3","5"},\
            "5":{"3","4"}}))

    mg3 = MicroGraph(defaultdict(set,\
            {"1":{"2","3"},\
            "2":{"1","3","4"},\
            "3":{"1","2","4"},\
            "4":{"2","3","6"},\
            "5":{"3"},\
            "6":{"4"}}))

    mg4 = MicroGraph(defaultdict(set,\
            {"1":{"2","4"},\
            "2":{"1","3"},\
            "3":{"2","4"},\
            "4":{"1","3"}})) 

    return [mg1,mg2,mg3,mg4] 

def greatest_common_subgraph_case_3():

    mg1 = MicroGraph(defaultdict(set,\
            {"1":{"2","3"},\
            "2":{"1","4"},\
            "3":{"1","4"},\
            "4":{"2","3","5"},\
            "5":{"3","4"}}))

    mg2 = MicroGraph(defaultdict(set,\
            {"1":{"2"},\
            "2":{"1","3","5","6"},\
            "3":{"2","4"},\
            "4":{"3"},\
            "5":{"2"},\
            "6":{"2"}}))

    mg3 = MicroGraph(defaultdict(set,\
            {"1":{"2"},\
            "2":{"1","3","4"},\
            "3":{"2"},\
            "4":{"2","5","6"},\
            "5":{"4","6"},\
            "6":{"4","5"}}))

    mg4 = MicroGraph(defaultdict(set,\
            {"1":set(),\
            "2":{"3"},\
            "3":{"2"},\
            "4":{"5","6"},\
            "5":{"4","6"},\
            "6":{"4","5"}}))

    return [mg1,mg2,mg3,mg4]

#---------------------------------------------------------------------------------------------------------------------------

"""

    0---1
    |\ 
    | \ 
    2  \ 
        3 

"""
def test_dfs_graph_1():
    d = defaultdict(set) 
    d[0] = {1,2,3}
    d[1] = {0}
    d[2] = {0}
    d[3] = {0}
    return d

"""

                _______
     ____  ____/_______\ 
    /    \/   /   \     \ 
    0--1--2--3--4--5--6--7--8
"""
def test_dfs_graph_2():
    d = defaultdict(set) 
    d[0] = {1,2}
    d[1] = {0,2}
    d[2] = {0,1,3,5,7}
    d[3] = {2,4,7}
    d[4] = {3,5}
    d[5] = {2,4,6}
    d[6] = {5,7}
    d[7] = {2,3,6,8}
    d[8] = {7}
    return d

"""

    0---1
    | \/| 
    | /\|
    2---3

"""
def test_dfs_graph_3():
    d = defaultdict(set)
    d[0] = {1,2,3}
    d[1] = {0,2,3}
    d[2] = {0,1,3}
    d[3] = {0,1,2}
    return d

"""

    0--1--2--3--4
"""
def test_dfs_graph_4():
    d = defaultdict(set)
    d[0] = {1}
    d[1] = {0,2}
    d[2] = {1,3}
    d[3] = {2,4}
    d[4] = {3}
    return d

#----------------------------------- used for testing <CNFGraphMask> 

"""
4  6  8  10
|  |  |  |
0--1--2--3
|  |  |  |
5  7  9  11 
"""
def base_graph_sample_E(): 

    D = defaultdict(set)

    D[0] = {1,4,5} 
    D[1] = {0,2,6,7} 
    D[2] = {1,3,8,9}
    D[3] = {2,10,11} 
    D[4] = {0} 
    D[5] = {0} 
    D[6] = {1} 
    D[7] = {1} 
    D[8] = {2} 
    D[9] = {2} 
    D[10] = {3} 
    D[11] = {3} 
    return D

"""
4  6 _8 _10
|  |/ |/ |
0--1--2--3
|\ |\ |  |
5  7  9  11
"""
def base_graph_sample_F(): 
    D = base_graph_sample_E() 

    D[10] |= {2} 
    D[2] |= {10} 

    D[8] |= {1} 
    D[1] |= {8} 
    D[9] |= {1} 
    D[1] |= {9} 

    D[7] |= {0} 
    D[0] |= {7} 
    return D 

#---------------------------------- used for testing calculations 
#                                   related to shortest paths. 

def base_graph_sample_G(): 

    return defaultdict(set,{\
        0:{1,2},\
        1:{0,3},\
        2:{0,3},\
        3:{1,2,4},\
        4:{3,5,6},\
        5:{4,7},\
        6:{4,7},\
        7:{5,6,8},\
        8:{7,9,10},\
        9:{8,11},\
        10:{8,11},\
        11:{9,10}})