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
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

class ElkWolf(Model):
    """
    Wolf-Elk Predation model
    """


    def __init__(
        self, 
        height,
        width,
        initial_elks,
        initial_wolves,
        elks_reproduction_rate,
        wolves_reproduction_rate,
        wolves_max_food,
        field_growth_time,
        elks_food_gain,
        elk_healty_proportion
    ):
        """
        Create a Elk-Wolf model with initial parameters.

        Args:
            initial_elks: The number of elks at the start of the model
            initial_wolves: The number of wolves at the start of the model

        """
        logging.debug("Initializing model.")

        super().__init__()
        
        self.height = height
        self.width = width
        
        # Initialize the continuous space field where the agents will be placed.
        self.space = ContinuousSpace(
            x_max = self.width, 
            y_max = self.height, 
            torus = True
        )

