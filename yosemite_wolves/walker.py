"""
GROUP: LIMPENS (9)
DATE: 8 January 2021
AUTHOR(S): Karlijn Limpens
           Joos Akkerman
           Guido Vaessen
           Stijn van den Berg
           David Puroja 
"""

from mesa import Agent
import random
import heapq
import numpy as np

class Walker(Agent):
    """
    Class containing definitions to move an agent on the grid. This class is 
    inherited by the agent using this walk-definition.
    """

    def __init__(self, unique_id, position, model, radius, step_distance):
        """
        Args:
            unique_id: Unique ID from the agent
            position: Location of the agent
            model: Reference to model
        """
        super().__init__(unique_id, model)
        self.pos = position
        self.radius = radius
        self.movement_per_step = step_distance

    def __get_neighbors(self, position, radius):
        """
        Gets the neighbors within a certain radius. The radius should be related
        to real factors like vision.
        """
        return self.model.grid._get_neighbors(position, radius)

    def __get_new_position_in_direction(self, agent_to_follow):
        """
        Moves the agent to the 
        """
        # get direction angle to the agent
        distance = self.model.grid.get_distance(agent_to_follow.pos, self.pos)
        if (distance > self.movement_per_step):
            heading_vector = np.array(self.model.grid.get_heading(agent_to_follow.pos, self.pos))
            normalized_heading = heading_vector / np.linalg.norm(heading_vector)
            return self.model.grid.torus_adj(self.pos + normalized_heading * self.movement_per_step)
        else:
            return agent_to_follow.pos
        return 

    def move_to_own_kind(self):
        """
        Move one step in possible direction with agent of same kind.
        Moves to closest.
        """
        self.move_to_specific_kind(type(self))

    def move_to_specific_kind(self, type_attractor):
        """
        Move one step in possible direction of a specific kind.
        If there are agents available, then move towards it, otherwise move 
        random 
        """
        neighbors = self.__get_neighbors(self.pos, self.radius)
        agent_of_type = [agent for agent in neighbors if isinstance(agent, type_attractor)]
        if agent_of_type:
            # TODO: Conditional to check how many are there at a certain point?
            # Move to one of the agents. 
            # For now, we move the agent to a random one. This can be changed to
            # the closest one by checking the distances. However, when the model
            # increases, 
            agent_to_follow = self.__move_to_closest_agent(agent_of_type) 
            self.model.grid.move_agent(self, agent_to_follow.pos)
        else:
            agent_to_follow = random.choice(agent_of_type)
            self.model.grid.move_agent(self, agent_to_follow.pos)

    def move_random(self):
        """
        Moves random at given step size
        """
        # First, get the movement radius
        x_step = random.uniform(0, self.movement_per_step)
        y_step = random.uniform(0, self.movement_per_step)
        x, y = self.pos
        # Then, set the coordinate within the radius
        return self.model.grid.torus_adj(x + x_step, y + y_step)


    def __move_to_closest_agent(self, agents):
        """
        Determine from list of agents which is the closest one and return the
        agent.
        """
        heap = []
        [heapq.heappush(heap,(self.model.grid.get_distance(agent.pos, self.pos), agent)) for agent in agents]
        return heapq.heappop(heap)