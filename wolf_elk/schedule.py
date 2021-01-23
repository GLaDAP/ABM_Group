"""
GROUP:      LIMPENS (9)
DATE:       18 January 2021
AUTHOR(S):  Karlijn Limpens
            Joos Akkerman
            Guido Vaessen
            Stijn van den Berg
            David Puroja 
DESCRIPTION:The scheduler which supports random activation and random
            activation by breed. This code is partially from Mesa Examples:
            https://github.com/projectmesa/mesa/tree/master/examples/wolf_sheep
            with the addition of helper functions to get statistics of the
            agents.
"""
from collections import defaultdict
import logging

from mesa.time import RandomActivation


class RandomActivationByBreed(RandomActivation):
    """
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    Assumes that all agents have a step() method.
    """

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_breed = defaultdict(dict)

    def add(self, agent):
        """
        Add an Agent object to the schedule
        Args:
            agent: An Agent to be added to the schedule.
        """
        self._agents[agent.unique_id] = agent
        agent_class = type(agent)
        self.agents_by_breed[agent_class][agent.unique_id] = agent

    def remove(self, agent):
        """
        Remove all instances of a given agent from the schedule.
        Args:
            agent (Agent): The agent to remove from the scheduler.
        """
        del self._agents[agent.unique_id]

        agent_class = type(agent)
        del self.agents_by_breed[agent_class][agent.unique_id]

    def step(self, by_breed=False):
        """
        Executes the step of each agent breed, one at a time, in random order.

        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        """
        if by_breed:
            for agent_class in list(self.agents_by_breed):
                self.step_breed(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_breed(self, breed):
        """
        Shuffle order and run all agents of a given breed.

        Args:
            breed (class): The class inherited from Agent.
        """
        agent_keys = list(self.agents_by_breed[breed].keys())
        self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            logging.debug("Step breed function with breed {}".format(breed))
            self.agents_by_breed[breed][agent_key].step()

    def get_breed_count(self, breed_class):
        """
        Returns the current number of agents of certain breed in the queue.
        Args:
            breed_class (class): The class inherited from Agent.
        Returns:
            Count of specified breed.
        """
        return len(self.agents_by_breed[breed_class].values())

    def get_breed_list(self, breed_class):
        """
        Returns a list with all the Agent from the specified breed.
        Args:
            breed_class (class): The class inherited from Agent.
        Returns: 
            A list with all the Agent from specified Breed.
        """
        return self.agents_by_breed[breed_class].values()

    def get_average_age(self, breed_class):
        """
        Returns the average age of all the agents of a certain breed in the
        queue.
        Args:
            breed_class (class): The class inherited from Agent.
        """
        agents = self.agents_by_breed[breed_class]
        if agents:
            age_list = [agent.age for agent in agents.values()]
            return sum(age_list) / len(agents)
        else:
            return 0

    def get_average_kills(self, breed_class):
        """
        Returns the average kills of all the agents of a certain breed in the
        queue.
        Args:
            breed_class (class): The class inherited from Agent. This Agent 
                                 should contain a 'kills' property.
        Returns:
            Average kills per agent.
        """
        agents = self.agents_by_breed[breed_class]
        if agents:
            age_list = [agent.kills for agent in agents.values()]
            return sum(age_list) / len(agents)
        else:
            return 0
