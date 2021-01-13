"""
GROUP: LIMPENS (9)
DATE: 8 January 2021
AUTHOR(S): Karlijn Limpens
           Joos Akkerman
           Guido Vaessen
           Stijn van den Berg
           David Puroja 

DESCRIPTION: In this file, the agents are defined used in the model.
             There are two types of agents: an agent of the Wolf class and an
             agent of the Elk class. 
"""

from mesa import Agent
from yosemite_wolves.walker import Walker

class Elk(Walker):
    """
    Elk Agent Class, simulating Elks which moves in a given space, reproduces,
    has health and is predated by wolves.
    """
    def __init__(
        self, 
        unique_id, 
        position, 
        model, 
        health,
        vision_radius,
        step_distance,
        age
    ):
        super().__init__(unique_id, position, model, vision_radius, step_distance)
        self.age = age
        self.health = health
