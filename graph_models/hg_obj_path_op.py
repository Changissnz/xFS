from .hg_obj_path import * 

class DIPathNavigator: 

    def __init__(self,G,node_value_range_map,prg):#,h2t_paths): 
        assert type(G) == defaultdict
        assert set(G.keys()) == set(node_value_range_map.keys())

        h,_,_,stat = verify_directed_implication_path(G) 
        assert stat 

        for v in node_value_range_map.values():
            assert is_valid_range(v,False,False) or is_valid_range(v,True,False)
            assert v[1] - v[0] > 10 ** 4 
            assert v[0] > 0 

        assert type(prg) in {MethodType,FunctionType} 

        self.G = G 
        self.head = h 

        self.nv_range = node_value_range_map
        self.prg = prg 
        self.loc = None

        # each element is (node,value)
        self.active_path = [] 

        self.node_to_expense_map = defaultdict(list) 
        self.total_expense = 0 

        return

    """
    return: 
    - [0] ?move forward? 
    - [1] forward: 
            (next node,support value)
          backward:
            node backtracked from 
    """
    def __next__(self): 
        
        # case: at head 
        if type(self.loc) == type(None): 
            n = self.head 
        else: 
            d = prg_decimal(self.prg,[0.,1.]) 

            # case: choose to backtrack 
            if d < 0.5:
                x = self.active_path.pop(-1)
                if len(self.active_path) == 0: 
                    self.loc = None 
                else: 
                    self.loc = self.active_path[-1][0] 

                return False,x

            # case: move on 
            else: 
                next_candidates = sorted(self.G[self.loc]) 
                i = int(self.prg()) % len(next_candidates) 
                n = next_candidates[i] 
        
        R = self.nv_range[n]
        expense_seq = self.node_to_expense_map[n] 
        max_expense = max(expense) + 10 ** -9 

        min_range = max([max_expense,R[0]]) 
        R2 = sorted([min_range,R[1]]) 

        v = modulo_in_range(self.prg(),R2) 
        return (n,v)

    def update_loc(self,loc): 
        assert loc in self.G 

        self.loc = loc 

    """
    used in cases of rejection from <PathTypeDI>. 
    """
    def revert_to_node(self,node_idn): 
        if node_idn == self.loc: return 

        x = [a[0] for a in self.active_path] 
        assert node_idn in x 

        i = x.index(node_idn) 

        self.active_path = self.active_path[:i+1] 
        self.loc = node_idn 

    def backtrack_from_nodeset(self,nodeset): 
        x = [a[0] for a in self.active_path] 
        indices = [x.index(n) for n in nodeset] 
        index = min(indices)
        self.active_path = self.active_path[:index] 

    @staticmethod
    def from_PathTypeDI(ptdi:PathTypeDI,prg): 
        assert issubclass(type(ptdi),PathTypeDI) 
        assert type(prg) in {MethodType,FunctionType}
        return DIPathNavigator(ptdi.G,ptdi.nv_map,prg,ptdi.min_paths) 

class DIPathNavigatorHandler: 

    def __init__(self,ptdi:PathTypeDI,dipn:DIPathNavigator,info_mode:int):  
        assert issubclass(type(ptdi),PathTypeDI) 
        assert type(dipn) == DIPathNavigator

        self.ptdi = ptdi 
        self.dipn = dipn 
        self.info_mode = info_mode 
        return 

    def __next__(self): 

        # have navigator make next node decision 
        is_forward,x = next(self.dipn)

        # process according to advance or backtrack 
        if is_forward: 
            node_idn = x[0] 
            value = x[1] 
            is_advance,x2,stat1,stat2 = self.ptdi.register_advance(node_idn,value) 
            
            # 
            if is_advance: 
                
                # case: failure 
                if not stat1: 
                    # case: immediate failure, do not advance 
                    if stat2: 
                        return 
                    # case: pending failure, advance 
                    else: 
                        self.dipn.update_loc(node_idn)
                # case: success 
                else: 
                    self.dipn.update_loc(node_idn)                
                return 

            # backtrack 
            else:
                self.dipn.backtrack_from_nodeset(x2) 
                self.dipn.update_loc(stat1)

        else: 
            self.ptdi.register_backtrack()
        return 