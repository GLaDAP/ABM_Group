"""
GROUP: LIMPENS (9)
DATE: 18 January 2021
AUTHOR(S): Karlijn Limpens
           Joos Akkerman
           Guido Vaessen
           Stijn van den Berg
           David Puroja 
DESCRIPTION: 
"""
"""
Walker class, with functions to move to certain kind so packs can be created
in the ABM. Also, distance (steps to the point in the grid) can be measured to
check the closest one and move in that direction.
"""

from mesa import Agent
import heapq  # For efficient sorting of nearby agents
import random


class Walker(Agent):
    """
    Class with walker functions for all the agents.
    """

    def __init__(
        self,
        unique_id: int,
        pos: tuple,
        model: object,
        moore: bool = True
    ):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(
            self.pos,
            self.moore,
            True
        )
        next_move = self.random.choice(next_moves)
        self.model.grid.move_agent(self, next_move)

    def move_towards_own_kind(self, radius: int, filter_func: callable = None):
        """
        Moves agent toward the same kind.
        """
        return self.move_towards_specified_kind(
            type(self),
            radius,
            filter_func
        )

    def move_towards_specified_kind(
        self,
        agent_type: object,
        radius: int,
        filter_func: callable = None
    ):
        # Get neighborhood first:
        neighbours = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=False,
            radius=radius
        )
        # Get closest neighbors
        agent_of_type = [
            agent for agent in neighbours if isinstance(agent, agent_type)
        ]
        if (filter_func):
            agent_of_type = filter_func(agent_of_type)
        if agent_of_type:
            agent_to_follow = self.__get_closest_agents(agent_of_type)
            self.model.grid.move_agent(self, agent_to_follow[1].pos)
            return agent_to_follow[1]
        else:
            return None

    def __get_closest_agents(self, agent_list: list):
        heap = []
        [
            heapq.heappush(
                heap,
                (
                    (abs(self.pos[0] - agent.pos[0]),
                     abs(self.pos[1] - agent.pos[1])),
                    agent
                )
            ) for agent in agent_list
        ]
        return heapq.heappop(heap)
