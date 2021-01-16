"""
GROUP: LIMPENS (9)
DATE: 8 January 2021
AUTHOR(S): Karlijn Limpens
           Joos Akkerman
           Guido Vaessen
           Stijn van den Berg
           David Puroja 

DESCRIPTION: Based on the research in Northern Yellowstone where Wolves where 
set out to predate Elks to stabilize the population and to increase the 
proportion of healthy 
"""
import logging

from mesa import Model
from mesa.space import ContinuousSpace, MultiGrid
from mesa.datacollection import DataCollector

from .schedule import RandomActivationByBreed
from .agents import Wolf, Elk, GrassPatch

class ElkWolf(Model):
    """
    Wolf-Elk Predation model
    """
    def __init__(self):
        """
        Create a Elk-Wolf model with initial parameters.

        Args:
            initial_elks: The number of elks at the start of the model
            initial_wolves: The number of wolves at the start of the model

        """
        logging.debug("Initializing model.")
        super().__init__()
        # Grid parameters
        self.height = 20
        self.width = 20
        self.running = True
        # Initial parameters
        self.initial_health_distribution = 0
        self.field_regrowth_time = 30

        # Wolves parameters
        self.initial_wolves = 50
        self.wolves_reproduction_rate = 0.05
        self.wolves_max_energy = 40
        self.wolf_food_gain = 20
        self.wolf_step_radius = 10
        self.wolf_vision_radius = 15

        # Elk parameters
        self.initial_elks = 100
        self.elk_food_gain = 20
        self.elks_reproduction_rate = 0.04
        self.elk_step_radius = 4

        self.schedule = RandomActivationByBreed(self)

        # Initialize the continuous space field where the agents will be placed.
        self.grid = ContinuousSpace(
            x_max = self.width, 
            y_max = self.height, 
            torus = True
        )
        self.grassgrid = MultiGrid(self.height, self.width, torus=True)
        self.grass = True

        if self.grass:
            for _, x, y in self.grassgrid.coord_iter():

                fully_grown = self.random.choice([True, False])

                if fully_grown:
                    countdown = self.field_regrowth_time
                else:
                    countdown = self.random.randrange(self.field_regrowth_time)

                patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        for _ in range(self.initial_elks):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.elk_food_gain)
            age = self.random.randrange(0, 20)
            sheep = Elk(self.next_id(), (x, y), self, energy, age)
            self.grid.place_agent(sheep, (x, y))
            self.schedule.add(sheep)

        for _ in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.wolf_food_gain)
            wolf = Wolf(self.next_id(), (x, y), self, energy)
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)

    def new_agent(self, agent_type, position):
        new_agent = agent_type(self.next_id(), position, self, )
        self.grid.place_agent(new_agent, new_agent.pos)
        self.schedule.add(new_agent)


    def remove_agent(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def step(self):
        """
        Calls the step methods for each of the agents.
        """
        self.schedule.step_breed(Elk)
        self.schedule.step_breed(Wolf)
        self.schedule.step_breed(GrassPatch)

    def run(self, step_count=300):
        """
        Runs the model.
        Args:
            step_count (int): The amount of steps the model must run.
        """
        for _ in range (step_count):
            self.step()
