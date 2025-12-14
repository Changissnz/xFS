from morebs2.numerical_generator import prg__LCG

def RStructGraph_generation_parameters(): 

    num_nodes = 10 
    resistance = 10 ** 5 
    num_questions = 6
    answer_objective = 0 
    answer_range = [-10,10] 
    num_questions_to_vary = 3 
    prg = prg__LCG(14,53,23,1212) 
    start_node_idn = 0 

    return num_nodes,resistance,num_questions,\
        answer_objective,answer_range,num_questions_to_vary,\
        prg,start_node_idn