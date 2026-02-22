from .strangle_form import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence,prg_choose_n

DEFAULT_GRAPH_NODE_SIZE_RANGE = [600,6000] 
DEFAULT_FORCE_PER_NODE_RANGE = [10,100] 
DEFAULT_STRANGLE_GRAPH_EDGE_WEIGHT_RANGE = [10,100] 
DEFAULT_STRANGLE_GRAPH_NODE_WEIGHT_RANGE = [1,25] 
DEFAULT_STRANGLE_ENV_ENTRY_POINTS = [1,8] 

class StrangleEnv: 

    def __init__(self,strangler,strangle_subject,node_weights,info_mode,prg): 
        assert type(strangler) == StrangleForm
        assert type(strangle_subject) == StrangleSubject
        assert strangler.G == strangle_subject.G 
        assert type(node_weights) == dict 
        assert set(strangler.G.keys()) == set(node_weights.keys()) 
        assert info_mode in {0,1,2,3}
        assert type(prg) in {MethodType,FunctionType} 
        
        self.strangler = strangler 
        self.strangle_subject = strangle_subject
        self.node_weights = node_weights 
        self.info_mode = info_mode 
        self.prg = prg 

    def __next__(self): 
        entry_points = self.issue_entry_points()
        self.strangler.move(entry_points,traversal_type_seq=None)

        ##print("# of held_nodes: ", len(self.strangler.held_nodes))

        self.strangle_subject.calculate_communities() 
        ##print("communities: ",len(self.strangle_subject.communities))
        sfi = StrangleFormInfo(self.info_mode) 
        sfi.load_info(self.strangler,self.node_weights,self.strangle_subject.communities)
        ##print("SS: ",self.strangle_subject)
        self.strangle_subject.receive_surface_info(sfi) 
        ##print("SS2: ",self.strangle_subject)

        break_decision = self.strangle_subject.break_decision_()
        nodeset,force = break_decision 
        ##print("FORCE: ",force) 
        node_map_ = self.strangler.node_status(True)
        node_map = {k:v for k,v in node_map_.items() if k in nodeset} 
        ##print("NM: ",node_map) 
        q = default_strangle_breaking_function(node_map,force,node_weight_map=self.node_weights)
        broken = self.strangler.register_reaction(q) 
        print("BROKEN: ",broken) 


    def issue_entry_points(self): 
        q = modulo_in_range(int(self.prg()),DEFAULT_STRANGLE_ENV_ENTRY_POINTS)
        return set(prg_choose_n(sorted(self.node_weights.keys()),q,prg__single_to_int(self.prg))) 

    @staticmethod 
    def generate_instance(strangler_force_assignment_type,info_mode,prg,strangler_energy=10**6,\
        strangle_subject_energy=10**6): 

        connectivity_range = [0.009,0.025]

        vertex_degree = modulo_in_range(int(prg()),DEFAULT_GRAPH_NODE_SIZE_RANGE)
        connectivity = modulo_in_range(prg(),connectivity_range)
        is_realtime_gen = bool(int(prg()) % 2)

        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
        vertex_degree=vertex_degree,edge_connectivity=connectivity,verbose=False)
        gg.full_run() 
        G = graph_to_one_component(gg.d,prg)

        gw = GraphWeightGen(G,prg,is_dsg=False,weight_range=DEFAULT_STRANGLE_GRAPH_EDGE_WEIGHT_RANGE)
        edge_cost_function = gw.weight_ 

        prgs = prg_to_prg__LCG_sequence(prg,4,3.55+78/66) 

        sf = StrangleForm(G,prgs[0],edge_cost_function=edge_cost_function,\
        force_assignment_type=strangler_force_assignment_type,force_per_node_range=DEFAULT_FORCE_PER_NODE_RANGE,\
        energy=strangler_energy)

        ss = StrangleSubject(G,num_comm_range=DEFAULT_STRANGLESUBJECT_COMMUNITY_SIZE_RANGE,\
        break_prg=prgs[1],comm_prg=prgs[2],force_per_node_range=DEFAULT_FORCE_PER_NODE_RANGE,\
        energy=strangle_subject_energy)  

        node_weights = dict() 
        for k in G.keys(): 
            node_weights[k] = modulo_in_range(int(prg()),DEFAULT_STRANGLE_GRAPH_NODE_WEIGHT_RANGE)

        return StrangleEnv(sf,ss,node_weights,info_mode,prgs[3])