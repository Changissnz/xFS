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