from graph_models.jamming_graph import * 
from .middle_agent import * 
from collections import Counter 

# starting number of middle agent sellers 
DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE = [10,25]

# number of units a middle agent must sell before reproducing 
DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE = [6,16] 

# number of timestamps an agent has to sell an existing unit 
DEFAULT_MIDDLE_AGENT_UNIT_SHELF_LIFE = [3,8] 

# number of dumped units before bankruptcy (termination)
DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE = [6,16]

# number of units a seller can sell before pseudo-random termination 
# by network 
DEFAULT_MIDDLE_AGENT_DOMINANT_SELLER_TERMINATION_RANGE = \
    [int(DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE[1] * 1.5),
    DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE[1] * 2] 

# length of seller idn. log used by network for dominant seller termination 
DEFAULT_MIDDLE_AGENT_SELLER_LOG_SIZE = \
    DEFAULT_MIDDLE_AGENT_DOMINANT_SELLER_TERMINATION_RANGE[1] * 20 

"""
The network structure used for the Middleman bot. 

Features one buying agent and a variable number of sellers. Number of sellers increases 
and decreases according to specific seller frequencies that satisfy the parameter 
values of the middle agent default variables (top of this file).
"""
class MiddleManNetwork:  

    def __init__(self,buying_agent:MiddleAgentBuyer,unit_price,unit_shelf_life,\
        reprod_rate,seller_lifespan:int,jg:JammingGraph,prg,verbose:bool=False):

        assert type(buying_agent) == MiddleAgentBuyer
        assert is_number(unit_price) 
        assert type(unit_shelf_life) == int and unit_shelf_life > 0 
        assert type(reprod_rate) == int and reprod_rate > 0 
        assert type(seller_lifespan) == int and seller_lifespan > 0 

        assert issubclass(type(jg),JammingGraph) 
        assert len(jg) == 3  
        assert type(prg) in {MethodType,FunctionType}
        assert type(verbose) == bool 

        self.buying_agent = buying_agent
        self.unit_price = unit_price 
        self.unit_shelf_life = unit_shelf_life
        self.reprod_rate = reprod_rate 
        self.seller_lifespan = seller_lifespan
        self.jg = jg 
        self.prg = prg 
        self.verbose = verbose 

        self.middle_agents = dict()
        self.num_transactions = 0   
        self.eliminated_dominants = set()  
        self.eliminated_bankrupts = set() 

        self.preproc()  
        self.seller_idn_log = [] 
        return

    def __next__(self): 
        self.reset_seller_sold_stat() 

        # move buyer 
        if self.verbose: 
            print("timestamp: {}".format(self.buying_agent.units_bought)) 

        seller_idn = self.move_buyer()

        # case: no sell 
        if type(seller_idn) == type(None): return 
        
        if self.verbose: 
            print("\t buy from seller: {}".format(seller_idn))

        # move sellers 
        self.one_transaction(seller_idn)

        # delete any seller that is dominant 
        self.eliminate_dominant_sellers() 

        self.num_transactions += 1 
        return

    def set_prg(self,prg,agent_idn,for_buying_agent:bool=False): 
        assert type(prg) in {MethodType,FunctionType}

        if for_buying_agent:
            assert type(agent_idn) == type(None) 
            self.buying_agent.prg = prg 

        if type(agent_idn) == type(None): 
            self.prg = prg 
        else: 
            assert agent_idn in self.middle_agents 
            self.middle_agents[agent_idn].prg = prg 

    """
    instantiates x middle-agents in the beginning
    """
    def preproc(self): 

        # instantiate a MiddleAgentSeller for node 2 (original seller)
        s = MiddleAgentSeller(2,None,self.unit_price,self.prg,self.unit_shelf_life,\
            self.seller_lifespan,tax_range=DEFAULT_MIDDLE_AGENT_TAX_RANGE,\
            deduction_range=DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE)
        self.middle_agents[2] = s 

        # instantiate x middle-agents 
        
            # choose nodes for the agents 
        num_middle_agents = modulo_in_range(int(self.prg()),\
            DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE)

        stat = True 
        while stat: 
            self.jg.one_jam(1,False) 
            for v in self.jg.G.values(): 
                assert None not in v 

            q = self.jg.entire_nodeset_for_node(1)

            if len(q) >= num_middle_agents: 
                stat = False 

        q = sorted(self.jg.entire_nodeset_for_node(1))
        middle_agents = prg_choose_n(q,num_middle_agents,\
            prg__single_to_int(self.prg),is_unique_picker=True)

            # instantiate each middle-agent 
        for m in middle_agents: 
            s2 = MiddleAgentSeller(m,s,s.initial_price,self.prg,self.unit_shelf_life,\
                self.seller_lifespan,tax_range=DEFAULT_MIDDLE_AGENT_TAX_RANGE,\
                deduction_range=DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE)
            self.middle_agents[m] = s2 
        return  

    #-------------------------------- code for buyer actions
    #-------------------- travelling the network, choosing a seller to buy from 

    def move_buyer(self): 
        # travel network to search for seller with cheapest price 
        x = set(self.middle_agents.keys())
        self.buying_agent.load_context(self.jg.G,\
            sellers=x)
        self.buying_agent.travel_graph() 

        # case: ?strange,no buyers could be found?
        if len(self.buying_agent.seller_price_map) == 0: 
            return None 

        # send prices to buyer 
        self.transmit_prices_to_buyer() 

        # have buyer decide 
        s = self.buying_agent.choose_seller()

        # log seller into log 
        self.log_seller(s) 
        
        return s 

    def log_seller(self,idn): 
        self.seller_idn_log.append(idn) 
        while len(self.seller_idn_log) > DEFAULT_MIDDLE_AGENT_SELLER_LOG_SIZE: 
            self.seller_idn_log.pop(0) 

    """
    sends the prices of all sellers buyer contacted, during this 
    time duration. 
    """
    def transmit_prices_to_buyer(self): 
        d = dict()
        for k in self.buying_agent.seller_price_map.keys(): 
            d[k] = self.middle_agents[k].price 
        
        if self.verbose: 
            q = sorted([(k,v) for k,v in d.items()],key=lambda x:x[1])
            print("--- seller / prices")
            for q_ in q: 
                print("\t\t{} / {}".format(q_[0],q_[1]))

        self.buying_agent.load_prices(d) 

    #------------------------------------------ seller actions 

    def reset_seller_sold_stat(self): 
        for s in self.middle_agents.values(): 
            s.mark_sold(False)

    def one_transaction(self,seller_idn): 
        # register all sellers in chain of sellers related 
        # to direct seller that sold  
        s = self.middle_agents[seller_idn]
        s.mark_sold(True) 
        chain_members = s.update() 

        if self.verbose: 
            print("total number of sellers: {}".format(len(self.middle_agents)))
            print("all sellers involved")
            print(sorted(chain_members)) 

        # register all other sellers that did not sell 
        q = set(self.middle_agents.keys()) - chain_members 

        for q_ in q: 
            s2 = self.middle_agents[q_] 
            s2.update() 

        # clear bankrupt 
        self.clear_bankrupt_sellers() 

        # reproduce 
        self.reproduce_sellers() 

    def fetch_reproducible_sellers(self): 
        reproducible = set() 

        for k,v in self.middle_agents.items(): 
            if v.units_sold_ >= self.reprod_rate:  
                reproducible |= {k}
        return reproducible 

    def reproduce_sellers(self): 
        reproducible = sorted(self.fetch_reproducible_sellers()) 

        if self.verbose: 
            print("sellers reproducing:\n{}".format(sorted(reproducible)))

        for r in reproducible: 
            # one jam 
            self.jg.one_jam(1,False)

            # fetch new nodes from that jam 
            new_nodes = sorted(self.jg.new_nodes) 

            # choose a new node to be another seller 
            i = int(self.prg()) % len(new_nodes)
            n = new_nodes[i] 

            # reproduce 
            source = self.middle_agents[r] 
            m = source.reproduce(n) 
            self.middle_agents[n] = m  
        return 


    def fetch_bankrupt_sellers(self): 
        bankrupt = set() 

        for k,v in self.middle_agents.items(): 
            if v.units_dumped >= self.seller_lifespan: 
                bankrupt |= {k} 
        return bankrupt 

    def clear_bankrupt_sellers(self): 
        bankrupt = self.fetch_bankrupt_sellers() 

        # case: none are bankrupt 
        if len(bankrupt) == 0: return 

        if self.verbose: 
            print("bankrupt sellers: {}".format(sorted(bankrupt))) 

        self.eliminated_bankrupts |= bankrupt 
        self.delete_sellers(bankrupt) 

    def eliminate_dominant_sellers(self): 
        l = len(self.seller_idn_log) - 1

        # case: empty log 
        if l < 0: 
            return 

        sold_units_threshold = safe_modulo_in_range(int(self.prg()),\
            DEFAULT_MIDDLE_AGENT_DOMINANT_SELLER_TERMINATION_RANGE)

        c = Counter(self.seller_idn_log)
        x = sorted([(k,v) for k,v in c.items()],key=lambda x:x[1])  

        to_eliminate = set() 
        while len(x) > 0: 
            q = x.pop(-1) 
            if q[1] >= sold_units_threshold:
                to_eliminate |= {q[0]}
            else: 
                break 

        to_eliminate = to_eliminate.intersection(set(self.middle_agents.keys()))

        if len(to_eliminate) > 0: 
            self.eliminated_dominants |= to_eliminate
            if self.verbose: 
                print("** eliminating dominant sellers {}".format(\
                    sorted(to_eliminate))) 
            self.delete_sellers(to_eliminate)

    def delete_sellers(self,nodeset):
        # case: delete nodeset 
        self.jg.delete_nodeset(nodeset) 

            # ensure graph is one component 
        self.jg.G = graph_to_one_component(self.jg.G,self.prg) 

            # delete the agents from the map 
        for b in nodeset:
            if b not in self.middle_agents: continue 

            del self.middle_agents[b]  
        return

    @staticmethod
    def generate_instance(jamming_graph_type,unit_price,\
        allow_buyer_memoryless_navigation:bool,prg1,prg2):

        max_seller_candidates = modulo_in_range(int(prg1()),\
            DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE)

        buyer = MiddleAgentBuyer(location=0,max_seller_candidates=max_seller_candidates,\
            prg=prg1,allow_memoryless_navigation=allow_buyer_memoryless_navigation) 

        jg = JammingGraph.generate_3node_instance(is_directed=False,jam_type=jamming_graph_type,\
            prg=prg2,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE)

        unit_shelf_life = modulo_in_range(int(prg2()),DEFAULT_MIDDLE_AGENT_UNIT_SHELF_LIFE)
        reprod_rate = modulo_in_range(int(prg2()),\
            DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE)
        seller_rate = modulo_in_range(int(prg2()),\
            DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE)
        return MiddleManNetwork(buyer,unit_price,unit_shelf_life,\
            reprod_rate,seller_rate,jg,prg2)