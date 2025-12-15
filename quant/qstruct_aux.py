
# auxiliary methods for <QStruct> 

from morebs2.search_space_iterator import * 

def update_mean(mean_value,new_value,new_frequency): 
    assert type(new_frequency) in {int,np.int32,np.int64} 
    assert new_frequency > 0 

    new_value = (mean_value * (new_frequency - 1)) + new_value 
    return new_value / frequency 

def is_valid_rnb_info_mode(info_mode):
    if not type(info_mode) in {list,tuple}: return False 
    if not (len(info_mode) == 4 and set(info_mode).issubset({0,1})): return False 
    return True 

def default_QStruct_query_cost(n,q): 
    return 1 

def info_on_query(expected_node_resistance,delta,querycost_func): 
    assert delta >= 0. 

    num_attempts = zero_div(expected_node_resistance,delta,float('inf'))
    query_cost = None 
    if not np.isinf(num_attempts): 
        num_attempts = ceil(num_attempts) 
        query_cost = 0 
        for _ in range(num_attempts): 
            query_cost += querycost_func(n,q) 
    else: 
        query_cost = float('inf')
    return num_attempts,query_cost 

def default_QStruct_F2FixCost_function(scalar:float = 1.0):

    def f(qstruct,node): 
        contra_row = qstruct.crate[node,:]
        contra_sum = np.sum(contra_row) 
        return contra_sum * scalar 
    return f 

#------------------------------------------------------------------------------------------------------

QSMOVE_CAT = {"initial scan","f1-fix node","f2-fix nodeset"}

class QSMove: 

    def __init__(self,category,additional_info): 
        self.ssi = None 
        self.f1_attempt_counter = 0 
        if category == "initial_scan": 
            assert type(additional_info) == tuple
            assert len(additional_info) == 2

            bounds = np.array([[0,additional_info[0]],\
                        [0,additional_info[1]]]) 
            start_point = bounds[:,0]
            column_order = [1,0] 
            ssi_hop = np.array(additional_info) 
            self.ssi = SearchSpaceIterator(bounds,start_point,column_order,ssi_hop,\
                cycleOn = False,cycleIs = 0)

        elif category == "f1-fix node":
            # (node index,question index,num attempts)
            assert type(additional info) == tuple 
            assert len(additional_info) == 3 
        else: 
            assert type(additional_info) == set 

        self.category = category
        self.additional_info = additional_info
        self.fin_stat = False 
        return

    def __next__(self):
        if self.fin_stat: return None 

        if self.category == "initial_scan":
            if self.ssi.reached_end(): 
                self.fin_stat = True 
                return None,None
            return self.category,next(self.ssi) 
        
        if self.category == "f1-fix node":
            if self.f1_attempt_counter >= self.additional_info[2]:
                self.fin_stat = True 
                return None,None 

            self.f1_attempt_counter += 1 
            return self.category,tuple(self.additional_info[:2]) 
        
        if len(self.additional_info) == 0: 
            self.fin_stat = True 
            return None,None 
        return self.category,self.additional_info.pop() 
             
class QSMoveLog: 

    def __init__(self):
        self.cache = []
        self.active_move = None    
        return 

    def load_QSMove(self,category,additional_info):
        qsm = QSMove(category,additional_info)
        self.active_move = qsm 

    def run_active_move(self):
        if type(self.active_move) == type(None): return None,None  

        cat,info = next(self.active_move)
        if type(cat) == type(None):
            self.cache.append(self.active_move)
            self.active_move = None  
            return None,None 
        return cat,info

    

#------------------------------------------------------------------------------------------------------
