# xFS

This project is allocated for algorithms I have attempted in some of my past projects, 
as well as some emerging ideas of mine. 

The projects `puissec` and `r2apart`, in particular, are not fully functional and were 
developed by me only in conjunction with my research efforts. Technicalities in both 
hardware and those projects' code implementation have pressured me to cease their 
further development.

```
NOTE: Project has entered progressive mode on 3/3/2026. Further developments will not 
go according to previous rate of development. 
```

```
NOTE: no graphical user interface provided. 
``` 

## Graph Problems of Interest (in my words)

Here is a list of graph problems in the project: 
- Respondent Network Bot (Alpha) 
    - vantage point for learning: Q, the questioner. 
    - file: `graph_problems/rnb.py`
- Hidden Threat Exposure Bot (Alpha) 
    - vantage point for learning: navigator of network containing threats. 
    - file: `graph_problems/hte.py`
- Slander Net Bot (Alpha)  
    - vantage point for learning: agent that determines what communication 
      ports to open and close to maximize objective function score. 
    - code has non-deterministic elements to it. Required to set seeds for 
    Python and Numpy random. 
    - file: `graph_problems/snb.py`
- Poison Trace Bot (Alpha) 
    - vantage point for learning: agent (poison target), in a network, that 
    has to position alert relays to help it know (poison source, poison identity) 
    of poison delivered to it. Accurate knowledge allows for poison target to 
    negate poison before its termination. 
    - code has non-deterministic elements to it. Required to set seeds for 
    Python and Numpy random.
    - file: `graph_problems/ptb.py`  
- Bull Killer Bot (Alpha) 
    - vantage point for learning: Chaser agents that pursue the Bull along a 
    network. 
    - file: `graph_problems/bkb.py` 
- Homo Frame Bot (Alpha) 
    - vantage point for learning: n agents expected to act according to 
    homomorphic demands, set by administrator. 
    - file: `graph_problems/hfb.py` 
- Mob Killer Bot (Alpha) 
    - vantage point for learning: anti-mob unit acting against `n` Mob agents in 
    a reactive system. 
    - file: `graph_problems/mkb.py` 
- Strangle Bot (Alpha)  
    - vantage point for learning: strangling agent with objective to control all nodes 
    of graph G, the subject of strangling. 
    - file: `graph_problems/sb.py` 
- Controverter Bot (Alpha) 
    - vantage point for learning: an agent in a multi-agent cyclical game, structured as a 
    continually variable chain of decision junction points, each requiring all the 
    agents to make their moves. 
    - file: `graph_problems/cb.py` 
- Token-Swapping Bot (Alpha) 
    - vantage point for learning: an agent that has to solve the NP-Complete problem, Token Swapping, 
    for an arbitrary graph. 
    - file: `graph_problems/tsb.py` 
- Dual Role Bot (Pre-Alpha) 
- Middleman Bot (Pre-Alpha)

#### NOTE: 
Some of these bots rely on Python/Numpy random. User results may differ from 
developer results. As of this time in writing, developer Python version is 3.14.2. 

## The Machine-Learning Aspect 

The graph problems defined in this project involve software agents. These agents are 
programmed with functionalities that are static. This implies the agents cannot "learn" 
any more, past their programming, about the specific problems they act in. Their learning 
mechanisms cannot "expand" any more outside of this static programming: no additional 
variables of interest, no different data structure formats, no different ordering scheme 
of deciding on the best choice per timestamp, no different ranking mechanisms for choices. 
Instead, the only way to improve a solution is through a semi-blind search process that iterates 
through a candidate list of pseudo-random number generators (PRNGs) for the best PRNG. 
PRNGs are used in agent decision-making for these graph problems. PRNGs output numbers, 
and agents map these numbers out to decisions taken by them. The utility of obtaining a 
high-performing PRNG for a graph problem of specific starting parameters is restricted to 
that case. There is no software mechanism provided to automate deriving of further insight 
into any graph problem example via a high-performing PRNG. This deficit differs from 
traditional machine-learning problems on fixed and labeled datasets, where feedback loops 
of training iterations can be guaranteed to yield incrementally better solutions, until 
the global optimum is found. This guarantee, of course, is theoretical and cannot be stated for 
deep learning problems on highly variable datasets. It is possible to implement further 
code for these graph problems to be more conducive for machine-learning. However, 
implementing further code would defeat the purpose of graph problem difficulty. The 
division of partial information between agents in every one of these graph problems was 
deliberate in fulfillment of maintaining a baseline of probabilistic difficulty for an agent 
to improve its solution (PRNG). Unlike the highly vectorizable (input,output) samples 
of traditional machine-learning that typically operates in Euclidean space, finding a 
high-scoring solution does not easily lead to a better solution derived from that one. 
Users can refer to one high-scoring PRNG, and add tweaks to it at selected indices of 
the generator output. See below for illustration on PRNG G and tweaking it to G2: 
```
G:  x0,x1,x2,x3,x4,x5... 
G2: x0,x42,x2,x56,x4,x5,... 
```

But this is a cumbersome process, and there is no guarantee making tweaks to a high-performing 
generator would result in a better solution. 

## User Access to the Graybox 

The computer code for these bots in these graph problems is open for view. This is not a 
blackbox arrangement. Users, in their attempts to guess high-performing PRNGs for any 
graph problem example, can carefully review how the automata decision-making pipelines 
work. These pipelines follow a general form, and descriptions are provided for each of 
these graph problem bots. But these implementations rest on arbitrary design. 

In a blackbox system, users would not know what the graph problem is, let alone the general 
form of it. They would only be able to enter in a PRNG for the automaton to use for 
decision-making. They would not be able to ascertain the end results from the PRNG. In these 
graybox implementations, users would know the end results from the PRNG. But since a 
PRNG only outputs real numbers for decision-making, users would not be able to easily know 
what decisions the PRNG was responsible for. Thus, users would have a relatively difficult 
time knowing what decisions are sub-optimal. Users can analyze the code implementation to 
determine the specific decisions the PRNG mapped to, post-simulation. But code is not 
provided in this project to convenience that.  