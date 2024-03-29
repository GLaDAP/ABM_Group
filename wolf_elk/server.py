"""
GROUP:      LIMPENS (9)
DATE:       18 January 2021
AUTHOR(S):  Karlijn Limpens
            Joos Akkerman
            Guido Vaessen
            Stijn van den Berg
            David Puroja
DESCRIPTION:This file contains code to show the web interface for the model.
            It contains elements to add charts, change the slider variables and
            values and to change the canvas size.
            Part of the code (Base function setup) is from Mesa Examples:
            https://github.com/projectmesa/mesa/tree/master/examples/wolf_sheep
"""
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from .wolf import Wolf, Pack
from .agents import Elk, GrassPatch
from .model import WolfElk


def wolf_elk_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Elk:
        portrayal["Shape"] = "wolf_elk/resources/elk.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    if type(agent) is Pack:
        portrayal["Shape"] = "wolf_elk/resources/pack.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    elif type(agent) is Wolf:
        portrayal["Shape"] = "wolf_elk/resources/wolf.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is GrassPatch:
        if agent.fully_grown:
            portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
        else:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(wolf_elk_portrayal, 40, 40, 1000, 1000)

chart_element = ChartModule(
    [
        {"Label": "Wolves", "Color": "#AA0000"},
        {"Label": "Elks", "Color": "#666666"}
    ]
)
chart_element2 = ChartModule(
    [{"Label": "Elks age", "Color": "#666666"}]
)

chart_element3 = ChartModule(
    [{"Label": "Killed Elks/Wolf", "Color": "#666666"}]
)

chart_element4 = ChartModule(
    [{"Label": "Packs", "Color": "#666666"}]
)

model_params = {
    "grass_regrowth_time": UserSettableParameter(
        "slider", "Grass Regrowth Time", 20, 1, 50
    ),
    "initial_elk": UserSettableParameter(
        "slider", "Initial Elk Population", 200, 50, 500
    ),
    "initial_wolves": UserSettableParameter(
        "slider", "Initial Wolf Population", 20, 10, 100
    ),
    "pack_size_threshold": UserSettableParameter(
        "slider", "Minimum Pack size", 1, 1, 4
    ),
    "wolf_reproduce": UserSettableParameter(
        "slider",
        "Wolf Reproduction Rate",
        0.05,
        0.01,
        1.0,
        0.01,
        description="The rate at which wolf agents reproduce.",
    ),
    "wolf_gain_from_food": UserSettableParameter(
        "slider", "Wolf Gain From Food Rate", 20, 1, 50
    ),
    "elk_gain_from_food": UserSettableParameter(
        "slider", "Elk Gain From Food", 4, 1, 10
    ),
}

server = ModularServer(
    WolfElk,
    [
        canvas_element,
        chart_element,
        chart_element2,
        chart_element3,
        chart_element4
    ], "Wolf Elk Predation", model_params
)
server.port = 8521
