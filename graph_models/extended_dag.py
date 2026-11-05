from .dag_gen import * 

"""
Extended (D)irected (A)cyclic (G)raph Type 
(L)inear (T)hreshold (P)er (N)ode. 

Calculates booleans from inputs of node `n`, found in `G`, 
and an index-to-bool map `M`. 

For a node `n`, the `vfunc` outputs a sequence of indices V (keys 
of `M`) that are pertinent to `n`. The `wfunc` function outputs 
a vector of weights W associated with V. The `tfunc` function outputs 
a value f in [0.,1.]. All three of these functions take arbitrary 
node `n` of `G` as the parameter.

If the values V of the input map `M` multiplied with W results in 
r, such that 
    r >= f * sum(W), 
then boolean is TRUE. Otherwise, it is False. 

NOTE: function designed to be activation function. Typically, 
weight vectors outputted from `wfunc` have non-negative values. 
"""
class ExtendedDAGTypeLTPN(DAGraphContainer): 

    def __init__(self,G,l2n_map,vfunc,wfunc,tfunc,check_input_graph:bool=True):
        assert type(vfunc) in {MethodType,FunctionType}
        assert type(wfunc) in {MethodType,FunctionType}
        assert type(tfunc) in {MethodType,FunctionType}
        super().__init__(G,l2n_map,check_input_graph) 

        self.vfunc = vfunc 
        self.wfunc = wfunc 
        self.tfunc = tfunc 

    def boolean_output(self,n,index2bool_map): 
        assert n in self.G 
        assert type(index2bool_map) == dict 

        indices = self.vfunc(n) 
        weight_vec = np.array(self.wfunc(n)) 
        assert len(indices) == len(weight_vec) 
        threshold = self.tfunc(n)

        index_vec = np.zeros(len(weight_vec))
        for (j,i) in enumerate(indices): 
            if i in index2bool_map: 
                q = int(index2bool_map[i]) 
                index_vec[j] = q 

        s = np.sum(index_vec * weight_vec) 

        r = s / np.sum(weight_vec) 
        return r >= 0.5 