#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visual subsystem module contains main loop and majority of important classes.

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
from time import time,sleep
from itertools import combinations

# installed modules
import pyglet

# local modules
from shared import config

# local classes
from shared import debug
from myfieldelements import MyField
from myoschandlers import MyOSCHandler

# constants
LOGFILE = config.logfile
FRAMERATE = config.framerate

GRAPHMODES = config.graphic_modes
GRAPHOPTS = {'screen': 1, 'osc': 2, 'etherdream':3}

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

    # initialize field
    field = MyField()
    # initialize pyglet 
    field.init_screen()

    osc = MyOSCHandler(field)
    field.update(osc=osc)

    keep_running = True
    while keep_running:

        starttime = time()

        # call user script
        osc.each_frame()

        pyglet.clock.tick()

        for window in pyglet.app.windows:
            pass
        window.switch_to()
        window.dispatch_events()
        field.render_all()
        field.draw_all()
        window.dispatch_event('on_draw')
        #window.clear()
        window.flip()

        #TODO: Move this somewhere sensible
        if GRAPHMODES & GRAPHOPTS['osc']:
            if dbug.LEV & dbug.GRAPH: 
                print "Main:OSC to laser:", OSCPATH['graph_update']
            field.m_osc.send_laser(OSCPATH['graph_update'],[])

        keep_running = osc.m_run & field.m_still_running

        #for (cell0,cell1) in list(combinations(field.m_cell_dict.values(), 2)):
            #field.update_conx_attr(cell0, cell1, 'friends', 1.0)

        #TODO: Change this to be triggered by Frame msg
        timeleft = 1/FRAMERATE - (time() - starttime)
        if timeleft > 0:
            #print "KILLME:Sleep for",timeleft,"seconds"
            sleep(timeleft)

    osc.m_oscserver.close()

if __name__ == '__main__':
    sys.exit(main())
