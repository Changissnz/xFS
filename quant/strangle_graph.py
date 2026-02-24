from .strangle_form import * 
from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg_to_prg__LCG_sequence,prg_choose_n

DEFAULT_GRAPH_NODE_SIZE_RANGE = [600,6000] 
DEFAULT_FORCE_PER_NODE_RANGE = [10,100] 
DEFAULT_STRANGLE_GRAPH_EDGE_WEIGHT_RANGE = [10,100] 
DEFAULT_STRANGLE_GRAPH_NODE_WEIGHT_RANGE = [1,25] 
DEFAULT_STRANGLE_ENV_ENTRY_POINTS = [1,8] 

class StrangleEnv: 

    def __init__(self,strangler,strangle_subject,node_weights,info_mode,prg,\
        enable_consumption:bool=False,verbose=False): 
        
        assert type(strangler) == StrangleForm
        assert type(strangle_subject) == StrangleSubject
        assert strangler.G == strangle_subject.G 
        assert type(node_weights) == dict 
        assert set(strangler.G.keys()) == set(node_weights.keys()) 
        assert info_mode in {0,1,2,3}
        assert type(prg) in {MethodType,FunctionType} 
        
        self.strangler = strangler 
        self.G_ = deepcopy(self.strangler.G) 
        self.strangler.enable_consumption = enable_consumption  
        self.strangle_subject = strangle_subject
        self.node_weights = node_weights 
        self.info_mode = info_mode 
        self.prg = prg 
        self.verbose = verbose 

        self.timestamp = 0 
        self.fin_stat = False 
        self.win_stat = None 

    def set_prng_for_subject(self,comm_prg,break_prg): 
        if type(comm_prg) in {MethodType,FunctionType}:
            self.strangle_subject.comm_prg = comm_prg 

        if type(break_prg) in {MethodType,FunctionType}:
            self.strangle_subject.break_prg = break_prg 
 
    def __next__(self): 
        # case: done 
        if self.fin_stat: 
            return 

        # case: register done due to no more energy 
        if self.strangler.energy <= 0. or self.strangle_subject.energy <= 0.:
            self.fin_stat = True 

            if self.strangler.energy > 0: 
                self.win_stat = "strangler" 
            elif self.strangle_subject.energy > 0: 
                self.win_stat = "subject"
            else: 
                self.win_stat = "tie" 
            return  

        # case: register strangled 
        if self.strangler.strangled_stat : 
            self.fin_stat = True 
            self.win_stat = "strangler" 
            return 

        # case: strangler can consume nodes it strangled 
        nodeset,G = self.strangler.consume()
        if type(nodeset) != type(None):
            self.strangle_subject.G = deepcopy(G) 

        # strangler moves first 
        entry_points = self.issue_entry_points()
        self.strangler.move(entry_points,traversal_type_seq=None)

        self.strangler.check_strangled_stat()
        self.strangler.score(self.node_weights,0.5) 
        stat = self.strangler.strangle_status() 
        if self.verbose: 
            print("\t\t timestamp={}".format(self.timestamp))
            print("-- strangler: {}\n\t{} / {} nodes strangled".format(\
                self.strangler.energy,stat[0],len(self.strangler.G)))
            print("\t{} broken strangles\n\t{} strangle entities\t".format(\
                stat[1],stat[2]))
            print("\t{} consumed nodes".format(len(self.strangler.consumed)))

        # case: strangler holds all environment nodes, strangler wins. 
        if self.strangler.strangled_stat: 
            self.fin_stat = True 
            self.win_stat = "strangler"
            return 

        # strangle subject moves second
        self.strangle_subject.calculate_communities() 
        sfi = StrangleFormInfo(self.info_mode) 
        sfi.load_info(self.strangler,self.node_weights,self.strangle_subject.communities)
        self.strangle_subject.receive_surface_info(sfi) 

        break_decision = self.strangle_subject.break_decision_()
        nodeset,force = break_decision 
        ##print("FORCE: ",force) 
        node_map_ = self.strangler.node_status(True)
        node_map = {k:v for k,v in node_map_.items() if k in nodeset} 
        q = default_strangle_breaking_function(node_map,force,node_weight_map=self.node_weights)
        broken = self.strangler.register_reaction(q) 

        self.timestamp += 1
        if self.verbose: 
            print("-- subject, {} energy.\n used {} F to break {} strangles".format(\
                self.strangle_subject.energy,force,len(broken))) 
            ##print("TESTING: ",len(self.strangle_subject.G)) 
            print("\t\tbroken")
            print(broken) 
            print("-----------------------------------------------------") 

    def issue_entry_points(self): 
        q = modulo_in_range(int(self.prg()),DEFAULT_STRANGLE_ENV_ENTRY_POINTS)
        return set(prg_choose_n(sorted(self.strangler.G.keys()),q,prg__single_to_int(self.prg))) 

    @staticmethod 
    def generate_instance(strangler_force_assignment_type,info_mode,prg,strangler_energy=10**6,\
        strangle_subject_energy=10**6,enable_consumption=False): 

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

        return StrangleEnv(sf,ss,node_weights,info_mode,prgs[3],enable_consumption)