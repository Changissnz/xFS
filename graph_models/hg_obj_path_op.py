from .hg_obj_path import * 

DEFAULT_DIPNAV_LOG_LENGTH = 5 

class DIPathNavigator: 

    def __init__(self,G,node_value_range_map,prg):
        assert type(G) == defaultdict
        assert set(G.keys()) == set(node_value_range_map.keys())

        h,t,_,stat = verify_directed_implication_path(G) 
        assert stat 

        for v in node_value_range_map.values():
            assert is_valid_range(v,False,False) or is_valid_range(v,True,False)
            assert v[1] - v[0] > 10 ** -4 
            assert v[0] > 0 

        assert type(prg) in {MethodType,FunctionType} 

        self.G = G 
        self.head = h 
        self.tail = t 

        self.nv_map = node_value_range_map
        self.prg = prg 
        self.loc = None

        # each element is (node,value)
        self.active_path = [] 

        self.node_to_expense_map = defaultdict(list) 
        self.total_expense = 0 

        self.fin_stat = False 
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
        if self.fin_stat: return 

        # case: at head 
        if type(self.loc) == type(None): 
            n = self.head 
        else: 
            d = prg_decimal(self.prg,[0.,1.]) 

            # case: choose to backtrack 
            if d < 0.5 and len(self.active_path) > 0:
                x = self.active_path.pop(-1)
                if len(self.active_path) == 0: 
                    self.loc = None 
                else: 
                    self.loc = self.active_path[-1][0] 

                return False,x

            # case: move on 
            next_candidates = sorted(self.G[self.loc]) 
            i = int(self.prg()) % len(next_candidates) 
            n = next_candidates[i] 
        
        R = self.nv_map[n]
        expense_seq = self.node_to_expense_map[n] 
        if len(expense_seq) == 0: 
            R2 = R 
        else: 
            max_expense = max(expense_seq)#+ 10 ** -9 
            min_range = max([max_expense,R[0]]) 

            R2 = sorted([min_range,R[1]]) 

        v = modulo_in_range(self.prg(),R2) 
        self.node_to_expense_map[n].append(v) 
        self.node_to_expense_map[n] = self.node_to_expense_map[n][:DEFAULT_DIPNAV_LOG_LENGTH]

        return True,(n,v)

    def update_loc(self,loc): 
        assert loc in self.G 
        self.loc = loc 

        if self.loc == self.tail: 
            self.fin_stat = True 

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
        return DIPathNavigator(ptdi.G,ptdi.nv_map,prg) 

class DIPathNavigatorHandler: 

    def __init__(self,ptdi:PathTypeDI,dipn:DIPathNavigator,info_mode:int,verbose):  
        assert issubclass(type(ptdi),PathTypeDI) 
        assert type(dipn) == DIPathNavigator
        assert ptdi.nv_map == dipn.nv_map 

        self.ptdi = ptdi 
        self.dipn = dipn 
        self.info_mode = info_mode 
        self.verbose = verbose 
        return 

    def __next__(self): 
        
        if self.dipn.fin_stat: return 

        if self.verbose: 
            print("----------------------------------")
            print("LOC: ",self.dipn.loc)

        # have navigator make next node decision 
        is_forward,x = next(self.dipn)

        if self.verbose: 
            print("moving forward? ",is_forward) 
            if is_forward: 
                print("move to {} with support {}".format(x[0],x[1]))
            else: 
                print("backtracking from {}".format(x))

        # process according to advance or backtrack 
        if is_forward: 
            node_idn = x[0] 
            value = x[1] 
            is_advance,x2,stat1,stat2 = self.ptdi.register_advance(node_idn,value,self.verbose) 

            if self.verbose: 
                print("advancing? ",is_advance)
                if is_advance: 
                    print("difference with threshold: {}".format(x2))
                    print("success: {}".format(stat1))
                    print("immediate effect: {}".format(stat2)) 
                else: 
                    print("backtracking nodes: {}".format(x2))
                    print("location after backtracking: {}".format(stat1))

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
                        self.dipn.active_path.append((node_idn,value)) 
                        self.ptdi.navigator_path_record.append((node_idn,value))
                # case: success 
                else: 
                    self.dipn.active_path.append((node_idn,value))
                    self.dipn.update_loc(node_idn)                
                return 

            # backtrack 
            else:
                self.dipn.backtrack_from_nodeset(x2) 
                self.dipn.update_loc(stat1)

        else: 
            self.ptdi.register_backtrack()
        return 