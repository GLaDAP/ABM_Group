"""
Wolf-elk Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf elk Predation model.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import logging

from .agents import Elk, Wolf, GrassPatch
from .schedule import RandomActivationByBreed


class WolfElk(Model):
    """
    Wolf-elk Predation Model
    """
    height = 20
    width = 20

    initial_elk = 100
    initial_wolves = 50

    elk_reproduce = 0.04
    wolf_reproduce = 0.05

    wolf_gain_from_food = 20

    grass = False
    grass_regrowth_time = 30
    elk_gain_from_food = 4

    description = (
        "A model for simulating wolf and elk (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        height = 20,
        width = 20,
        initial_elk = 100,
        initial_wolves = 50,
        elk_reproduce = 0.39,
        wolf_reproduce = 0.05,
        wolf_gain_from_food = 20,
        grass = False,
        grass_regrowth_time = 30,
        elk_gain_from_food = 4,
    ):
        """
        Create a new Wolf-elk model with the given parameters.

        Args:
            initial_elk: Number of elk to start with
            initial_wolves: Number of wolves to start with
            elk_reproduce: Probability of each elk reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a elk
            grass: Whether to have the elk eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            elk_gain_from_food: Energy elk gain from grass, if enabled.
        """
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_elk = initial_elk
        self.initial_wolves = initial_wolves
        self.elk_reproduce = elk_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time
        self.elk_gain_from_food = elk_gain_from_food

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {
                "Wolves": lambda m: m.schedule.get_breed_count(Wolf),
                "Elks": lambda m: m.schedule.get_breed_count(Elk),
                "Elks age": lambda m: m.schedule.get_average_age(Elk),
                "Killed Elks/Wolf" : lambda m: m.schedule.get_average_kills(Wolf)
            }
        )

        # Create elk:
        for _ in range(self.initial_elk):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            age = self.random.randrange(0, 20)
            energy = self.random.randrange(2 * self.elk_gain_from_food)
            elk = Elk(self.next_id(), (x, y), self, True, age, energy)
            self.grid.place_agent(elk, (x, y))
            self.schedule.add(elk)

        # Create wolves
        for _ in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.next_id(), (x, y), self, True, energy)
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)

        # Create grass patches
        if self.grass:
            for _, x, y in self.grid.coord_iter():

                fully_grown = self.random.choice([True, False])

                if fully_grown:
                    countdown = self.grass_regrowth_time
                else:
                    countdown = self.random.randrange(self.grass_regrowth_time)

                patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        logging.debug(
            [
                self.schedule.time,
                self.schedule.get_breed_count(Wolf),
                self.schedule.get_breed_count(Elk),
            ]
        )

    def run_model(self, step_count=200):
        logging.debug("Initial number wolves: %s", self.schedule.get_breed_count(Wolf))
        logging.debug("Initial number elk: %s", self.schedule.get_breed_count(Elk))

        for _ in range(step_count):
            self.step()

        logging.debug("Final number wolves: %s", self.schedule.get_breed_count(Wolf))
        logging.debug("Final number elk: %s", self.schedule.get_breed_count(Elk))
