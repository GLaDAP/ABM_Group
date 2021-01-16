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
    def __init__(self, unique_id, position, model):
        """
        Args:
            unique_id: Unique ID from the agent.
            position:  Location of the agent.
            model:     Reference to model.
        """
        super().__init__(unique_id, model)
        self.pos = position

    def __get_neighbors(self, position, radius):
        """
        Gets the neighbors within a certain radius. The radius should be related
        to real factors like vision.
        Args:
            position (tuple): Position of the agent in the space.
            radius   (float): The vision radius of the agent.
        """
        return self.model.grid._get_neighbors(position, radius)

    def __get_new_position_in_direction(self, agent_to_follow, movement_per_step):
        """
        Moves the agent in the direction of the agent to follow
        Args:
            agent_to_follow (Agent): Agent-object to follow.
        """
        # get direction angle to the agent
        distance = self.model.grid.get_distance(agent_to_follow.pos, self.pos)
        if (distance > movement_per_step):
            heading_vector = np.array(self.model.grid.get_heading(agent_to_follow.pos, self.pos))
            normalized_heading = heading_vector / np.linalg.norm(heading_vector)
            return self.model.grid.torus_adj(self.pos + normalized_heading * movement_per_step)
        else:
            return agent_to_follow.pos
        return 

    def move_to_own_kind(self, filter_func : callable = None):
        """
        Move one step in possible direction with agent of same kind.
        Moves to closest.
        Args:
            filter_func (callable)(optional): Function to filter agent based on 
            conditions. Should return a list of agents.
        """
        self.move_to_specific_kind(type(self), filter_func)

    def move_to_specific_kind(self, type_attractor : Agent, vision_radius : float, filter_func : callable = None):
        """
        Move one step in possible direction of a specific kind.
        If there are agents available, then move towards it, otherwise move 
        random to avoid locking on an agent.
        Args:
            type_attractor (Agent): The type to which the agent has to move.
            filter_func (callable)(Optional): 
        """
        neighbors = self.__get_neighbors(self.pos, vision_radius)
        agent_of_type = [agent for agent in neighbors if isinstance(agent, type_attractor)]
        if (filter_func):
            agent_of_type = filter_func(agent_of_type)
        if agent_of_type:
            # TODO: Conditional to check how many are there at a certain point?
            # Move to one of the agents. 
            agent_to_follow = self.__get_closest_agent(agent_of_type) 
            self.model.grid.move_agent(self, agent_to_follow.pos)
        else:
            agent_to_follow = random.choice(agent_of_type)
            self.model.grid.move_agent(self, agent_to_follow.pos)

    def move_random(self, movement_per_step):
        """
        Moves random at given step size.
        """
        # First, get the movement radius
        x_step = random.uniform(0, movement_per_step)
        y_step = random.uniform(0, movement_per_step)
        x, y = self.pos
        # Then, set the coordinate within the radius
        return self.model.grid.torus_adj((x + x_step, y + y_step))


    def __get_closest_agent(self, agents):
        """
        Determine from list of agents which is the closest one and return the
        agent.
        Args:
            agents [Agent]: The list of agents.
        """
        heap = []
        [heapq.heappush(heap,(self.model.grid.get_distance(agent.pos, self.pos), agent)) for agent in agents]
        return heapq.heappop(heap)