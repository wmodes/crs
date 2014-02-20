#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related Space is an interactive multimedia installation that engages the themes of presence, interaction, and place. It is an innovative work that encourages playful interactions between participants and visually and sonically transforms a regularly trafficked space. It rewards participants’ active engagement and experimentation with sound and light."""
 
__appname__ = "corelated-conductor.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"
 
# imports
import config
import logging
import warnings 
import time
import daemon

# create logger
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=config.logfile,level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')
 
# constants

#options_and_logging():
#    """Handle command line options and start logging
#    Args:
#        None
#    """


