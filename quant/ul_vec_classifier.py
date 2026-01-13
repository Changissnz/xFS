from morebs2.ball_comp import * 

class VecClassifierTypeBC: 

    def __init__(self,max_balls,max_radius):  
        self.max_balls = max_balls 
        self.max_radius = max_radius 
        self.start_BallComp_classifier() 

    def start_BallComp_classifier(self): 
        vh1 = ViolationHandler1(self.max_balls,self.max_radius) 
        self.bc = BallComp(self.max_balls,self.max_radius,vh1,verbose=0) 
        return 
    
    def input(self,p): 
        # case: declare a new classifier 
        if self.bc.terminateDelta: 
            self.start_BallComp_classifier() 
        self.bc.conduct_decision(p) 
        return 

    def classify(self,p): 
        return self.bc.ball_label_for_point(p) 

    def contra_classify(self,p,variance): 
        # get the closest class to variance on class of p 
        S = set(self.bc.balls.keys()) 
        min_key,max_key = min(S),max(S) 
        diff = round((max_key - min_key) * variance,0)

        C = self.classify(p)
        t0,t1 = C + diff, C - diff 
        
        closest_key = None 
        min_diff = float('inf') 
        for s in S: 
            d0 = abs(s - t0) 
            d1 = abs(s - t1) 

            if d0 < min_diff: 
                closest_key = s 
                min_diff = d0 

            if d1 < min_diff: 
                closest_key = s 
                min_diff = d1  

        return closest_key 