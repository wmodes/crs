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
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

class Attr(object):
    """Represents an attribute that is attached to a cell or connector.

    Stores the following values:
        m_type: The time of attr (str)
        m_id: UID, CID, GID, and EID of the parent object
        m_origvalue: A value associated with the attr
        m_value: A value associated with the attr
        m_timestamp: UTC unix time the event was created
        m_freshness: Freshness of connection - fraction of max_age since last triggerred
    """

    def __init__(self, a_type, a_id, value=None):
        self.m_type = a_type
        self.m_id = a_id
        self.m_origvalue = value
        self.m_createtime = time()
        self.m_value = value
        self.m_updatetime = time()
        self.m_freshness = 1.0

    def update(self, value=None, aboveTrigger=False):
        if value is not None:
            self.m_value = value
        if aboveTrigger:
            self.m_updatetime = time()
            self.m_freshness = 1.0

    def set_freshness(self, value):
        self.m_freshness = value
