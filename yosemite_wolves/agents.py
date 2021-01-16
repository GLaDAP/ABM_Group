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
import random
import heapq

from mesa import Agent
from yosemite_wolves.walker import Walker

class Elk(Walker):
    """
    Elk Agent Class, simulating Elks which moves in a given space, reproduces,
    has health and is predated by wolves.
    """
    malnutrition_limit = 10

    def __init__(
        self, 
        unique_id, 
        position, 
        model, 
        init_energy,
        age
    ):
        super().__init__(unique_id, position, model)
        self.age = age
        self.energy = init_energy # Scale between 0 and 100

    def step(self):
        self.move_random(self.model.elk_step_radius)
        self.eat()
        self.death()
        self.reproduce()

    def eat(self):
        if self.model.grass:
            # Reduce energy
            self.energy -= 1
            # If there is grass available, eat it
            print(self.model.grassgrid.out_of_bounds(self.pos))
            this_cell = self.model.grassgrid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)]
            print(grass_patch)
            if grass_patch.fully_grown:
                self.energy += self.model.elk_food_gain
                grass_patch.fully_grown = False

    def reproduce(self):
        """
        """
        chance = random.random()
        if (chance > self.model.elks_reproduction_chance):
            self.model.new_agent(Elk, self.pos)

    def death(self):
        """
        Death NOT by a Wolf can occur in the following events:
        - malnutrition
        - age

        First, determine parameters and then, check probability when an Elk 
        dies.
        """
        if self.model.grass:
            if self.energy < 0:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)

        death_probability = self.get_death_probability_by_age(self.age)
        if (death_probability > random.random()):
            self.model.remove_agent(self)

    def get_death_probability_by_age(self, age):
        return random.random()


class Wolf(Walker):
    """
    Wolf Agent Class, simulating Wolves which moves in a given space, 
    reproduces, kills elks and has an age.
    """
    def __init__(
        self,
        unique_id,
        position,
        model,
        energy_init
    ):
        super().__init__(unique_id, position, model)
        self.energy = energy_init
    # def filter_non_hungry_wolves(self, list_of_agents):
    #     hungry_agents = 

    def step(self):
        """
        Step function.
        Order in step function:
        #1: Determine if wolf attacks Elk
        #2a: If yes, then check with agents in close proximity
        #2b: If no, finish phase
        #3: Move the agent
        #4: Use energy
        #4: Reproduction (costs energy)
        #5: Death Chance
        """
        self.move_random(self.model.wolf_step_radius)
        self.eat()
        self.death()
        self.reproduce()

    def eat(self):
        elks = self.get_neighbouring_agents()
        if (elks):
            elk_to_eat = self.random.choice(elks)
            self.energy += self.model.wolf_gain_from_food
            self.model.grid._remove_agent(elk_to_eat)
            self.model.schedule.remove(elk_to_eat)

    def reproduce(self):
        """
        Reproduce a Wolf asexually by probability.
        """
        reproduction_chance = random.random()
        if (reproduction_chance > self.model.wolves_reproduction_rate):
            self.model.new_agent(Wolf, self.pos)
            self.energy /= 2

    def death(self):
        """
        Removes by probability a Wolf from the model.
        """
        if (self.energy < 0):
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

        death_chance = random.random()
        if (death_chance > self.model.wolves_reproduction_rate):
            self.model.remove_agent(self)
            self.model.schedule.remove(self)

    def get_neighbouring_agents(self):
        """
        """
        neighbours = self.model.grid._get_neighbors(self.pos, self.model.wolf_vision_radius)
        agents = [agent for agent in neighbours if isinstance(self, Elk)]
        if (agents):
            heap = []
            [heapq.heappush(heap,(self.model.grid.get_distance(agent.pos, self.pos), agent)) for agent in agents]
            return [heapq.heappop(heap) for i in range(5)]
        else:
            return []


class GrassPatch(Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """
    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
