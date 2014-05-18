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

# installed modules

# local modules
from shared import config

# local classes
from shared import debug
from shared.dataelements import Cell,Connector

# constants
LOGFILE = config.logfile

DEF_RADIUS = config.default_radius

# init debugging
dbug = debug.Debug()


class MyCell(Cell):
    """Represents one person/object on the floor.

    Create a cell as a subclass of the basic data element.
    
    Stores the following values:
        m_color: color of cell

    """

    def __init__(self, field, id, p=None, r=None, gid=None):
        super(MyCell, self).__init__(field, id, p, r, gid)

    def update(self, p=None, r=None, gid=None):
        """Store basic info and create a DataElement object"""
        super(MyCell, self).update(p, r, gid)


class MyConnector(Connector):
    """Represents a connector between two cells.

    Create a connector as a subclass of the basic data element.
    
    Stores the following values:
        m_cell0, m_cell1: the two cells connected by this connector

    """

    def __init__(self, field, id, cell0, cell1):
        """Store basic info and create a DataElement object"""
        # process passed params
        # store other params
        self.m_score = 0
        super(MyConnector,self).__init__(field, id, cell0, cell1)

