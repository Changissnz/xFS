from graph_models.jamming_graph import * 
from .middle_agent import * 

DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE = [10,25]
DEFAULT_MIDDLE_AGENT_SOLD_UNITS_TO_REPRODUCE_RANGE = [6,16] 
DEFAULT_MIDDLE_AGENT_UNIT_SHELF_LIFE = [3,8] 
DEFAULT_MIDDLE_AGENT_LIFESPAN_RANGE = [6,16]

class MiddleManNetwork:  

    def __init__(self,buying_agent:MiddleAgentBuyer,unit_price,unit_shelf_life,\
        reprod_rate,jg:JammingGraph,prg):

        assert type(buying_agent) == MiddleAgentBuyer
        assert issubclass(type(jg),JammingGraph) 
        assert len(jg) == 3  

        self.buying_agent = buying_agent
        self.unit_price = unit_price 
        self.unit_shelf_life = unit_shelf_life
        self.reprod_rate = reprod_rate 
        self.jg = jg 
        self.prg = prg 

        self.middle_agents = dict()

        self.num_transactions = 0      
        return

    def __next__(self): 

        return -1 

    def move_buyer(self): 

        return -1 

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
            tax_range=DEFAULT_MIDDLE_AGENT_TAX_RANGE,\
            deduction_range=DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE)
        self.middle_agents[2] = s 

        # instantiate x middle-agents 
        
            # choose nodes for the agents 
        num_middle_agents = modulo_in_range(int(prg()),\
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
            s2 = MiddleAgentSeller(m,s,self.unit_price,self.prg,self.unit_shelf_life,\
                tax_range=DEFAULT_MIDDLE_AGENT_TAX_RANGE,\
                deduction_range=DEFAULT_MIDDLE_AGENT_DEDUCTION_RANGE)
            self.middle_agents[m] = s2 
        return  

    @staticmethod
    def generate_instance(jamming_graph_type,unit_price,allow_buyer_memoryless_navigation:bool,prg1,prg2):
        max_seller_candidates = modulo_in_range(int(prg()),\
            DEFAULT_MIDDLE_AGENT_BUYER__MAX_NUMBER_OF_SELLER_CANDIDATES_RANGE)

        buyer = MiddleAgentBuyer(location=0,max_seller_candidates=max_seller_candidates,\
            prg=prg1,allow_memoryless_navigation=allow_buyer_memoryless_navigation) 

        jg = JammingGraph.generate_3node_instance(is_directed=False,jam_type=jamming_graph_type,\
            prg=prg2,jam_nodesize_range=DEFAULT_JAMMING_GRAPH_JAMSIZE_RANGE)

        return MiddleManNetwork(buyer,unit_price,jg,prg2) 
