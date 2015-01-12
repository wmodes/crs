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
import logging.config
import json

from time import time,sleep

# installed modules
# noinspection PyUnresolvedReferences
sys.path.append('..')     # Add path to find OSC
from OSC import OSCMessage

# local modules
import config

# local classes
from field import Field
from myoschandler import MyOSCHandler
from conductor import Conductor

# constants
FRAMERATE = config.framerate

# init logging
def setup_logging(default_path='logging.json',     default_level=logging.INFO,env_key='LOG_CFG'):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        

def main():
    # Configure logging
    setup_logging()

    # create logger
    logger = logging.getLogger(__name__)

    # initialize stuff
    field = Field()
    
    osc = MyOSCHandler()
    conductor = Conductor()
    field.update(osc=osc)
    osc.update(field=field, conductor=conductor)
    conductor.update(field=field)

    if os.path.isfile('settings.py'):
        logger.info( "Loading settings from settings.py")
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
