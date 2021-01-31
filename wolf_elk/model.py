"""
GROUP:       LIMPENS (9)
DATE:        18 January 2021
AUTHOR(S):   Karlijn Limpens
             Joos Akkerman
             Guido Vaessen
             Stijn van den Berg
             David Puroja
DESCRIPTION: Class containing the definitions to run the model. This file
             contains the default values to run the model, the setup of the
             fitting functions for the elk reproduction rate and the
             probability of wolves killing elk.

            A small part of the code (Agent initialization) is from Mesa
            Examples:
            https://github.com/projectmesa/mesa/tree/master/examples/wolf_sheep
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import logging
import numpy as np
import pandas as pd

from .agents import Elk, GrassPatch
from .wolf import Wolf, Pack
from .schedule import RandomActivationByBreed
import os
print(os.getcwd())


class WolfElk(Model):
    """
    Wolf-elk Predation Model
    """
    description = (
        "A model for simulating wolf and elk (predator-prey) \
         ecosystem modelling with pack-behaviour and real world fitted data."
    )

    def __init__(
        self,
        height=40,
        width=40,
        initial_elk=200,
        initial_wolves=20,
        wolf_reproduce=0.03,
        wolf_gain_from_food=30,
        grass_regrowth_time=30,
        elk_gain_from_food=6,
        energy_threshold=10,
        pack_size_threshold=2,
        wolf_territorium=8,
        polynomial_degree=10,
        wolf_lone_attack_prob=0.2,
        time_per_step=1/26
    ):
        """
        Create a new Wolf-elk model with the given parameters.

        Args:
            height:              Height of the grid
            width:               Width of the grid
            initial_elk:         Number of elk to start with
            initial_wolves:      Number of wolves to start with
            wolf_reproduce:      Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a elk
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            elk_gain_from_food:  Energy elk gain from grass, if enabled
            energy_threshold:    The threshold when wolves are going to look
                                 for elk to eat
            pack_size_threshold: The minimum size for a pack to attack an elk
            wolf_territorium:    The radius of the wolf to search for a pack
                                 to join and elk to eat
            polynomial_degree:   The degree of the polynomial where the real
                                 world data is fitted
            wolf_lone_attack_prob: The probability a wolf can eat an elk when
                                 attacking the elk alone.
            time_per_step:       The real time duration simulated in each
                                 time step
        """
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_elk = initial_elk
        self.initial_wolves = initial_wolves
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass_regrowth_time = grass_regrowth_time
        self.elk_gain_from_food = elk_gain_from_food
        self.energy_threshold = energy_threshold
        self.pack_size_threshold = pack_size_threshold
        self.wolf_territorium = wolf_territorium
        self.wolf_lone_attack_prob = wolf_lone_attack_prob
        self.polynomial_degree = polynomial_degree
        self.elk_age_distribution = self.fit_elk_age_distr()
        self.elk_reproduction_params = self.fit_elk_reproduction_chance()
        self.elk_wolfkill_params = self.fit_elk_wolfkill_by_age()
        self.time_per_step = time_per_step

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
            age = np.random.choice(
                np.arange(1,20.01,1/26),p=self.elk_age_distribution)
            energy = self.random.uniform(
                self.elk_gain_from_food, 2 * self.elk_gain_from_food)
            elk = Elk(self.next_id(), (x, y), self, True, age, energy)
            self.grid.place_agent(elk, (x, y))
            self.schedule.add(elk)

        # Create wolves
        for _ in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.uniform(
                self.energy_threshold, 2 * self.energy_threshold)
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
        """
        Helper function to count the total wolves in the model, combining
        wolves who are in Packs and lone wolves.
        """
        wolves = self.schedule.get_breed_count(Wolf)
        wolves += sum([
            len(pack) for pack in self.schedule.get_breed_list(Pack)
        ])
        return wolves

    def fit_elk_reproduction_chance(self):
        """
        Fits a polynomial to the elk reproduction data, used for interpolation
        Returns:
            Coefficients for polynomial.
        """
        df = pd.read_csv('empirical_data/elk_ratesbyage.csv', sep=',')
        all_ages = np.append([1],df['age'].values)
        all_preg_rate = np.append([0], df['preg_rate'])/26

        degree = self.polynomial_degree

        params = params = np.polyfit(all_ages, all_preg_rate, deg=degree)

        return params

    def fit_elk_age_distr(self):
        """
        Fits a polynomial to the survival rate per elk age, used for
        interpolation.
        Returns:
            Probability distribution of elk ages
        """
        df = pd.read_csv('empirical_data/elk_ratesbyage.csv', sep=',')
        all_ages = np.append([1],df['age'].values)
        all_surv_rate = np.append([0.9],df['surv_rate'].values)

        # Compute share of population by age
        all_surv_rate = all_surv_rate/sum(all_surv_rate)

        degree = self.polynomial_degree

        # Fit polynomial
        params = np.polyfit(all_ages, all_surv_rate, deg=degree)

        # Compute chances
        chances = np.array([
            sum([
                params[i]*age**(degree-i) for i in range(degree+1)
            ]) for age in np.arange(1,20.01,1/26)
        ])
        chances = chances/sum(chances)

        return chances

    def fit_elk_wolfkill_by_age(self):
        """
        Fits a polynomial to the data of wolf-kills per elk age, used for 
        interpolation.
        Returns:
            Coefficients for polynomial.
        """
        df = pd.read_csv('empirical_data/elk_ratesbyage.csv', sep=',')
        all_ages = np.append([1],df['age'].values)
        all_perc_killed = np.append([50],(df['perc_of_killed'].values)/2)/100
        all_surv_rate = np.append([0.9],df['surv_rate'].values)

        degree = self.polynomial_degree
        P_kill_by_wolf = 1100/1350

        def bayes_func(i):
            return (
                (all_perc_killed[i] / all_surv_rate[i] * P_kill_by_wolf) \
                / all_surv_rate[i]
            )

        # Apply Bayes' Theorem
        P_kill_wolf_byage = np.array([
            bayes_func(i) for i, _ in enumerate(all_ages)
        ])

        # Fit polynomial
        params = np.polyfit(all_ages, P_kill_wolf_byage, deg=degree)
        return params

    def step(self):
        """
        Steps through the model.
        Returns
            Dictionary with the 
        """
        # Random activation by breed is set to False by default since the pack
        # agent creates trouble with the scheduler when enabled, throwing 
        # KeyErrors.
        self.schedule.step(False)
        # collect data
        self.datacollector.collect(self)

        logging.debug(
            [
                self.schedule.time,
                self.get_wolf_breed_count(),
                self.schedule.get_breed_count(Elk),
                self.schedule.get_breed_count(Pack),
                self.schedule.get_average_kills(Wolf),
                self.schedule.get_average_age(Elk)
            ]
        )

        return {
            "step":self.schedule.time,
            "wolf":self.get_wolf_breed_count(),
            "elk":  self.schedule.get_breed_count(Elk),
            "pack": self.schedule.get_breed_count(Pack),
            "average_kills":  self.schedule.get_average_kills(Wolf),
            "average_elk_age": self.schedule.get_average_age(Elk)
        }

    def run_model(self, step_count=200):
        """
        Runs the model.
        Args:
            step_count (int, optional): The amount of steps to simulate.
        Returns:
            Pandas Dataframe with values.
        """
        logging.info(
            "Initial number wolves: %s", self.schedule.get_breed_count(Wolf)
        )
        logging.info(
            "Initial number elk: %s", self.schedule.get_breed_count(Elk)
        )

        result_dicts = []

        for _ in range(step_count):
            result = self.step()
            result_dicts.append(result)

        logging.info(
            "Final number wolves: %s", self.schedule.get_breed_count(Wolf)
        )
        logging.info(
            "Final number elk: %s", self.schedule.get_breed_count(Elk)
        )
        return pd.DataFrame(result_dicts)