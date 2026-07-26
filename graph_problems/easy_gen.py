from .easy_gen_default_vars import * 

def easy_generate_RNBot(prg,qstruct_nfa_type = None, qstruct_answer_type:str=None,qstruct_open_info_mode:str=None): 

    if type(qstruct_nfa_type) == type(None):
        qstruct_nfa_type = modulo_in_range(int(prg()),[1,3]) 
    assert qstruct_nfa_type in {1,2,3}

    if type(qstruct_answer_type) == type(None): 
        i = int(prg()) % len(DEFAULT_QSTRUCT_GENERATION_ANSWER_TYPES) 
        qstruct_answer_type = DEFAULT_QSTRUCT_GENERATION_ANSWER_TYPES[i]
    else: 
        assert qstruct_answer_type in DEFAULT_QSTRUCT_GENERATION_ANSWER_TYPES

    if type(qstruct_open_info_mode) == type(None): 
        qstruct_open_info_mode = [int(prg()) % 2 for _ in range(4)] 

    qstruct_open_info_mode = tuple(qstruct_open_info_mode) 
    assert len(qstruct_open_info_mode) == 4 
    assert set(qstruct_open_info_mode).issubset({0,1}) 

    ## now for the rest of the variables 
    num_nodes = modulo_in_range(int(prg()),DEFAULT_RNB_NUM_NODES_RANGE) 
    uniform_resistance = modulo_in_range(int(prg()),DEFAULT_RNB_NODE_RESISTANCE_RANGE) 
    num_questions = modulo_in_range(int(prg()),DEFAULT_RNB_NUM_QUESTIONS_RANGE) 

    num_questions_to_vary = int(prg()) % num_questions

    answer_objective = int(prg()) % 3
    answer_range = DEFAULT_RNB_ANSWER_RANGE

    start_node_idn = 0 

    R = RNBot.generate_instance(num_nodes,uniform_resistance,num_questions,answer_objective,\
        answer_range,num_questions_to_vary,prg,start_node_idn,qstruct_answer_type,\
        qstruct_open_info_mode,verbose=True)

    R.set_qstruct_nfa_type(qstruct_nfa_type)
    return R 

def easy_generate_HTEBOT(prg,info_mode=None,navigator_remembers_past_encounters:bool=None):

    if type(info_mode) == type(None): 
        info_mode = [int(prg()) % 2 for _ in range(3)]
        info_mode.append(round(prg_decimal(prg,[0.,1.]),5)) 

    info_mode = np.array(info_mode) 

    if type(navigator_remembers_past_encounters) != bool: 
        navigator_remembers_past_encounters = bool(int(prg()) % 2)

    # generate the graph 
    is_dsg = False 
    is_realtime_gen = bool(int(prg()) % 2)
    vertex_degree = modulo_in_range(int(prg()),DEFAULT_HTEB_GRAPH_NODE_SIZE_RANGE) 
    edge_connectivity = round(modulo_in_range(prg(),DEFAULT_HTEB_GRAPH_EDGE_CONN_RANGE),5)
    
    gg = GraphGen(is_dsg,prg,is_realtime_gen,vertex_degree,edge_connectivity,verbose=False) 
    gg.full_run() 
    
    G = gg.d 
    G = graph_to_one_component(G,prg)

    # generate the other variables
    num_entry_points = modulo_in_range(int(prg()),DEFAULT_HTEB_NUM_ENTRY_POINTS_RANGE)
    num_objective_points = modulo_in_range(int(prg()),DEFAULT_HTEB_NUM_OBJECTIVE_POINTS_RANGE)
    threat_ratio = round(modulo_in_range(prg(),DEFAULT_HTEB_THREAT_RATIO_RANGE),5)
    threat_mobility_ratio = round(modulo_in_range(prg(),DEFAULT_HTEB_THREAT_MOBILITY_RATIO_RANGE),5) 
    threat_nodes_include_entry_points = bool(int(prg()) % 2)

    S = HTESurface.generate_instance(G,num_entry_points,num_objective_points,threat_ratio,threat_mobility_ratio,\
        threat_nodes_include_entry_points,prg) 

    H = HTEBot(S,None,navigator_remembers_past_encounters,verbose=True)
    H.set_bot_mode(info_mode)
    return H 

def easy_generate_SNBot(prg,auto_agent_ratio:float=None):

    if type(auto_agent_ratio) == type(None):
        auto_agent_ratio = round(prg_decimal(prg,[0.,1.]),5)
    assert 0. <= auto_agent_ratio <= 1. 

    num_agents = modulo_in_range(int(prg()),DEFAULT_SNB_NUM_AGENTS_RANGE) 
    prg_state_shape = modulo_in_range(int(prg()),DEFAULT_SNB_STATE_SHAPE_RANGE) 
    
    r_conn_range = deepcopy(DEFAULT_SNB_XCONN_RANGE)
    s_conn_range = deepcopy(DEFAULT_SNB_XCONN_RANGE)
    t_conn_range = deepcopy(DEFAULT_SNB_XCONN_RANGE)

    s_port_variance_range = [0.,1.]

    M = MutableCEAgentNetwork.generate_instance__type_prng(num_agents,prg_state_shape,r_conn_range,\
        s_conn_range,t_conn_range,s_port_variance_range,prg) 

    auto_agents = set() 
    if auto_agent_ratio > 0.: 
        q = sorted(M.cea_map.keys())
        num_auto = auto_agent_ratio * len(q)
        auto_agents = prg_choose_n(q,num_auto,prg__single_to_int(prg),is_unique_picker=True)
        auto_agents = set(auto_agents)

    return SNBot.from_MutableCEAgentNetwork(M,auto_agents,True)

def easy_generate_PTBot(prg):

    num_source_nodes = modulo_in_range(int(prg()),DEFAULT_PTB_NUM_ST_RANGE)
    num_target_nodes = modulo_in_range(int(prg()),DEFAULT_PTB_NUM_ST_RANGE)
    num_poisons = modulo_in_range(int(prg()),DEFAULT_PTB_NUM_POISONS_RANGE)

    p0 = round(prg_decimal(prg,DEFAULT_PTB_P2S_RATIO_RANGE),5)
    p1 =  round(prg_decimal(prg,DEFAULT_PTB_P2S_RATIO_RANGE),5)
    poison2source_ratio_range = sorted([p0,p1])
    
    poison_matrix_square_dim = modulo_in_range(int(prg()),DEFAULT_PTB_POISON_MATRIX_SQUARE_DIM_RANGE)
    expressive_mode = bool(int(prg()) % 2) 
    
    seed0 = int(prg()) % 52414
    seed1 = int(prg()) % 52114 
    seed_pair = (seed0,seed1)

    relays_per_source = modulo_in_range(int(prg()),DEFAULT_PTB_RELAYS_PER_SOURCE_RANGE) 

    r0,r1 = prg_decimal(prg,[0.,1.]),prg_decimal(prg,[0.,1.])
    r0,r1 = round(r0,5), round(r1,5)

    if r0 == r1: 
        r1 = (r1 + 0.1) % 1.0 

    relay_accuracy_range = sorted([r0,r1]) 
    return PTBot.generate_instance(num_source_nodes,num_target_nodes,num_poisons,\
        poison2source_ratio_range,poison_matrix_square_dim,expressive_mode,\
        prg,seed_pair,relays_per_source,relay_accuracy_range,verbose=True)

def easy_generate_BKBot(prg,open_info_mode:tuple=None):

    if type(open_info_mode) == type(None):
        open_info_mode = [int(prg()) % 2 for _ in range(2)]
    open_info_mode = tuple(open_info_mode)
    assert len(open_info_mode) == 2 
    assert set(open_info_mode).issubset({0,1})

    num_nodes = modulo_in_range(int(prg()),DEFAULT_BKB_NUM_NODES_RANGE) 
    
    i = int(prg()) % len(DEFAULT_TREE_GEN_GROWTH_TYPES)
    growth_type = DEFAULT_TREE_GEN_GROWTH_TYPES[i]

    num_entry_points = modulo_in_range(int(prg()),DEFAULT_BKB_NUM_ENTRY_POINTS_RANGE)
    num_agents = modulo_in_range(int(prg()),DEFAULT_BKB_NUM_AGENTS_RANGE) 

    visual_radius = modulo_in_range(int(prg()),DEFAULT_BKB_CHASER_COORD_RADIUS_RANGE) 
    c2c_distance = modulo_in_range(int(prg()),DEFAULT_BKB_CHASER_COORD_RADIUS_RANGE)
    c2c_distance = max([visual_radius+1,c2c_distance])

    bull_is_2nd_premover = round(prg_decimal(prg,[0.,1.]),5)

    bull_energy = modulo_in_range(int(prg()),DEFAULT_BKB_AGENT_ENERGY_RANGE)
    chaser_energy = modulo_in_range(int(prg()),DEFAULT_BKB_AGENT_ENERGY_RANGE)

    K = BKBot.generate_instance(num_nodes,growth_type,num_entry_points,\
        num_agents,visual_radius,c2c_distance,prg,open_info_mode,\
        bull_is_2nd_premover,bull_energy,chaser_energy,\
        weight_range=[1,10])
    K.set_verbosity(True)

    return K 

def easy_generate_HFBot(prg,open_info:bool=None,weighted_mode:bool=None):

    if type(open_info) == type(None): 
        open_info = bool(int(prg()) % 2) 

    if type(weighted_mode) == type(None): 
        weighted_mode = bool(int(prg()) % 2) 

    assert type(open_info) == bool == type(weighted_mode)

    num_agents = modulo_in_range(int(prg()),DEFAULT_HFB_NUM_AGENTS_RANGE) 
    score_per_agent = modulo_in_range(prg(),DEFAULT_HFB_INITIAL_AGENT_SCORE_RANGE)

    H = HomoFrameBot.generate_instance(num_agents,prg,score_per_agent,open_info)
    H.set_weighted_mode(weighted_mode) 
    H.verbose = True 
    return H 

def easy_generate_MKBot(prg): 

    num_agents = modulo_in_range(int(prg()),DEFAULT_MKB_NUM_AGENTS_RANGE) 
    mob_agent_uniform_score = round(modulo_in_range(prg(),DEFAULT_MKB_MOB_AGENT_UNIFORM_SCORE_RANGE),5) 

    antimob_mult = round(modulo_in_range(prg(),DEFAULT_MKB_ANTIMOB_SCORE_MULTIPLIER_RANGE),5) 
    antimob_score = round(mob_agent_uniform_score * antimob_mult,5) 

    M = MKBot.generate_instance(num_agents,prg,antimob_score,mob_agent_uniform_score)
    M.verbose = True 
    return M 

def easy_generate_SBot(prg,strangler_force_assignment_type:str=None,info_mode:int=None,enable_consumption:bool=None):

    if type(strangler_force_assignment_type) == type(None): 
        i = int(prg()) % len(DEFAULT_STRANGLER_FORCE_ASSIGNMENT)
        strangler_force_assignment_type = DEFAULT_STRANGLER_FORCE_ASSIGNMENT[i] 
    assert strangler_force_assignment_type in DEFAULT_STRANGLER_FORCE_ASSIGNMENT

    if type(info_mode) == type(None): 
        info_mode = int(prg()) % 4 
    assert info_mode in {0,1,2,3}

    if type(enable_consumption) == type(None): 
        enable_consumption = bool(int(prg()) % 2) 
    assert type(enable_consumption) == bool 

    strangle_subject_energy = round(modulo_in_range(prg(),DEFAULT_SB_SUBJECT_ENERGY_RANGE),5)

    strangler_mult = round(modulo_in_range(prg(),DEFAULT_SB_STRANGLER_ENERGY_MULTIPLIER_RANGE),5)
    strangler_energy = round(strangle_subject_energy * strangler_mult,5) 

    S = StrangleBot.generate_instance(strangler_force_assignment_type,\
        info_mode,prg,strangler_energy,strangle_subject_energy,enable_consumption,
        DEFAULT_SB_GRAPH_NODE_SIZE_RANGE) 
    S.verbose = True 
    return S 

def easy_generate_CBot(prg,correlation_value_0:float=None,correlation_value_1:float=None): 

    if type(correlation_value_0) == type(None):
        correlation_value_0 = prg_decimal(prg,[0.,1.])
    correlation_value_0 = round(correlation_value_0,5)
    assert 0. <= correlation_value_0 <= 1. 

    if type(correlation_value_1) == type(None):
        correlation_value_1 = prg_decimal(prg,[0.,1.])
    correlation_value_1 = round(correlation_value_1,5)
    assert 0. <= correlation_value_1 <= 1. 

    num_agents = modulo_in_range(int(prg()),DEFAULT_CB_NUM_AGENTS_RANGE) 

    q = floor(10 / num_agents)
    path_size = modulo_in_range(int(prg()),[1,q+1]) 
    
    agent_action_value_range = deepcopy(DEFAULT_CB_AGENT_ACTION_VALUE_RANGE)
    cumulative_payoff_multiplier_range = deepcopy(DEFAULT_CB_CUMULATIVE_PAYOFF_MULTIPLIER_RANGE) 

    T = ControverterBot.generate_instance(num_agents,path_size,agent_action_value_range,\
        cumulative_payoff_multiplier_range,prg)
    T.set_correlation_values(correlation_value_0,correlation_value_1)
    T.verbose = True 
    return T 

def easy_generate_TSBot(prg): 
    return TokenSwappingBot.generate_instance(prg,verbose=True) 

def easy_generate_DRBot(prg): 
    D = DualRoleBot.generate_instance(prg) 
    D.verbose = True 
    return D 

def easy_generate_MMBot(prg,prg2=None,allow_buyer_memoryless_navigation:bool=None):

    if type(prg2) == type(None): 
        prg2 = default_easy_generation_LCG(prg) 

    assert type(prg2) in {MethodType,FunctionType}

    if type(allow_buyer_memoryless_navigation) == type(None): 
        allow_buyer_memoryless_navigation = bool(int(prg()) % 2)
    assert type(allow_buyer_memoryless_navigation) == bool 

    i = int(prg()) % len(DEFAULT_JAMMING_GRAPH_TYPES)
    jamming_graph_type = DEFAULT_JAMMING_GRAPH_TYPES[i] 

    unit_price = round(modulo_in_range(prg(),DEFAULT_MMB_UNIT_PRICE_RANGE),5)

    M = MiddleManBot.generate_instance(jamming_graph_type,unit_price,\
        allow_buyer_memoryless_navigation,prg,prg2)
    M.verbose = True 
    return M 

def easy_generate_VTBot(prg): 
    num_chasers = modulo_in_range(int(prg()),DEFAULT_VTB_NUM_CHASERS_RANGE) 
    bound_dim = modulo_in_range(int(prg()),DEFAULT_VTB_BOUNDS_DIM_RANGE)
    vector_bound_range = np.array([DEFAULT_VTB_VECTOR_BOUND_SINGLE_RANGE for _ in range(bound_dim)]) 
    tracker_point_dispersal_max_float = round(modulo_in_range(prg(),DEFAULT_VTB_TRACKER_POINT_DISPERSAL_RANGE),5) 

    V = VTBot.generate_instance(num_chasers,vector_bound_range,\
        tracker_point_dispersal_max_float,prg)
    V.verbose = True 
    return V 

def easy_generate_IBot(prg,introspector_description:tuple=None,is_bfs:bool=None): 

    if type(introspector_description) == type(None): 
        i = int(prg()) % len(DEFAULT_INTROSPECTOR_TYPES) 
        t = DEFAULT_INTROSPECTOR_TYPES[i]

        b0 = bool(int(prg()) % 2)
        b1 = bool(int(prg()) % 2)

        if t == "reactive":
            introspector_description = (t,b0,b1)
        else: 
            f0 = round(prg_decimal(prg,[0.,1.]),5)
            f1 = round(prg_decimal(prg,[0.,1.]),5) 
            introspector_description = (t,f0,f1,b0,b1) 

    if type(is_bfs) == type(None): 
        is_bfs = bool(int(prg()) % 2)
    assert type(is_bfs) == bool 

    num_minpaths = modulo_in_range(int(prg()),DEFAULT_IB_NUM_MINPATHS_RANGE) 
    ascending_priority = bool(int(prg()) % 2) 

    sequence_length = modulo_in_range(int(prg()),DEFAULT_IB_SEQUENCE_LENGTH) 
    sequence = [modulo_in_range(int(prg()),DEFAULT_IB_TRAVERSAL_RANGE) for _ \
        in range(sequence_length)] 

    I = IntrospectionBot.generate_instance(\
        introspector_description,is_bfs,\
        ascending_priority,sequence,num_minpaths,prg)
    I.verbose = True 
    return I 

def easy_generate_PIBot(prg_O,prg_D=None,prg_E=None,open_info_mode:str=None): 

    if type(prg_D) == type(None): 
        prg_D = default_easy_generation_LCG(prg_O) 

    if type(prg_E) == type(None): 
        prg_E = default_easy_generation_LCG(prg_O) 

    L = sorted(SIMPLE_HMM_ENVIRONMENT_INFO_MODES - {"perfect-full"}) 

    if type(open_info_mode) == type(None): 
        i = int(prg_O()) % len(L) 
        open_info_mode = L[i] 
    assert open_info_mode in L 

    P = sorted(HMM_OFFENDER_LCG_PATTERN_TYPES)
    i = int(prg_O()) % len(P)
    offendor_lcg_delta_pattern_type = P[i]

    qmin = - modulo_in_range(int(prg_O()),[1,DEFAULT_PIB_OFFENDER_LCGV_MAX_VALUE+1]) 
    qmax = modulo_in_range(int(prg_O()),[1,DEFAULT_PIB_OFFENDER_LCGV_MAX_VALUE+1]) 
    offendor_lcgv_range = (qmin,qmax)

    P = PIBot.default_generate_instance(prg_O,prg_D,prg_E,offendor_lcg_delta_pattern_type,\
        offendor_lcgv_range,open_info_mode)
    P.verbose = True 

    return P 

def easy_generate_EFBot(prg,activation_type:str=None,info_mode:int=None): 

    L = sorted(PATH_TYPE_DI_NODE_ACTIVATION_TYPES) 

    if type(activation_type) == type(None): 
        i = int(prg()) % len(L) 
        activation_type = L[i] 
    assert activation_type in L 

    if type(info_mode) == type(None): 
        info_mode = int(prg()) % 2 
    assert info_mode in {0,1} 

    node_value_range = deepcopy(DEFAULT_EFB_NODE_VALUE_RANGE) 
    extra_edge_ratio = round(prg_decimal(prg,[0.,1.]),5) 
    ratio_indirect_activation = round(prg_decimal(prg,[0.,1.]),5) 
    prior_dependency_ratio = round(prg_decimal(prg,[0.,1.]),5) 

    efbot = EndsFixatedBot.generate_instance(node_value_range,extra_edge_ratio,\
        ratio_indirect_activation,prior_dependency_ratio,activation_type,info_mode,prg)
    efbot.verbose = True 
    return efbot 

def easy_generate_TFTMBot(prg,mo_type:str=None,variable_comp:bool=None): 

    if type(variable_comp) == type(None):
        variable_comp = bool(int(prg()) % 2) 
    assert type(variable_comp) == bool 

    agent_idns = [0,1,2] 
    num_categories = modulo_in_range(int(prg()),DEFAULT_TFTMB_NUM_CATEGORIES_RANGE)  
    label_size_range = deepcopy(DEFAULT_TFTMB_NUM_LABELS_RANGE) 

    L = sorted(DEFAULT_AGENT_TYPE_2F3M_MODUS_OPERANDI_TYPES)
    if type(mo_type) == type(None): 
        i = int(prg()) % len(L) 
        mo_type = L[i]
    assert mo_type in L 

    attribute_bound_vec = None 
    if mo_type == "compatible characterization": 
        attribute_bound_vec = np.array([deepcopy(DEFAULT_TFTMB_CC_ATTRIBUTE_RANGE) \
            for _ in range(num_categories)]) 

    T = TwoFacesThreeMotivesBot.generate_instance(\
        agent_idns,mo_type,num_categories,label_size_range,attribute_bound_vec,\
        variable_comp,prg)
    T.set_verbosity(True) 
    return T 

def easy_generate_PDIBot(prg,chain_prg=None,solver_prg=None,info_mode:int=None): 

    if type(chain_prg) == type(None): 
        chain_prg = default_easy_generation_LCG(prg) 
    
    if type(solver_prg) == type(None): 
        solver_prg = default_easy_generation_LCG(prg) 

    if type(info_mode) == type(None): 
        info_mode = int(prg()) % 2
    assert info_mode in {0,1} 

    num_moves = modulo_in_range(int(prg()),DEFAULT_PDIB_NUM_MOVES_RANGE)
    prior_connectivity_pr = round(prg_decimal(prg,[0.,1.]),5) 
    
    d0 = round(prg_decimal(prg,DEFAULT_PDIB_INADVERTENCY_RATIO_RANGE),5)
    d1 = round(prg_decimal(prg,DEFAULT_PDIB_INADVERTENCY_RATIO_RANGE),5)
    if d0 == d1: 
        d1 = (d1 + 0.1) % 1.0 
    inadvertency_ratio_range = tuple(sorted([d0,d1]))


    node_value_range = deepcopy(DEFAULT_PDIB_NODE_VALUE_RANGE)
    inadvertency_size_range = deepcopy(DEFAULT_PDIB_INADVERTENCY_SIZE_RANGE) 

    P = PDIBot(num_moves,prior_connectivity_pr,inadvertency_ratio_range,node_value_range,\
        inadvertency_size_range,info_mode,chain_prg,solver_prg)
    return P 