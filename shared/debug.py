#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module that handles debuging info.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "debug.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# local modules
import config

class Debug(object):

    # noinspection PyPep8Naming,PyPep8Naming,PyPep8Naming
    def __init__(self):
        self.LEV = config.debug_level
        self.MORE  = 0b00000001 # 1
        self.FIELD = 0b00000010 # 2
        self.DATA  = 0b00000100 # 4
        self.GRAPH = 0b00001000 # 8
        self.MSGS  = 0b00010000 # 16
        self.PYG   = 0b00100000 # 32

