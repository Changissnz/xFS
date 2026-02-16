from quant.mob_graph import * 

"""
Mob Killer Bot 

A simulation of a reactive system, with primary features of 'mass effect' and 'majority voting' 
processes. Since boolean space of non-definite dimension is infinite, the methodology of this bot 
were kept to a simplistic sequence of functions. The bot design is akin to a simulation of a 
coin toss with overhead. 

This 'coin toss' process goes as follows. 
There are two factions in competition with each other, an <AntiMobUnit> and n <MobAgent>s that 
make up the 'mob'. For every turn, the <AntiMobUnit> first transmits a vector, in the form of 
(boolean b, float f) to one <MobAgent> M, this one selected by the <AntiMobUnit> PRNG. 

Boolean b is the correct value for some unspecified attribute. 
<MobAgent> M receives (b,f) and accepts b if given its PRNG output, f_1, at that time, 
    ceil(f + f_1) % 2 == 1, 
otherwise, it accepts NOT b. 

For every <MobAgent> M_i after the first, <AntiMobUnit> uses its PRNG to route a boolean 
from exactly one <MobAgent> to another until all <MobAgents> have received a boolean. 
For the i'th <MobAgent> in this sequence, the boolean value b_(i-1) of the (i-1)'th <MobAgent> 
that is the acceptance or rejection of boolean b is fed to the i'th <MobAgent>. A threshold 
value is calculated as 

            i-1
    f_t =   SUM (M_j.weight)  /      MAX      SUM    (M_q.weight) ; {M_k} a subset in mob of size (i-1).  
            j=1                  {M_k} in mob  M_q in {M_k}

<MobAgent> M_i uses its PRNG to output a decimal f in [0.,1.]. If f <= f_t, then M_i 
accepts the boolean value b_(i-1) of M_(i-1) as value for b_i, otherwise b_i = NOT b_(i-1). 

After all the <MobAgent>s have received a boolean, a summation of 0's and of 1's proceeds. 
A majority vote b_vote is called. If b_vote equals b, the original boolean from <AntiMobUnit>, 
then <AntiMobUnit>'s score is deducted by 

           sum           (M.weight).  
    M in mob s.t. M.b == b  

Otherwise, the total deduction of <MobAgent>s' scores is 

        D_a  =  sum                (M.weight). 
           M in mob s.t. M.b == b_vote  

The deduction is either proportional XOR inversely proportional, according to the 0 XOR 1 PRNG 
output from <AntiMobUnit>, of the <MobAgent> weights. Given the cumulative sum of all mob weights W, 
the score of a <MobAgent> M is deducted by 
        (M.weight / W) * D_a   [proportional], 
        (1 - M.weight / W) * D_a   [inversely proportional]. 

----------------------------------------------------------------------------------------------------- 

Scores for either faction are non-increasing. Any agent with non-positive score is eliminated. Automaton 
is guaranteed to produce exactly one winning faction for any simulation. 
"""
class MKBot(MobNetwork): 

    def __init__(self,G,antimob:AntiMobUnit,mob_agent_map:dict,prg,mutable_weight_function,\
        verbose=False):
        super().__init__(G,antimob,mob_agent_map,prg,mutable_weight_function,\
            verbose=False)

    @staticmethod
    def generate_instance(num_agents,prg,antimob_score,mob_agent_uniform_score,\
        mob_agent_weight_range=[1,200],mutable_weight_function = lambda x: x + 0): 

        mn = MobNetwork(num_agents,prg,antimob_score,mob_agent_uniform_score,\
            mob_agent_weight_range,mutable_weight_function) 

        return MobKillerBot(mn.G,mn.antimob,mn.mob_agent_map,mn.prg,\
            mn.mutable_weight_function,mn.verbose)