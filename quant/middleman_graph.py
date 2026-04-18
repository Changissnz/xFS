from graph_models.jamming_graph import * 
from .middle_agent import * 

DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE = [10,25]
DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE = [6,16] 
DEFAULT_MIDDLE_AGENT_UNIT_SHELF_LIFE = [3,8] 
DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE = [6,16]

class MiddleManNetwork:  

    def __init__(self,buying_agent:MiddleAgentBuyer,unit_price,unit_shelf_life,\
        reprod_rate,seller_lifespan:int,jg:JammingGraph,prg):

        assert type(buying_agent) == MiddleAgentBuyer
        assert is_number(unit_price) 
        assert type(unit_shelf_life) == int and unit_shelf_life > 0 
        assert type(reprod_rate) == int and reprod_rate > 0 
        assert type(seller_lifespan) == int and seller_lifespan > 0 

        assert issubclass(type(jg),JammingGraph) 
        assert len(jg) == 3  

        self.buying_agent = buying_agent
        self.unit_price = unit_price 
        self.unit_shelf_life = unit_shelf_life
        self.reprod_rate = reprod_rate 
        self.seller_lifespan = seller_lifespan
        self.jg = jg 
        self.prg = prg 

        self.middle_agents = dict()
        self.num_transactions = 0    

        self.preproc()  
        return

    def __next__(self): 
        self.reset_seller_sold_stat() 

        # move buyer 
        seller_idn = self.move_buyer()

        # move sellers 
        self.one_transaction(seller_idn)
        return

    def set_prg(self,prg,agent_idn):
        assert type(prg) in {MethodType,FunctionType}

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

        # send prices to buyer 
        self.transmit_prices_to_buyer() 

        # have buyer decide 
        return self.buying_agent.choose_seller()

    """
    sends the prices of all sellers buyer contacted, during this 
    time duration. 
    """
    def transmit_prices_to_buyer(self): 
        d = dict()
        for k in self.buying_agent.seller_price_map.keys(): 
            d[k] = self.middle_agents[k].price 
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

        # case: delete bankrupt nodes 
        self.jg.delete_nodeset(bankrupt) 

            # ensure graph is one component 
        self.jg.G = graph_to_one_component(self.jg.G,self.prg) 

            # delete the agents from the map 
        for b in bankrupt: 
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