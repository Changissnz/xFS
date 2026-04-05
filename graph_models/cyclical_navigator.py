from .base_node import * 
from morebs2.frequency_generator import * 
from morebs2.seq_repr import greatest_index_of_occurrence


"""
used to store information on cycle for <CyclicalNodeNavigatorTypeSM> to travel.
"""
class CycleObjective:

    def __init__(self):
        self.current_target = None 
        self.current_frequency = 0 
        self.current_index = None 
        self.target_frequency = None 
        self.target_finished = None 

    def is_active(self): 
        return type(self.current_target) != type(None) 

    def set_target(self,t,f):
        assert type(t) == list 
        assert type(f) == int and f > 0     
        self.current_target = t 
        self.target_frequency = f 
        self.target_finished = False 
        self.current_frequency = 0 
        self.current_index = 0
    
    def clear_target(self): 
        self.current_target = None 
        self.target_frequency = None 
        self.target_finished = None 
        self.current_frequency = 0 
        self.current_index = None 

    def reset_frequency(self,new_frequency): 
        self.target_frequency = new_frequency
        self.current_frequency = 0

    def decide(self,neighbors): 
        if self.current_frequency >= self.target_frequency: 
            self.target_finished = True 
            return None 

        if len(neighbors) == 0: return None 

        l = len(self.current_target)
        q = self.current_index + 1 
        if q >= l: 
            self.current_frequency += 1 
            q = q % l 
        self.current_index = q 

        n = self.current_target[q] 
        assert n in neighbors 
        return n  

    def register(self,travel_log): 
        if type(self.current_target) == type(None):
            return 
        loc = travel_log[-1] 

        q = self.current_target[self.current_index]
        assert q == loc
        return

"""
navigator that can travel a graph, repeating cycles, using `sparse memory`. 

`Sparse memory` consists of the travel log sequence of k <= `path_log_length` 
nodes, possibly non-unique, that the navigator has already travelled over. 

Shortest paths between nodes are not recorded into node memory. Node-to-cycle 
relations are also not recorded into node memory. Navigator bases its decisions 
on the travel log sequence.

Frequency of travel is calculated by Poisson distribution probabilities, given 
`frequency_range`. The boolean `skew_frequency` specifies whether navigator 
can extend its iteration over a cycle after the Poisson target frequency for 
travelling that cycle has been reached. When this parameter is set to True, 
navigator uses a decision process found in method<travel__objective_cycle> 
to determine the number of additional iterations to travel current cycle. 

NOTE: 
Navigator can be used with both directed and undirected graphs, but some of the 
decision-making processes suit undirected graph more. 

NOTE: 
Code is designed for navigator with radial vision of 1 edge. 

NOTE: 
Navigator is designed for use with immutable graphs (no changes in nodes and edges). 
"""
class CyclicalNodeNavigatorTypeSM(NodeObjectiveNavigator): 

    def __init__(self,starting_loc,prg,frequency_range,max_drift:int,\
        skew_frequency:bool=False,path_log_length=150,verbose=False): 

        assert type(starting_loc) != type(None)
        assert type(prg) in {MethodType,FunctionType}        
        #assert type(vary_centric) == bool 
        assert is_valid_range(frequency_range,True,False)
        assert frequency_range[0] > 0 
        assert type(max_drift) == int and max_drift > 1 
        assert type(skew_frequency) == bool == type(verbose)

        super().__init__(starting_loc,set(),set(),set(),prg,path_log_length,absolute_avoid=False,\
            risk_possible_avoid=False,nav_ctr=DEFAULT_NAVIGATOR_NODE_COUNTER)

        #self.centric_type = centric_type
        #self.vary_centric = vary_centric 
        self.max_drift = max_drift
        self.frequency_range = frequency_range
        self.skew_frequency = skew_frequency
        self.verbose = verbose 

        self.context = None
        self.is_roaming = False 

        self.drift_count = 0 

        self.cycle_objective = CycleObjective() 
        self.freq_gen = PoissonBasedFreqencyOutputter(self.prg)
        return

    def set_varying_obj(self,stat:bool): 
        assert type(stat) == bool 
        self.vary_centric = stat 
        return

    def set_roaming_mode(self,stat:bool): 
        assert type(stat) == bool 
        self.is_roaming = stat 
        self.cycle_objective.clear_target() 

    def make_choice(self): 
        # case: is_roaming 
        if self.is_roaming: 
            x = super().make_choice()
            return 

        if self.cycle_objective.is_active(): 
            q = self.travel__objective_cycle()
            if q: return 

        self.travel__null_objective() 

    def travel__null_objective(self):
        neighbors = self.context[self.loc]

        # check if any neighbors loop back to a previous node 
        x = set(self.path_log[:-1]) 

        I = x.intersection(neighbors)

        # case: no neighbors for looping, cannot drift anymore 
        if len(I) == 0 and self.drift_count >= self.max_drift:  
            # case: cannot drift anymore, try travelling backward. 
            q = self.path_log[-1] 

            # case: previous node cannot be reached, travel arbitrary 
            #       node 
            if q not in neighbors: 
                self.drift_one()
                return 
            # case: travel previous node 
            else:
                self.loc = q 
                index = greatest_index_of_occurrence(self.path_log,self.loc)
                assert type(index) != type(None) 
                self.set_objective(index) 
                self.drift_count = 0 
                self.update_travel_log()
            return 

        # case: no neighbors for looping, can drift 
        if len(I) == 0: 
            self.drift_one()
            return

        # case: choose a neighbor to loop to 
        I = sorted(I) 
        i = int(self.prg()) % len(I) 
        n = I[i]
        self.loc = n 
        index = greatest_index_of_occurrence(self.path_log,self.loc) 
        self.set_objective(index) 
        self.update_travel_log()    
        self.drift_count = 0     
        return

    def drift_one(self): 
        if self.verbose: print("drifting") 

        neighbors = self.context[self.loc]
        if len(neighbors) == 0: return 

        N = sorted(neighbors) 
        i = int(self.prg()) % len(N)
        n = N[i] 
        self.loc = n 
        self.drift_count += 1 
        self.update_travel_log()

    def set_objective(self,suffix_start_index): 
        T = self.path_log[suffix_start_index:]

        expected = modulo_in_range(self.prg(),self.frequency_range) 
        f = self.freq_gen.out(expected,self.frequency_range)

        self.cycle_objective.set_target(T,f)

    def travel__objective_cycle(self): 
        neighbors = self.context[self.loc]
        if len(neighbors) == 0: return False 

        q = self.cycle_objective.decide(neighbors) 

        # case: finished with cycling 
        if type(q) == type(None): 
            # case: longer cycling possible
            if self.skew_frequency:
                m = (self.frequency_range[1] - self.frequency_range[0]) / 2
                r = [0,ceil(m)]
                f = self.freq_gen.out(ceil(m/2),r) 
                # subcase: extending cycling 
                if f > 0: 
                    if self.verbose: print("extending travel of current cycle with {} iterations".format(f)) 
                    self.cycle_objective.reset_frequency(f) 
                    return self.travel__objective_cycle()

            # case: clear cycle objective  
            self.cycle_objective.clear_target()
            return False 

        # case: continue on cycling 
        self.loc = q 
        self.update_travel_log() 
        self.cycle_objective.register(self.path_log) 
        return True 