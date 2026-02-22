from .strangle_form import * 

class StrangleEnv: 

    def __init__(self,strangler,strangle_subject,prg): 
        assert type(strangler) == StrangleForm
        assert type(strangle_subject) == StrangleSubject
        assert type(prg) in {MethodType,FunctionType} 

        self.strangler = strangler 
        self.strangle_subject = self.strangle_subject
        self.prg = prg 
