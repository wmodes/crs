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

__appname__ = "main.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"


#import debughook

# core modules
import os.path
import sys
import warnings
import logging
from time import time,sleep

# installed modules
# noinspection PyUnresolvedReferences
sys.path.append('..')     # Add path to find OSC
from OSC import OSCMessage

# local modules
import config

# local classes
import debug
from field import Field
from myoschandler import MyOSCHandler
from conductor import Conductor

# constants
LOGFILE = config.logfile
FRAMERATE = config.framerate

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

    CYCLETIME = 1/25.0

    # initialize stuff
    field = Field()
    osc = MyOSCHandler()
    conductor = Conductor()
    field.update(osc=osc)
    osc.update(field=field, conductor=conductor)
    conductor.update(field=field)

    if os.path.isfile('settings.py'):
        print "Loading settings from settings.py"
        execfile('settings.py')

    keep_running = True
    lastframe = None
    while keep_running:
        # call user script
        osc.each_frame()

        if field.m_frame != lastframe or \
            time() - lasttime > 1:
            # do conductor calculations and inferences
            field.check_for_abandoned_cells()
            conductor.update_all_cells()
            conductor.update_all_conx()

            # send regular reports out
            osc.send_regular_reports()
            lastframe = field.m_frame
            lasttime = time()
        else:
            # Still on the same frame, sleep for a fraction of the frame time to not hog CPU
            #field.m_osc.send_laser('/conductor/sleep',[field.m_frame])    # Useful for debugging -- can see in OSC stream when this process was sleeping
            sleep((1.0/FRAMERATE)/10)

        keep_running = osc.m_run & field.m_still_running

    osc.m_oscserver.close()

if __name__ == '__main__':
    #try:
    sys.exit(main())
    #except:
        #pass
