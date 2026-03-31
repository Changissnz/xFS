from graph_models.graph_gen import * 
from graph_models.pswap_graph import * 

DEFAULT_TOKEN_SWAPPING_BOT_NODE_SIZE = [40,1000]

class TokenSwappingBot(PSGraphHandler): 

    def __init__(self,pg:PSwapGraph):
        assert type(pg) == PSwapGraph
        super().__init__(pg)

    def set_prg(self,prg):
        assert type(prg) in {MethodType,FunctionType} 
        self.pg.prg = prg 

    @staticmethod 
    def generate_instance(prg,verbose=True):

        num_nodes = modulo_in_range(int(prg()),DEFAULT_TOKEN_SWAPPING_BOT_NODE_SIZE) 

        if num_nodes < 100: 
            ratio_range = [0.09,0.22] 
        else: 
            ratio_range = [0.006,0.03] 

        ratio = modulo_in_range(prg(),ratio_range) 

        is_realtime_gen = prg_decimal(prg,[0.,1]) >= 0.5 
        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
            vertex_degree=num_nodes,edge_connectivity=ratio,verbose=False)
        gg.full_run()

        G = gg.d 
        graph_to_one_component(G,prg) 

        P = PSwapGraph.generate_token_placement(num_nodes,prg)
        pg = PSwapGraph(G,P,prg,DEFAULT_EDGE_COST_FUNCTION_2,verbose=verbose)

        return TokenSwappingBot(pg) 