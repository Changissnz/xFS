from morebs2.numerical_generator import * 

'''
converging linear congruential generator 
'''
class CLCG:

    def __init__(self):
        return -1 

    def gd_preproc(self):
        self.io_map()
        self.io_map_partition()
        self.io_map_summary()

    def io_map(self):
        self.map_io.clear()
        for x in range(self.r[0],self.r[1]): 
            y = modulo_in_range(x * self.m + \
                self.a,self.r) 
            self.map_io[x] = y 

    def io_map_partition(self): 
        qx = defaultdict(set)
        for k,v in self.map_io.items():
            qx[k] = set([v]) 

        self.gd = GraphComponentDecomposition(qx) 
        self.gd.decompose()

    def io_map_summary(self):
        for i in range(len(self.gd.components)):
            cd = self.component_index_summary(i)
            self.cycle_descriptors.append(cd) 