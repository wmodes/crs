#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data elements for CRS.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "attr.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules

# local classes
from shared import debug

# constants

# init debugging
dbug = debug.Debug()


class Attr(object):
    """Represents an attribute that is attached to a cell or connector.

    Stores the following values:
        m_type: The time of attr (str)
        m_id: UID, CID, GID, and EID of the parent object
        m_origvalue: A value associated with the attr
        m_value: A value associated with the attr
        m_timestamp: UTC unix time the event was created

    """

    def __init__(self, type, id, value=None):
        self.m_type = type
        self.m_id = id
        self.m_origvalue = value
        self.m_value = value
        self.m_createtime = time()
        self.m_updatetime = time()
        
    def update(self, value=None, aboveTrigger=False):
        if value is not None:
            self.m_value = value
        if aboveTrigger:
            self.m_updatetime = time()

    def decay_value(self, value=None):
        """Essentially update without updating the tiemstamp."""
        if value is not None:
            self.m_value = value