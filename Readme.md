# Wolf-Elk Predation Model

## Summary

The purpose of the model is to understand the dynamics when a wolf population is added to an area where elks live. The elk population live in an area where they can eat vegetation, but there is no natural enemy to cap the population, resulting in mass-starvation in winter due to shortage of food in the area. This leads to oscillations in population size. Introducing wolves in the area can stabilize the elk population, reducing oscillation of the elk population, preventing mass starvation.
### Entities variables
The model consists of three different types of entities: individual agents, spatial units and collectives. Each of these entities contain state variables or attributes that create their functionality. 
- **Individual Agents:** Two agent types are created that construct the predator-prey model. These two agent represent the wolf and elk individuals. Each contain different parameters that determine the behavior and working of the agents. The main principles of the model result in the hunting on elk by wolf. Different state variables are established from this principle. First the movement/vision of wolves where the agent observes if elks or wolves are in its range. The agent is able to look in all directions and therefore looks at its Moore neighborhood. Depending on the wolf's energy level, it will try to form a pack and hunt on the elk. For this, the wolf contains an energy threshold after which it will start seeking a pack. If the energy of an individual reaches zero, the agent dies. After killing an elk, the wolf gains energy. If the wolf is not able to find a pack to hunt with, it is able to hunt alone with with a certain probability: the lonely wolf hunt chance. The main behaviors of the wolf are thus driven by its individual level of energy.
    
    Elks also have an energy state variable which is increased by eating grass. Elk individuals reproduce by a reproduction rate dependent on the age of the agent. The agents moves randomly through the environment and consumes vegetation when available. All elks have an age variable which increases with every time step. This age variable determines the fertility and chance of getting for the individual elk. 

- **Spatial units:** In the model a multi-grid cell system is used provided by Mesa. The spatial unit is in this model the vegetation type, grass. Wolves do not have a direct impact on this spatial unit. However, elks consume the grass, after which the grass needs time to regrow in a deterministic and linear way, after which it is available for elks to consume again.
    
- **Collectives:** In the model one collective is created by the formation of hunting packs. When the energy levels of wolf agents is lower then their thresholds, they will search for other wolves to hunt with. They form a pack which subsequently hunt on elks and dissolve afterwards. The size of a pack is dependent on the pack size threshold. If multiple elk agents are in the vision of the pack it will select the elk with the highest probability of success. This is based on the age of the elk, which the pack directly can observe.
    

### Process Overview
Every time step the agents are activated in random order. When a wolf is activated, the wolf first moves through the grid, reducing its energy level. When the energy falls below the specified energy threshold, a wolf will start looking for other hungry wolves to create a pack or joins an already existing pack. When the wolf is added to a new or existing pack, it is removed from the scheduler: updates of the wolf agent are now done through the Pack-agent. In case a wolf cannot find another wolf or pack, it looks for elk in its radius and tries to attack the elk with a specified probability. If successful, energy is added to the wolf, otherwise the wolf does nothing. When the energy-level of the wolf is negative, the wolf dies, otherwise the wolf will try to reproduce asexually. If successful, a new wolf agent is added to the model with half of the energy of the parent, which is reduced from the parents energy.

The Pack agent is a collective of hungry wolves. They will search for elks in its radius when the pack has reached a minimum size where they can hunt an elk. If the size is below the threshold, the pack will try to merge with other packs or tries to find a hungry wolf. When there is an elk in its radius, it will go to the elk and eat it; in case there is more than one elk available, it picks one or multiple, based on the age of the elk and the energy-demand of the wolves. All the wolves in the pack are then updated with new energy, each with the same amount. When they did not find an elk, the pack will move randomly and the pack will check for each wolf if the energy level is still positive and which of the wolves are reproducing.

Lastly there is a GrassPatch agent which is fixed on the grid. It grows with a specified regrowth time countdown. When an Elk eats grass, the fully-grown variable is set to false and the countdown for regrowth is set to the specified number. At each step the countdown is reduced by one until it is negative, then the fully grown parameter is set to true.

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```
The dependencies are as follows:
- Mesa: to run the actual model
- pandas: to save the results from runs in a csv
- matplotlib: to plot the results
- salib: to perform the sensitivity analysis
## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* ``wolf_elk/walker.py``: This defines the ``Walker`` agent, which implements the behavior of moving accross the grid randomly and towards specific agents. The radius of movement is defined per agent. Both the Elk, Wolf and Pack agents will inherit from it.
* ``wolf_elk/agents.py``: Defines the Elk and GrassPatch agent classes.
* ``wolf_elk/wolf.py``: Defines the Wolf and Pack agent classes.
* ``wolf_elk/schedule.py``: Defines a custom variant on the RandomActivation scheduler, where all agents of one class are activated (in random order) before the next class goes -- e.g. all the wolves go, then all the elk, then all the grass.
* ``wolf_elk/model.py``: Defines the Wolf-Elk Predation model itself
* ``wolf_elk/server.py``: Sets up the interactive visualization server.
* ``run.py``: Launches a model visualization server.
* ``run_model.py``: Helper file to run the model multiple times and store statistics.
* ``sensititvity.py``: Helper file to perform sensitivity analysis on the model using SALib.
* ``empirical_data/elk_ratesbyage.csv``: Data-file with elk age rates from Northern Yellowstone park.
* ``empirical_data/popsize_elk_wolf_YSNorth.csv``: Data file with population sizes for elk and wolves in Yellowstone Park North.
## Further Reading

Part of the code used in this model is based on the Mesa examples repository found here: [Wolf-Sheep-Example](https://github.com/projectmesa/mesa/tree/master/examples/wolf_sheep)

