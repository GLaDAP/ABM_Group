from mesa import Agent
from .walker import Walker

class Elk(Walker):
    """
    A elk that walks around, reproduces (asexually) and gets eaten.
    """

    # energy = None

    def __init__(self, unique_id, pos, model, moore, age, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.age = age

    def step(self):
        """
        A model step. Move, then eat grass and reproduce.
        """
        self.random_move()
        # living = True
        self.age += 1 / 26 # two weeks
        if self.model.grass:
            # Reduce energy
            self.energy -= 1

            # If there is grass available, eat it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
            if grass_patch.fully_grown:
                self.energy += self.model.elk_gain_from_food
                grass_patch.fully_grown = False

            # Death
            if self.energy < 0:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)
                # living = False

        if  self.random.random() < self.model.elk_reproduce:
            # Create a new Elk:
            if self.model.grass:
                self.energy /= 2
            calf = Elk(
                self.model.next_id(), self.pos, self.model, self.moore, 0, self.energy
            )
            self.model.grid.place_agent(calf, self.pos)
            self.model.schedule.add(calf)


class Wolf(Walker):
    """
    A wolf that walks around, reproduces (asexually) and eats elk.
    """

    # energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy

    def step(self):
        self.random_move()
        self.energy -= 1

        # If there are elk present, eat one
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        elk = [obj for obj in this_cell if isinstance(obj, Elk)]
        if len(elk) > 0:
            elk_to_eat = self.random.choice(elk)
            self.energy += self.model.wolf_gain_from_food

            # Kill the elk
            self.model.grid._remove_agent(self.pos, elk_to_eat)
            self.model.schedule.remove(elk_to_eat)

        # Death or reproduction
        if self.energy < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
        else:
            if self.random.random() < self.model.wolf_reproduce:
                # Create a new wolf cub
                self.energy /= 2
                cub = Wolf(
                    self.model.next_id(), self.pos, self.model, self.moore, self.energy
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)


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
