#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Console elements for CRS.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "consoleelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import curses

# installed modules

# local modules
#from shared import config

# local classes
#from shared import debug

# constants
#LOGFILE = config.logfile

# init debugging
#dbug = debug.Debug()


class Screen(object):

    def __init__(self):
        self.m_fullscreen = curses.initscr()
        curses.noecho() 
        curses.curs_set(0) 
        screen.keypad(1)
