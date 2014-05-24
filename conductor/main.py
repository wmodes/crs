#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conductor subsystem module contains main loop and majority of important classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
lSpace highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "visualsys.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"


# core modules
import sys
import warnings
import logging
from time import time


# installed modules
# noinspection PyUnresolvedReferences
from OSC import OSCMessage

# local modules
from shared import config

# local classes
from shared import debug
from myfieldelements import MyField
from myoschandlers import MyOSCHandler
from conductorelements import Conductor

# constants
LOGFILE = config.logfile

OSCPATH = config.oscpath

XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field
XMIN_VECTOR = config.xmin_vector
YMIN_VECTOR = config.ymin_vector
XMAX_VECTOR = config.xmax_vector
YMAX_VECTOR = config.ymax_vector
XMIN_SCREEN = config.xmin_screen
YMIN_SCREEN = config.ymin_screen
XMAX_SCREEN = config.xmax_screen
YMAX_SCREEN = config.ymax_screen
DEF_MARGIN = config.default_margin
MODE_SCREEN = 0
MODE_VECTOR = 1
PATH_UNIT = config.path_unit
BLOCK_FUZZ = config.fuzzy_area_for_cells

MIN_CONX_DIST = config.minimum_connection_distance

MAX_LOST_PATIENCE = config.max_lost_patience

# init debugging
dbug = debug.Debug()


# create logger
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=LOGFILE,level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')


def main():

    from sys import stdout

    CYCLETIME = 1/25.0

    # initialize field
    field = MyField()

    osc = MyOSCHandler(field)
    field.update(osc=osc)
    conductor = Conductor(field)

    keep_running = True
    while keep_running:

        starttime = time()

        # call user script
        osc.each_frame()

        # do conductor calculations and inferences
        conductor.age_and_expire_connections()
        conductor.update_all_connections()

        # send regular reports out
        osc.send_regular_reports()

        keep_running = osc.m_run & field.m_still_running

        #TODO: Change this to be triggered by Frame msg
        while time() - starttime > CYCLETIME:
            pass

    osc.m_oscserver.close()

if __name__ == '__main__':
    sys.exit(main())
