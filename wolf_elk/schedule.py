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
from collections import defaultdict
import logging

from mesa.time import RandomActivation


class RandomActivationByBreed(RandomActivation):
    """
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.

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
        """

        del self._agents[agent.unique_id]

        agent_class = type(agent)
        del self.agents_by_breed[agent_class][agent.unique_id]

    def step(self, by_breed=True):
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
            breed: Class object of the breed to run.
        """
        agent_keys = list(self.agents_by_breed[breed].keys())
        self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            logging.debug("Step breed function with breed {}".format(breed))
            self.agents_by_breed[breed][agent_key].step()

    def get_breed_count(self, breed_class):
        """
        Returns the current number of agents of certain breed in the queue.
        """
        return len(self.agents_by_breed[breed_class].values())

    def get_average_age(self, breed_class):
        """
        Returns the average age of all the agents of a certain breed in the
        queue.
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
        """
        agents = self.agents_by_breed[breed_class]
        if agents:
            age_list = [agent.kills for agent in agents.values()]
            return sum(age_list) / len(agents)
        else:
            return 0