#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Subclassed data element classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "mycell.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules
from shared import config

# local classes
from journal import Journal
from shared import debug
from shared.cell import Cell

# constants
LOGFILE = config.logfile

# init debugging
dbug = debug.Debug()


class MyCell(Cell):
    """ Create a cell as a subclass of the basic data element.

    Stores the following values:
        m_history: list of 

    """
    def __init__(self, field, id, x=None, y=None, vx=None, vy=None, 
                 major=None, minor=None, gid=None, gsize=None):
        self.m_history = []
        super(MyCell, self).__init__(field, id, x, y, vx, vy, major, 
                                     minor, gid, gsize)

    def record_history(self, type, uid1, value, time):
        self.m_history.append(Journal(type, self.m_id, uid1, value, time))

    def get_history(self, uid0, uid1):
        shared_history = []
        for entry in self.m_history:
            if entry.uid1 == uid1:
                shared_history.append(entry)
        return shared_history

    def have_history(self, uid0, uid1):
        for entry in self.m_history:
            if entry.uid == uid1:
                return True
        return False

    def age(self, uid):
        """Returns the age of a cell in seconds."""
        return time() - self.m_timestamp


