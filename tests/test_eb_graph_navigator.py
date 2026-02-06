from graph_models.graph_gen import * 
from morebs2.numerical_generator import prg__LCG 
from graph_models.shortest_paths_approx import * 
from graph_models.radial_subgraph import * 
from graph_models.eb_graph_navigator import * 
import unittest 

def base_graph_info__sample_R(add_edge_weights=False): 
    prg = prg__LCG(67.4,-100,89.6,9196.66)
    is_realtime_gen = True 
    vertex_degree = 50 
    edge_connectivity = 0.1   
    gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=is_realtime_gen,\
            vertex_degree=vertex_degree,edge_connectivity=edge_connectivity,\
            verbose=False)
    gg.full_run() 

    G = graph_to_one_component(gg.d,prg) 

    if add_edge_weights: 
        gw = GraphWeightGen(G,prg,is_dsg=False,weight_range=[1.,10.]) 
        edge_cost_function = gw.weight 
    else: 
        edge_cost_function = DEFAULT_EDGE_COST_FUNCTION_2

    P = BDFSCache.BFS_full(G,return_type="paths",prg=prg,max_search_radius=float('inf'),\
            edge_cost_function=edge_cost_function,verbose=False)[0] 
    qsf = QuickSubgraphFetcher(G,prg=prg,\
        edge_cost_function=DEFAULT_EDGE_COST_FUNCTION_2)

    return G,P,qsf,prg 

"""
two agents for the setting of <base_graph_info__sample_R>. 
"""
def EnergyBasedGraphNavigator__sample_two_agents(prg): 

    idn = 0 
    loc = 0 
    energy = 200 
    is_bull = True 
    en0 = EnergyBasedGraphNavigator(idn,loc,energy,prg,is_bull,verbose=True)

    idn1 = 1
    loc1 = 21  
    energy1 = 200 
    is_bull1 = False  
    en1 = EnergyBasedGraphNavigator(idn1,loc1,energy1,prg,is_bull1,verbose=True)
    return en0,en1 

def EnergyBasedGraphNavigator__sample_three_agents(prg): 
    en0,en1 = EnergyBasedGraphNavigator__sample_two_agents(prg)  

    idn2 = 2
    loc2 = 43  
    energy2 = 200 
    is_bull2 = False  
    en2 = EnergyBasedGraphNavigator(idn2,loc2,energy2,prg,is_bull2,verbose=True)

    return en0,en1,en2 

"""
py -m tests.test_eb_graph_navigator
"""
class EnergyBasedGraphNavigatorClass(unittest.TestCase):

    """
    On graph with unit weight=1.  

    Bull and Chaser are in vicinity of each other. Chaser chooses 
    to travel to next node not of the Bull's current node location. 

    Neither Bull nor Chaser know the next paths of each other. 
    """
    def test__EnergyBasedGraphNavigator__next__case_1(self):
        print("\t\t** CASE 1")
        G,P,qsf,prg = base_graph_info__sample_R(False) 

        # bull is at node 0 
        G0 = qsf.subgraph(0,2) 

        # agent 1 is at node 21 
        G21 = qsf.subgraph(21,2) 

        en0,en1 = EnergyBasedGraphNavigator__sample_two_agents(prg) 

        min_paths0 = fetch_paths_for_nodeset(P,set(G0.keys())) 
        en0.receive_context(G0,min_paths0,None,{21})   

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en1.receive_context(G21,min_paths21,0,None)   

        en0.agent_predicts_best_path__bull(None)
        en1.agent_predicts_best_path__chaser(None,[])

        q0 = next(en0)
        q21 = next(en1) 

        assert en0.location() == 26 
        assert en1.location() == 46 
        assert P[(26,46)].cost() == 1 

    """
    On graph with variable weights. 

    Bull and Chaser are in vicinity of each other. Chaser chooses 
    to travel to next node that is the Bull's current node location. 

    Neither Bull nor Chaser know the next paths of each other. 
    """
    def test__EnergyBasedGraphNavigator__next__case_2(self):
        print("\t\t** CASE 2")
        G,P,qsf,prg = base_graph_info__sample_R(True) 

        # bull is at node 0 
        G0 = qsf.subgraph(0,2) 

        # agent 1 is at node 21 
        G21 = qsf.subgraph(21,2) 

        en0,en1 = EnergyBasedGraphNavigator__sample_two_agents(prg) 

        min_paths0 = fetch_paths_for_nodeset(P,set(G0.keys())) 
        en0.receive_context(G0,min_paths0,None,{21})   

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en1.receive_context(G21,min_paths21,0,None)   

        en0.agent_predicts_best_path__bull(None)
        en1.agent_predicts_best_path__chaser(None,[])

        q0 = next(en0)
        q21 = next(en1) 

        assert en0.location() == 8,"got {}".format(en0.location())
        assert en1.location() == 0,"got {}".format(en1.location())

    """
    Bull and two Chasers are in vicinity of each other. Chaser chooses 
    to travel to next node that is the Bull's current node location. 

    Neither Bull nor Chasers know the next paths of each other. 
    """
    def test__EnergyBasedGraphNavigator__next__case_3(self):
        print("\t\t** CASE 3")
        G,P,qsf,prg = base_graph_info__sample_R(False) 

        loc1,loc2 = 21,43

        # bull is at node 0 
        G0 = qsf.subgraph(0,2) 

        # agent 1 is at node 21 
        G21 = qsf.subgraph(loc1,2) 

        # agent 2 is at node 43 
        G43 = qsf.subgraph(loc2,2) 

        en0,en1,en2 = EnergyBasedGraphNavigator__sample_three_agents(prg) 

        min_paths0 = fetch_paths_for_nodeset(P,set(G0.keys())) 
        en0.receive_context(G0,min_paths0,None,{21})   

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en1.receive_context(G21,min_paths21,0,None)   
        min_paths_other = fetch_paths_from_node_to_nodeset(P,loc1,set(G43.keys()))
        en1.add_other_chasers_info({2:(loc2,set(G43.keys()))},min_paths_other)

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en2.receive_context(G21,min_paths21,0,None)   
        min_paths_other = fetch_paths_from_node_to_nodeset(P,loc2,set(G21.keys()))
        en2.add_other_chasers_info({1:(loc1,set(G21.keys()))},min_paths_other)

        en0.agent_predicts_best_path__bull(None)
        en1.agent_predicts_best_path__chaser(None,[])
        en2.agent_predicts_best_path__chaser(None,[(en1.current_path,en1.mode)])

        q0 = next(en0)
        q21 = next(en1) 
        q43 = next(en2) 

        assert en0.location() == 26 
        assert en1.location() == 46 
        assert en2.location() == 31

    """
    Bull and two Chasers are in vicinity of each other. Chaser chooses 
    to travel to next node that is the Bull's current node location. 

    Bull does not know Chasers' next paths. 
    Chasers know Bull's next path. 

    Checks for non-duplicate node location of Chaser after they travel.  
    """
    def test__EnergyBasedGraphNavigator__next__case_4(self):
        print("\t\t** CASE 4")
        G,P,qsf,prg = base_graph_info__sample_R(False) 

        loc1,loc2 = 21,43

        # bull is at node 0 
        G0 = qsf.subgraph(0,2) 

        # agent 1 is at node 21 
        G21 = qsf.subgraph(loc1,2) 

        # agent 2 is at node 43 
        G43 = qsf.subgraph(loc2,2) 

        en0,en1,en2 = EnergyBasedGraphNavigator__sample_three_agents(prg) 

        min_paths0 = fetch_paths_for_nodeset(P,set(G0.keys())) 
        en0.receive_context(G0,min_paths0,None,{21})   

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en1.receive_context(G21,min_paths21,0,None)   
        min_paths_other = fetch_paths_from_node_to_nodeset(P,loc1,set(G43.keys()))
        en1.add_other_chasers_info({2:(loc2,set(G43.keys()))},min_paths_other)

        min_paths21 = fetch_paths_for_nodeset(P,set(G21.keys())) 
        en2.receive_context(G21,min_paths21,0,None)   
        min_paths_other = fetch_paths_from_node_to_nodeset(P,loc2,set(G21.keys()))
        en2.add_other_chasers_info({1:(loc1,set(G21.keys()))},min_paths_other)

        en0.agent_predicts_best_path__bull(None)
        en1.agent_predicts_best_path__chaser(en0.current_path,[])
        en2.agent_predicts_best_path__chaser(en0.current_path,[(en1.current_path,en1.mode)])

        q0 = next(en0)
        q21 = next(en1) 
        q43 = next(en2) 

        assert en0.location() == 26 
        assert en1.location() == 26 
        assert en2.location() == 34 
        assert P[(26,34)].cost() == 2 


if __name__ == "__main__":
    unittest.main()