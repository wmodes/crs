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

__appname__ = "journal.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config

# local classes
from shared import debug

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