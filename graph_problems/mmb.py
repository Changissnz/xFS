from quant.middleman_graph import * 

class MiddleManBot(MiddleManNetwork): 

    def __init__(self,buying_agent:MiddleAgentBuyer,unit_price,unit_shelf_life,\
        reprod_rate,seller_lifespan:int,jg:JammingGraph,prg,verbose:bool=False):

        super().__init__(buying_agent,unit_price,unit_shelf_life,reprod_rate,\
            seller_lifespan,jg,prg,verbose) 
        return 

    @staticmethod 
    def generate_instance(jamming_graph_type,unit_price,\
        allow_buyer_memoryless_navigation:bool,prg1,prg2):
        
        mm = MiddleManNetwork.generate_instance(\
            jamming_graph_type,unit_price,\
            allow_buyer_memoryless_navigation,\
            prg1=prg1,prg2=prg2)

        return MiddleManBot(mm.buying_agent,mm.unit_price,mm.unit_shelf_life,\
            mm.reprod_rate,mm.seller_lifespan,mm.jg,mm.prg,mm.verbose)