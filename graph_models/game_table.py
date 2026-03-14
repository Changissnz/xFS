from .action_table import * 

"""
table for immediate + long-term effects of actions by agents. 
Three <MultiAgentActionTable> instances.
[0] immediate value 
[1] cumulative value 
[2] duration (number of timestamps) for cumulative value to be met 
"""
class FullMultiAgentActionTable(MultiAgentActionTable):

    def __init__(self,agents,agent_action_imap,agent_action_cmap,agent_action_dmap):
        super().__init__(agents,agent_action_imap)

        assert set(self.agent_action_map.keys()) == set(agent_action_cmap.keys()) 
        assert set(self.agent_action_map.keys()) == set(agent_action_dmap.keys()) 

        mt1 = MultiAgentActionTable(agents,agent_action_cmap) 
        mt2 = MultiAgentActionTable(agents,agent_action_dmap) 
        assert mt1.agent2move_map == self.agent2move_map == mt2.agent2move_map

        self.agent_action_cmap = agent_action_cmap
        self.agent_action_dmap = agent_action_dmap
