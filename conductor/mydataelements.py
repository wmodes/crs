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

__appname__ = "mydataelements.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules
from shared import config

# local classes
from shared import debug
from shared.dataelements import Cell,Connector,Group

# constants
LOGFILE = config.logfile

# init debugging
dbug = debug.Debug()

class Journal(object):
    """Journal entry for storing history of cells.

    Stores the following values:
        m_type: Connection type
        m_cell: Other cell involved
        m_value: Value when it started
        m_time: Length of this connection
        m_timestamp: When this journal entry was made
    """
    def __init__(self, type, uid0, uid1, value, time):
        self.m_type = type
        self.m_uid0 = uid0 # The uid of this cell
        self.m_uid1 = uid1 # The uid of the other cell
        self.m_value = value
        self.m_time = time
        self.m_timestamp = time()


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
        self.m_history.append(Journal(type, self.id, uid1, value, time))

    def get_history(self, uid0, uid1):
        shared_history = []
        for entry in self.m_history:
            if entry.uid1 == uid1:
                shared_history.append(entry)
        return shared_history

    def have_history(self, uid0, uid1):
        for entry in self.m_history:
            if entry.uid == uid:
                return True
        return False

    def age(self, uid):
        """Returns the age of a cell in seconds."""
        return time() - self.m_timestamp

class MyConnector(Connector):
    """Represents a connector between two cells.

    Create a connector as a subclass of the basic data element.

    """

class MyGroup(Group):
    """Represents a group of people.

    Create a group as a subclass of the basic data element.

    """

