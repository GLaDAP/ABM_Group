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


from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from collections import defaultdict
import logging
import uuid

import numpy as np
import pandas as pd

from .agents import Elk, GrassPatch
from .wolf import Wolf, Pack
from .schedule import RandomActivationByBreed


class WolfElk(Model):
    """
    Wolf-elk Predation Model
    """
    description = (
        "A model for simulating wolf and elk (predator-prey) \
         ecosystem modelling."
    )

    def __init__(
        self,
        height=40,
        width=40,
        initial_elk=100,
        initial_wolves=50,
        elk_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass_regrowth_time=30,
        elk_gain_from_food=4,
        energy_threshold=10,
        pack_size_threshold=4,
        wolf_territorium=4,
        polynomial_degree=10
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
        self.grass_regrowth_time = grass_regrowth_time
        self.elk_gain_from_food = elk_gain_from_food
        self.energy_threshold = energy_threshold
        self.pack_size_threshold = pack_size_threshold
        self.wolf_territorium = wolf_territorium

        self.polynomial_degree = polynomial_degree
        self.elk_reproduction_params = self.fit_elk_reproduction_chance()
        self.elk_wolfkill_params = self.fit_elk_wolfkill_by_age()

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {
                "Wolves": lambda m: m.get_wolf_breed_count(),
                "Elks": lambda m: m.schedule.get_breed_count(Elk),
                "Elks age": lambda m: m.schedule.get_average_age(Elk),
                "Killed Elks/Wolf": lambda m:
                    m.schedule.get_average_kills(Wolf),
                "Packs": lambda m: m.schedule.get_breed_count(Pack)
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
        for _, x, y in self.grid.coord_iter():
            fully_grown = self.random.choice([True, False])

            if fully_grown:
                countdown = self.grass_regrowth_time
            else:
                countdown = self.random.randrange(self.grass_regrowth_time)

            patch = GrassPatch(
                self.next_id(),
                (x, y),
                self,
                fully_grown,
                countdown
            )
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

        self.running = True
        self.datacollector.collect(self)

    def get_wolf_breed_count(self):
        wolves = self.schedule.get_breed_count(Wolf)
        wolves += sum([len(pack) for pack in self.schedule.get_breed_list(Pack)])
        return wolves

    def fit_elk_reproduction_chance(self):
        """
        Fits a polynomial to the elk reproduction data, used for interpolation
        """
        df = pd.read_csv('wolf_elk/empirical_data/elk_ratesbyage.csv', sep=',')
        all_ages = np.append([1],df['age'].values)
        all_preg_rate = np.append([0], df['preg_rate'])/26

        degree = self.polynomial_degree

        params = params = np.polyfit(all_ages, all_preg_rate, deg=degree)

        return params

    def fit_elk_wolfkill_by_age(self):
        """
        Fits a polynomial to the data of wolf-kills per elk age, used for interpolation
        """
        df = pd.read_csv('wolf_elk/empirical_data/elk_ratesbyage.csv', sep=',')
        all_ages = np.append([1],df['age'].values)
        all_perc_killed = np.append([50],(df['perc_of_killed'].values)/2)/100
        all_surv_rate = np.append([0.9],df['surv_rate'].values)

        degree = self.polynomial_degree
        P_kill_by_wolf = 1100/1350

        # Apply Bayes' Theorem
        P_kill_wolf_byage = np.array([((all_perc_killed[i]/all_surv_rate[i]*P_kill_by_wolf)/all_surv_rate[i]) for i,a in enumerate(all_ages)])

        # Fit polynomial
        params = np.polyfit(all_ages, P_kill_wolf_byage, deg=degree)

        return params

    def step(self):
        self.schedule.step(False)
        # collect data
        self.datacollector.collect(self)
        logging.debug(
            [
                self.schedule.time,
                self.schedule.get_breed_count(Wolf),
                self.schedule.get_breed_count(Elk),
                self.schedule.get_breed_count(Pack)
            ]
        )

    def run_model(self, step_count=200):
        logging.debug(
            "Initial number wolves: %s", self.schedule.get_breed_count(Wolf)
        )
        logging.debug(
            "Initial number elk: %s", self.schedule.get_breed_count(Elk)
        )

        for _ in range(step_count):
            self.step()

        logging.debug(
            "Final number wolves: %s", self.schedule.get_breed_count(Wolf)
        )
        logging.debug(
            "Final number elk: %s", self.schedule.get_breed_count(Elk)
        )
