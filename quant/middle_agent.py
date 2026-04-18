from graph_models.base_node import * 

def one_plus_x_PRNG_value(src,prg,x): 
    r = safe_modulo_in_range(prg(),1+x) 
    return round(src * r,5)

DEFAULT_MIDDLE_AGENT_TAX_RANGE = [0.02,0.15]
DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE = [-0.1,-0.02] 

DEFAULT_REPRODUCED_MIDDLE_AGENT_PRNG_LCG_MULTIPLIER_RANGE = [1.1,5+7/9] 

class MiddleAgentSeller: 

    def __init__(self,idn,source,source_price,prg,unit_shelf_life,\
        tax_range=DEFAULT_MIDDLE_AGENT_TAX_RANGE,deduction_range=DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE):

        assert type(source) in {MiddleAgentSeller,type(None)} 
        assert source_price > 0 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(unit_shelf_life) == int and unit_shelf_life > 0 
        assert is_valid_range(tax_range,False,True)
        assert is_valid_range(deduction_range,False,True)
        assert tax_range[0] > 0 
        assert deduction_range[1] < 0 

        self.idn = idn 
        self.source = source 
        self.prg = prg 
        self.unit_shelf_life = unit_shelf_life
        self.tax_range = tax_range 
        self.deduction_range = deduction_range

        if type(self.source) == type(None): 
            self.price = source_price
        else: 
            self.price = one_plus_x_PRNG_value(source_price,self.prg,self.tax_range)
            
        self.initial_price = self.price 

        self.prev_is_sold = False 
        self.sitting_prod_ctr = 0 

        self.units_sold = 0 
        self.units_dumped = 0

    def mark_sold(self): 
        self.prev_is_sold = True 
        return 

    def update(self): 
        q = self.prev_is_sold 
        self.prev_is_sold = False 

        # case: sold. reset sitting product counter to 0. update all 
        #       distributors in chain 
        if q: 
            self.supdate_sold_to_all_in_chain()
            return 

        # case: not sold. update sitting product counter. price reduction. if 
        #       counter surpasses `unit_shelf_life`, dump product and reset price 
        #       to initial price.
        self.sitting_prod_ctr += 1
        self.price = one_plus_x_PRNG_value(self.price,self.prg,self.deduction_range)
        if self.sitting_prod_ctr >= self.unit_shelf_life: 
            self.sitting_prod_ctr = 0 
            self.units_dumped += 1 
            self.price = initial_price 

    def update_sold_to_all_in_chain(self): 
        self.sitting_prod_ctr = 0
        self.units_sold += 1 

        q = self.source 
        if type(q) == type(None): 
            return 
        q.update_sold()

    """
    instantiates another <MiddleAgentSeller> with an LCG PRNG, using the 
    next three values from this agent's PRNG. 
    """
    def reproduce(self,new_idn): 
        multiplier = modulo_in_range(self.prg(),DEFAULT_REPRODUCED_MIDDLE_AGENT_PRNG_LCG_MULTIPLIER_RANGE) 
        new_prng = prg_to_prg__LCG_sequence(self.prg,1,multiplier)[0] 
        M = MiddleAgentSeller(new_idn,self,self.price,self.unit_shelf_life,self.tax_range) 
        return M 

class MiddleAgentBuyer:

    def __init__(self,location,max_seller_candidates,prg,allow_memoryless_navigation:bool): 
        assert type(prg) in {MethodType,FunctionType} 
        assert type(max_seller_candidates) == int and max_seller_candidates > 0 

        self.starting_loc = location 
        self.prg = prg  
        self.allow_memoryless_navigation = allow_memoryless_navigation
        self.max_seller_candidates = max_seller_candidates

        self.seller_price_map = dict() 
        self.price_loaded = False 
        self.ref_graph = None 
        self.sellers = None 

        self.preproc() 
        return 

    def preproc(self): 
        self.navigator = NodeObjectiveNavigator(self.starting_loc,avoid_nodeset=set(),\
            take_nodeset=set(),objective_nodeset=set(),prg=self.prg) 

    """
    travels graph until at least one of three conditions is satisfied:
    - navigator reaches every node of graph 
    - navigator has reached `max_seller_candidates`
    - navigator has travelled |ref_graph.edges| edges, uniqueness not required.  
    """
    def travel_graph(self): 
        self.seller_price_map.clear() 
        self.price_loaded = False 
        self.clear_memory__memoryless_mode() 
        self.navigator.reset_location(self.starting_loc)

        num_nodes = len(self.ref_graph)
        max_travel = sum([len(v) for v in self.ref_graph.values()])

        touched_nodes = set([self.starting_loc]) 

        H = GraphNavigatorHandler(self.ref_graph,1,self.n,self.prg)
        for _ in range(max_travel): 

            # case: maximum number of sellers contacted 
            if len(self.seller_price_map) >= self.max_seller_candidates: 
                break 

            # case: all nodes have been reached 
            if len(touched_nodes) == num_nodes: 
                break 

            q = next(H) 
            touched_nodes |= {q} 
            if q in sellers: 
                self.seller_price_map[q] = None 


    def clear_memory__memoryless_mode(self): 
        if not self.allow_memoryless_navigation: 
            return 

        q = prg_decimal(self.prg,[0.,1.])

        # case: no clear 
        if q < 0.5: 
            return 

        self.navigator.clear_mainvars() 


    """
    ref_graph := defaultdict, undirected graph
    """
    def load_context(self,ref_graph,sellers:set): 
        assert type(ref_graph) == defaultdict
        assert self.loc in ref_graph 
        assert type(sellers) == set and len(sellers) > 0 

        self.ref_graph = ref_graph 
        self.sellers = sellers

    #-------------------------------------------------------

    def load_prices(self,seller_price_dict):
        assert seller_price_dict.keys() == self.seller_price_map.keys() 

        for k,v in seller_price_dict.items(): 
            self.seller_price_map[k] = v 
        self.price_loaded = True 
        return 

    def choose_seller(self): 
        q = [(k,v) for k,v in self.seller_price_map.items()]
        q_ = prg_seqsort_ties(q,self.prg,vf=lambda x:x[1])[-1]

        self.seller_price_map.clear() 
        self.price_loaded = False 
        return q_[0] 