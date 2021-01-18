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
import sys
import logging


root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s \
                              - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)