from .hg_obj_path import * 
from morebs2.v2f_solver import * 
from morebs2.numerical_generator import is_number 

DEFAULT_DIPNAV_LOG_LENGTH = 5 
DEFAULT_DIPNAV_LINEXP_SOLVER_COEFF_RANGE = [0.05,2.] 

"""
Used for navigating a Directed Implication Path (see class<PathTypeDI>), in 
the case of `open_info`. 

Stores on-contact node information about its activation threshold values, of type 
`linexp` XOR `single`. 

Every time memory structure is updated with activation threshold information from 
a node, it updates the known min. threshold values for all involved nodes. This 
knowledge allows navigator to expend less in allocating support for the minimum 
threshold node value requirements. 
"""
class DIPNMaxMinDB:  

    """
    nv_map := dict, node idn -> range [r_min,r_max) of possible values for assignment 
    """
    def __init__(self,nv_map:dict,prg):
        assert type(nv_map) == dict 
        assert type(prg) in {FunctionType,MethodType}

        self.nv_map = nv_map 
        self.prg = prg 

        # node -> ()
        self.nt_info = dict() 
        self.maxmin_node_values = dict() 
        self.untouched_nodes = [] 

        self.dipn_type = None 

    def __setitem__(self, node_idn, value):
        assert type(value) == tuple 
        assert len(value) == 2 
        assert type(value[0]) in {defaultdict,dict} 
        dtype = "single" if type(value[1]) == type(None) else "linexp" 
        if type(self.dipn_type) == type(None): 
            self.dipn_type = dtype 
        else: 
            assert self.dipn_type == dtype 

        self.nt_info[node_idn] = value 
        self.update_untouched_nodes(node_idn,value[0])
        self.maxmin_recal(node_idn) 

    def __getitem__(self, key):
        if key not in self.maxmin_node_values: return None 
        return self.maxmin_node_values[key]

    def maxmin_recal(self,node_idn): 
        v0,v1 = self.nt_info[node_idn] 

        # type: single 
        if type(v1) == type(None): 
            for k,v in v0.items(): 
                self.maxmin_node_value_assignment(k,v)
        # type: linexp 
        else: 
            keys = sorted(v0.keys()) 
            values = np.array([v0[k] for k in keys])
            index_ranges = np.array([self.nv_map[k] for k in keys])
            vs = Vector2FloatSolverTypeRX(values,index_ranges,v1,self.prg) 
            vs.solve()

            weights = vs.W
            for (node_idn,w) in zip(keys,weights): 
                self.maxmin_node_value_assignment(node_idn,w) 

    def maxmin_node_value_assignment(self,node_idn,value:float): 
        assert is_number(value) 
        value = ceil(value * 10 ** 5) / 10 ** 5
        value = round(value,5) 
        if node_idn not in self.maxmin_node_values: 
            self.maxmin_node_values[node_idn] = value 
            return 

        v2_ = max([self.maxmin_node_values[node_idn],value])
        
        self.maxmin_node_values[node_idn] = v2_ 

    """
    adds required nodes from n2v_map, besides from `node_idn`, to 
    `untouched_nodes` cache. 
    """
    def update_untouched_nodes(self,node_idn,n2v_map): 
        s = sorted(set(n2v_map.keys()) - {node_idn})  
        self.untouched_nodes.extend(s) 
        return

"""
Navigator for <PathTypeDI>. 
"""
class DIPathNavigator: 

    def __init__(self,G,node_value_range_map,prg,backtrack_pr=0.5,complete_backtrack_pr=0.):
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
        self.bt_pr = None 
        self.complete_bt_pr = None 
        self.complete_bt_mode = False  
        self.set_backtrack_pr(backtrack_pr,complete_backtrack_pr)
        self.loc = None

        # each element is (node,value)
        self.active_path = [] 

        self.node_to_expense_map = defaultdict(list) 
        self.total_expense = 0 

        self.fin_stat = False 
        self.dip_type = None 
        self.maxmin_db = DIPNMaxMinDB(self.nv_map,self.prg) 

        self.entire_path = [] 
        return

    def set_type_for_PathDI(self,t): 
        assert t in PATH_TYPE_DI_NODE_ACTIVATION_TYPES
        self.dip_type = t 

    def set_backtrack_pr(self,pr,cpr=0.):
        assert 0. <= pr <= 1. 
        assert 0. <= cpr <= 1. 
        self.bt_pr = pr
        self.complete_bt_pr = cpr 
        return

    def recv_node_info(self,node_idn,M,s): 
        self.maxmin_db[node_idn] = (M,s) 

    def max_current_node_support(self):
        d = dict() 
        for k,v in self.node_to_expense_map.items(): 
            if len(v) == 0: continue 
            
            q = self.maxmin_db[k]
            if type(q) == type(None): 
                q = float('inf')
            d[k] = min([max(v),q]) 
        return d 

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
            self.complete_bt_mode = False 
        else: 
            if self.complete_bt_mode: 
                x = self.default_backtrack() 
                return False,x 

            d = prg_decimal(self.prg,[0.,1.]) 

            # case: choose to backtrack 
            if d < self.bt_pr and len(self.active_path) > 0:
                
                d2 = prg_decimal(self.prg,[0.,1.]) 
                # set complete backtracking to True 
                if d2 < self.complete_bt_pr: 
                    self.complete_bt_mode = True 

                x = self.default_backtrack() 
                return False,x

            # case: move on 
            n = self.choose_next_node() 
        
        v = self.choose_support_value(n)
        self.node_to_expense_map[n].append(v) 
        self.node_to_expense_map[n] = self.node_to_expense_map[n][:DEFAULT_DIPNAV_LOG_LENGTH]
        self.total_expense += v 
        return True,(n,v)

    def update_loc(self,loc): 
        assert loc in self.G 
        self.loc = loc 

        if self.loc == self.tail: 
            self.fin_stat = True 

    def choose_next_node(self): 
        q = self.maxmin_db.untouched_nodes 
        
        neighbors = self.G[self.loc]
        neighbors_ = sorted(neighbors.intersection(set(q))) 

        if len(neighbors_) == 0: 
            neighbors_ = sorted(neighbors) 

        i = int(self.prg()) % len(neighbors_) 
        n = neighbors_[i] 
        return n 

    def choose_support_value(self,node_idn):
        # case: min threshold value available 
        #       through open info. mode. 
        x = self.maxmin_db[node_idn] 
        if type(x) != type(None): 
            return x 

        R = self.nv_map[node_idn]
        expense_seq = self.node_to_expense_map[node_idn] 
        if len(expense_seq) == 0: 
            R2 = R 
        else: 
            max_expense = max(expense_seq)#+ 10 ** -9 
            min_range = max([max_expense,R[0]]) 

            R2 = sorted([min_range,R[1]]) 

        v = modulo_in_range(self.prg(),R2) 
        return v 

    def default_backtrack(self): 
        assert len(self.active_path) > 0 
        x = self.active_path.pop(-1)
        if len(self.active_path) == 0: 
            self.loc = None 
        else: 
            self.loc = self.active_path[-1][0] 
            self.entire_path.append(self.loc) 
        return x 

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

    """
    backtracks from nodeset to the node of minimum index in active path 
    """
    def backtrack_from_nodeset(self,nodeset): 
        x = [a[0] for a in self.active_path] 
        indices = [x.index(n) for n in nodeset] 
        if len(indices) == 0: 
            return 

        index = min(indices)
        self.active_path = self.active_path[:index] 

    @staticmethod
    def from_PathTypeDI(ptdi:PathTypeDI,prg): 
        assert issubclass(type(ptdi),PathTypeDI) 
        assert type(prg) in {MethodType,FunctionType}
        return DIPathNavigator(ptdi.G,ptdi.nv_map,prg) 

"""
Processes <DIPathNavigator> decisions on a Path Type (D)irected (I)mplication.
"""
class DIPathNavigatorHandler: 

    def __init__(self,ptdi:PathTypeDI,dipn:DIPathNavigator,info_mode:int,verbose):  
        assert issubclass(type(ptdi),PathTypeDI) 
        assert type(dipn) == DIPathNavigator
        assert ptdi.nv_map == dipn.nv_map 

        self.ptdi = ptdi 
        self.dipn = dipn 
        self.dipn.set_type_for_PathDI(self.ptdi.act_type) 
        self.info_mode = info_mode 
        self.verbose = verbose 
        return 

    """
    return: (0|1,?,?,?)

    - CASE 0: have to backtrack due to pending failures activating 
        - set::(backtracked nodes)
        - current location [after backtracking]
        - True: immediate effect 
    - CASE 1: other
        - difference between score and min. threshold score 
        - bool: ?success status?
        - bool: ?immediate effect? 
    """
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

            # feed navigator on-contact threshold info for node, if `open_info`
            #if self.info_mode: 
            self.feed_info_to_navigator(node_idn) 

            does_advance,x2,stat1,stat2 = self.ptdi.register_advance(node_idn,value,self.verbose) 

            if self.verbose: 
                print("advancing? ",bool(does_advance))
                if does_advance: 
                    print("difference with threshold: {}".format(x2))
                    print("success: {}".format(stat1))
                    print("immediate effect: {}".format(stat2)) 
                else: 
                    print("backtracking nodes: {}".format(x2))
                    print("location after backtracking: {}".format(stat1))

            # 
            if does_advance: 
                
                # case: failure 
                if not stat1: 
                    # case: immediate failure, do not advance 
                    if stat2: 
                        return 
                    # case: pending failure, advance 
                    else: 
                        self.dipn.update_loc(node_idn)
                        self.dipn.active_path.append((node_idn,value)) 
                        self.dipn.entire_path.append(node_idn)

                        self.ptdi.navigator_path_record.append((node_idn,value))
                # case: success 
                else: 
                    self.dipn.active_path.append((node_idn,value))
                    self.dipn.update_loc(node_idn)
                    self.dipn.entire_path.append(node_idn)
                return 

            # backtrack 
            else:
                self.dipn.backtrack_from_nodeset(x2) 
                self.dipn.update_loc(stat1)
                self.dipn.entire_path.append(stat1) 
        else: 
            self.ptdi.register_backtrack()
        return 

    """
    used for info. mode #1. 
    """
    def feed_info_to_navigator(self,next_node): 

        M,s = self.ptdi.info_for_node(next_node) 
        
        if self.info_mode: 
            self.dipn.recv_node_info(next_node,M,s) 
        else: 
            self.dipn.maxmin_db.update_untouched_nodes(next_node,M)
        return