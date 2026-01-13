from quant.ce_net import * 

def CEAgentNetwork__sample_1(): 
    num_agents = 13 
    prg_state_shape = 6 
    r_conn_range = [0.3,0.4] 
    s_conn_range = [0.2,0.4] 
    t_conn_range = [0.2,0.4] 
    s_port_variance_range = [0.,1.]
    prg = prg__LCG(45.66,8.94,-999.76,1032.66)  

    return CEAgentNetwork.generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,\
        s_conn_range,t_conn_range,s_port_variance_range,prg)
