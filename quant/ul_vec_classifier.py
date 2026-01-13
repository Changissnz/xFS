from morebs2.ball_comp import * 

class VecClassifierTypeBC: 

    def __init__(self,max_balls,max_radius):  
        self.max_balls = max_balls 
        self.max_radius = max_radius 

    def start_BallComp_classifier(self): 
        vh1 = ViolationHandler1(self.max_balls,self.max_radius) 
        self.bc = BallComp(self.max_balls,self.max_radius,vh1,verbose=0) 
        return 
    
    def input(self,p): 
        # case: declare a new classifier 
        if self.bc.terminatedDelta: 
            self.start_BallComp_classifier() 
        self.bc.conduct_decision(p) 
        return 

    def classify(self,p): 
        return self.bc.ball_label_for_point(p) 