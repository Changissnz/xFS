Folder contains code that casts over data structures from the folder `quant`. This final 
code cast over that code produces these bots, graph problems to be solved. The file 
`sim_solution_search.py` contains code to run sequences of PRNGs over the same bot, 
in order to check for the best solution (PRNG) out of those candidates. 

The bots are subclasses of existing classes in folder `quant`, mostly without any 
additional extension, only the changing of the name of that data structure superclass to 
the bot's name. Additionally, a lot of the code is duplicate, especially in the `_*.py` 
files, since every bot is dedicated its own scaffolding code to be used for 
`sim_solution_search.py`.
