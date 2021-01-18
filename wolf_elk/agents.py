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
from mesa import Agent
from .walker import Walker

import random
import logging


class Elk(Walker):
    """
    A elk that walks around, reproduces (asexually) and gets eaten.
    """
    def __init__(self, unique_id, pos, model, moore, age, energy=None):
        """
        Create a Pack.
        Args:
            unique_id        (int): ID Generated by Mesa
            pos            (tuple): Tuple with the coordinates
            model     (mesa.Model): Model-object
            moore           (bool): Use Moore Neighborhood
            age              (int): Age
            energy           (int): Initial energy level
        """
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.age = age

    def step(self):
        """
        A model step. Move, then eat grass and reproduce.
        """
        self.random_move()
        self.age += 1 / 26
        self.energy -= 1

        # If there is grass available, eat it
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        grass_patch = [
            obj for obj in this_cell if isinstance(obj, GrassPatch)
        ][0]
        if grass_patch.fully_grown:
            self.energy += self.model.elk_gain_from_food
            grass_patch.fully_grown = False

        # Death
        if self.energy < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

        if self.random.random() < self.model.elk_reproduce:
            # Create a new Elk:
            self.energy /= 2
            calf = Elk(
                self.model.next_id(),
                self.pos,
                self.model,
                self.moore,
                0,
                self.energy
            )
            self.model.grid.place_agent(calf, self.pos)
            self.model.schedule.add(calf)


class Pack(Walker):
    """
    Agent which holds a collection of wolves. Wolves are added to the pack and
    when the pack is large enough and finds an Elk, it eats and the pack is
    disbanded.
    """
    def __init__(self, unique_id, pos, model, wolves: list, moore: bool):
        """
        Create a Pack.
        Args:
            unique_id        (int): ID Generated by Mesa
            pos            (tuple): Tuple with the coordinates
            model     (mesa.Model): Model-object
            wolves          (list): List of Wolves initial
            moore           (bool): Whether the model uses Moore neighborhood.
        """
        super().__init__(unique_id, pos, model, moore=moore)
        self.wolves = wolves
        self.min_pack = 4
        for wolf in wolves:
            self.add_wolf_to_pack(wolf)

    def step(self):
        """
        Step function for the Pack.
        """
        logging.debug("Wolf pack size {}".format(len(self.wolves)))
        self.random_move()
        if (len(self.wolves) < self.min_pack):
            self.find_wolf_for_pack()
            logging.debug("Pack size below minimum")
        else:
            logging.debug("Pack up to size")

        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        elk = [obj for obj in this_cell if isinstance(obj, Elk)]

        if (len(elk) > 0 and len(self.wolves) >= 4):
            elk_to_eat = self.random.choice(elk)
            self.model.grid._remove_agent(self.pos, elk_to_eat)
            self.model.schedule.remove(elk_to_eat)
            logging.debug('Pack has eated, disbanding.')
            self.pack_has_eaten()
        for wolf in self.wolves:
            wolf.energy -= 1
            if (wolf.energy < 0):
                self.model.schedule.remove(wolf)
                self.wolves.remove(wolf)
            if self.random.random() < self.model.wolf_reproduce:
                # Create a new wolf cub
                logging.debug("Wolf born in pack")
                wolf.energy /= 2
                cub = Wolf(
                    self.model.next_id(),
                    self.pos,
                    self.model,
                    self.moore,
                    wolf.energy
                )
                cub.pack = True
                self.model.schedule.add(cub)
                self.wolves.append(cub)

        if (len(self.wolves) < 2):
            logging.debug("Disbanding small pack")
            for wolf in self.wolves:
                self.remove_from_pack(wolf)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

    def filter_func_pack(self, packs):
        """
        Filter the list of packs.
        Args:
            packs (list): List of packs to filter.
        """
        return [pack for pack in packs if len(pack.wolves) < self.min_pack]

    def filter_wolves(self, agents):
        """
        Filter the list of wolves.
        Args:
            agents (list): List of wolf-agents to filter.
        """
        return [
            agent for agent in agents if agent.energy < 20 and not agent.pack
        ]

    def find_wolf_for_pack(self):
        """
        Find a wolf in the neighborhood.
        """
        agent = self.move_towards_specified_kind(Wolf, 4, self.filter_wolves)
        if (agent):
            logging.debug("Next wolf found is: {}".format(agent))
            logging.debug("Pack size is now {}".format(len(self.wolves)))
            self.add_wolf_to_pack(agent)
        else:
            self.find_pack_for_pack()

    def find_pack_for_pack(self):
        """
        Find a pack in the neighborhood.
        """
        pack = self.move_towards_specified_kind(Pack, 4, self.filter_func_pack)
        if (pack):
            logging.debug("Next pack found is: {}".format(pack))
            logging.debug("Pack size is now {}".format(len(self.wolves)))
            self.add_pack_to_pack(pack)

    def add_pack_to_pack(self, pack):
        """
        Add a pack to this pack and dissolve the other one.
        """
        logging.debug("Merging packs")
        for wolf in pack.wolves:
            self.add_wolf_to_pack(wolf)
        logging.debug("Pack is now {} wolves".format(len(self.wolves)))
        self.model.schedule.remove(pack)
        self.model.grid._remove_agent(pack.pos, pack)

    def add_wolf_to_pack(self, wolf):
        """
        Add wolf to pack.
        """
        if (not wolf.pack):
            self.model.grid._remove_agent(wolf.pos, wolf)
            wolf.pack = True
        self.wolves.append(wolf)

    def remove_from_pack(self, wolf):
        """
        Remove wolf from this pack.
        """
        self.model.grid.place_agent(wolf, wolf.pos)
        wolf.pack = False
        self.wolves.remove(wolf)

    def pack_has_eaten(self):
        """
        Pack has eaten. Add kills to wolf, add energy and disband the pack.
        """
        logging.debug("Pack disbanding")
        for wolf in self.wolves:
            wolf.energy += self.model.wolf_gain_from_food
            wolf.kills += 1
            wolf.pack = False
            self.model.grid.place_agent(wolf, wolf.pos)
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)

    # Equality operators to overrule comparison in the heapq
    def __eq__(self, other):
        self.__class__ == other.__class__ and self.pos == other.pos

    def __lt__(self, other):
        return True


class Wolf(Walker):
    """
    A wolf that walks around, reproduces (asexually) and eats elk.
    THe wolf is hungry:
    1. Check in the radius for other hungry wolves
    1a. If None, then move random
    1b. If Yes, then move to other Wolf and form pack
    2. Check if cell contains Elk in radius
    2a. If Yes, eat, set Pack to False.
    2b. If No, stil move as pack
    3. If one dies, set Pack to False
    """
    def __init__(self, unique_id, pos, model, moore, energy=None):
        """
        Create a Wolf.
        Args:
            unique_id        (int): ID Generated by Mesa
            pos            (tuple): Tuple with the coordinates
            model     (mesa.Model): Model-object
            moore           (bool): Whether the model uses Moore neighborhood.
            energy           (int): Initial energy
        """
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.kills = 0
        self.pack = False

    def filter_func(self, agents):
        """
        Filter wolves from list.
        """
        return [
            agent for agent in agents if agent.energy < 20 and not agent.pack
        ]

    def step(self):
        """
        Step function for the Wolf-object
        """
        if (self.pack):
            # If part of a pack, the pack controls the Wolf and the rest is
            # skipped. The reason for this is that removing the wolf from the
            # scheduler gives iteration errors.
            return

        self.random_move()
        self.energy -= 1
        logging.debug("Wolf info: {} {} {}".format(
            self.energy, self.kills, self.pack
        ))
        if self.energy < 20:
            """
            A wolf first tries to create a pack to hutn down an Elk.
            If that is not possible, a Wolf tries to kill the elk, but with
            a smaller probability of success.
            """
            agent = self.move_towards_own_kind(4, self.filter_func)
            if (agent):
                pack = Pack(
                    self.model.next_id(), self.pos, self.model, [], self.moore
                )
                self.model.schedule.add(pack)
                self.model.grid.place_agent(pack, pack.pos)
                pack.add_wolf_to_pack(agent)
                pack.add_wolf_to_pack(self)
                return

            # See if there are Elks available
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            elk = [obj for obj in this_cell if isinstance(obj, Elk)]

            if len(elk) > 0:
                if (random.random() < 0.1):
                    elk_to_eat = self.random.choice(elk)
                    self.energy += self.model.wolf_gain_from_food

                    # Kill the elk
                    self.kills += 1
                    self.model.grid._remove_agent(self.pos, elk_to_eat)
                    self.model.schedule.remove(elk_to_eat)

        # Death or reproduction
        if self.energy < 0:
            self.death()
        else:
            if self.random.random() < self.model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(
                    self.model.next_id(),
                    self.pos,
                    self.model,
                    self.moore,
                    self.energy
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)

    def death(self):
        """
        Removes a dead wolf from the model.
        """
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)

    # Equality operators to overrule comparison in the heapq
    def __eq__(self, other):
        self.__class__ == other.__class__ and self.pos == other.pos

    def __lt__(self, other):
        return True


class GrassPatch(Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by elk
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