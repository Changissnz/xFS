
from morebs2.numerical_generator import prg_unique_sequence,modulo_in_range
from morebs2.matrix_methods import is_valid_range
from types import FunctionType,MethodType

"""
A structure with method<node_to_output> that has its uses, such 
as for 
- variable<StaticGraphIntrospector.node2output_function>.

Every node is associated with a cycle C and a current index i for 
that cycle. When node is called with method<node_to_output>, outputs 
C[i] and increments i. 
"""
class Node2CycleOutputter: 

    def __init__(self,node2cycle_map):
        assert type(node2cycle_map) == dict 
        for v in node2cycle_map.values(): assert len(v) > 0 and type(v) == list 

        self.n2c_map = node2cycle_map
        self.n2c_index_map = {k:0 for k in self.n2c_map.keys()}
        return

    def check_for_keys(self,keys): 
        return set(self.n2c_map.keys()) == set(keys)

    def node_to_output(self,n): 
        assert n in self.n2c_map 

        c = self.n2c_map[n] 
        l = len(c) 

        i = self.n2c_index_map[n] 
        i2 = (i + 1) % l 

        self.n2c_index_map[n] = i2 
        return c[i] 

    @staticmethod 
    def generate_instance(nodeset,cycle_length_range,prg):
        assert is_valid_range(cycle_length_range,True,False) 
        assert cycle_length_range[0] > 1 
        assert type(prg) in {MethodType,FunctionType}

        nodeset = sorted(nodeset) 
        D = dict() 
        for n in nodeset: 
            l = modulo_in_range(int(prg()),cycle_length_range)
            D[n] = prg_unique_sequence(prg,l) 
        return Node2CycleOutputter(D)

#------------------------------------------------------------------

"""
A variant of class<Node2CycleOutputter>. 

During calls to method<node_to_output>, variant generates cycles for nodes not present in map.
"""
class CumulativeNode2Cycle(Node2CycleOutputter): 

    def __init__(self,node2cycle_map,cycle_length_range,prg):

        super().__init__(node2cycle_map) 

        assert is_valid_range(cycle_length_range,True,False) 
        assert cycle_length_range[0] > 0 
        assert type(prg) in {MethodType,FunctionType}  

        self.cycle_length_range = cycle_length_range
        self.prg = prg 
        return

    def node_to_output(self,n): 
        if n not in self.n2c_map: 
            l = modulo_in_range(int(self.prg()),self.cycle_length_range)
            self.n2c_map[n] = prg_unique_sequence(self.prg,l) 
            self.n2c_index_map[n] = 0 

        return super().node_to_output(n) 

    @staticmethod 
    def generate_instance(nodeset,cycle_length_range,prg):

        Q = Node2CycleOutputter.generate_instance(nodeset,cycle_length_range,prg) 
        return CumulativeNode2Cycle(Q.n2c_map,cycle_length_range,prg) 