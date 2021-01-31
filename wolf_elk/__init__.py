"""
GROUP:       LIMPENS (9)
DATE:        18 January 2021
AUTHOR(S):   Karlijn Limpens
             Joos Akkerman
             Guido Vaessen
             Stijn van den Berg
             David Puroja
DESCRIPTION: This file contains lines to manage the logging in the model. Per
             default, verbose is set to False, muting all debugging
             information. If verbose is set to True, verbose information
             is shown.
"""
import sys
import logging

verbose = False
logging_level = logging.INFO
if (verbose):
    logging_level = logging.DEBUG

root = logging.getLogger()
root.setLevel(logging_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging_level)
formatter = logging.Formatter('%(asctime)s - %(name)s \
                              - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
