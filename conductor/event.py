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


__appname__ = "event.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# local modules
import config

class Event(object):
    """Represents a grouping of cells.

    /conductor/event [eid,"type",uid0,uid1,value,time]
    Stores the following values:
        m_id: unique event ID
        m_type: one of the following:
        m_uid0: the UID of the first target
        m_uid1: the UID of the second target
        m_value: intensity of the effect (unit value)
        m_timestamp: UTC unix time the event was created (s)

    """

    def __init__(self, field, id, type=None, uid0=None, uid1=None, value=None):
        self.m_field=field
        self.m_id = id
        self.m_type = type
        self.m_uid0 = uid0
        self.m_uid1 = uid1
        self.m_value = value
        self.m_createtime = time()
        self.m_timestamp = time()

    def update(self, type=None, uid0=None, uid1=None, value=None):
        if type is not None:
            self.m_type = type
        if uid0 is not None:
            self.m_uid0 = uid0
        if uid1 is not None:
            self.m_uid1 = uid1
        if value is not None:
            self.m_value = value
