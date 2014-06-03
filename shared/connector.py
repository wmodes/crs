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

__appname__ = "connector.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config

# local classes
from shared.attr import Attr
from shared import debug

# constants
LOGFILE = config.logfile

MAX_LEGS = config.max_legs
DEF_DIAM = config.default_diam
DIAM_PAD = config.diam_padding     # increased diam of circle around bodies

# init debugging
dbug = debug.Debug()



class Connector(object):

    """Represents a connector between two cells.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: the id of this connector (unique, but not enforced)
        m_cell0, m_cell1: the two cells connected by this connector
        m_attr_dict: dict of attrs applied to this conx (indexed by type)
        m_visible: is this cell displayed currently? (boolean)
        m_frame: last frame in which we were updated

    add_atts: add attrs to the attrs list
    conx_disconnect_thyself: Disconnect cells this connector refs

    """

    def __init__(self, field, id, cell0, cell1, frame=None):
        # process passed params
        self.m_field=field
        self.m_id = id
        self.m_cell0 = cell0
        self.m_cell1 = cell1
        self.m_attr_dict = {}
        # init other values
        self.m_path = []
        self.m_score = 0
        self.m_visible = True
        # tell the cells themselves that they now own a connector
        cell0.add_connector(self)
        cell1.add_connector(self)
        self.m_frame = frame

    def update(self, visible=None, frame=None):
        """Update attr, create it if needed."""
        # refresh the cells that the connector points to
        uid0 = self.m_cell0.m_id
        uid1 = self.m_cell1.m_id
        if uid0 in self.m_field.m_cell_dict:
            if self.m_cell0 != self.m_field.m_cell_dict[uid0]:
                if dbug.LEV & dbug.DATA:
                    print "Connector:conx_update:Conx",self.m_id,"needed refresh"
                self.m_cell0 = self.m_field.m_cell_dict[uid0]
        if uid1 in self.m_field.m_cell_dict:
            if self.m_cell1 != self.m_field.m_cell_dict[uid1]:
                if dbug.LEV & dbug.DATA:
                    print "Connector:conx_update:Conx",self.m_id,"needed refresh"
                self.m_cell1 = self.m_field.m_cell_dict[uid1]
        if visible is not None:
            self.m_visible = visible
        if frame is not None:
            self.m_frame = frame

    def update_attr(self, type, value):
        """Update attr, create it if needed."""
        if type in self.m_attr_dict:
            self.m_attr_dict[type].update(value)
        else:
            self.m_attr_dict[type] = Attr(type, self.m_id, value)

    def check_for_attr(self, type):
        if type in self.m_attr_dict:
            return True
        return False

    def del_attr(self, type):
        if type in self.m_attr_dict:
            del self.m_attr_dict[type]

    def conx_disconnect_thyself(self):
        """Disconnect cells this connector refs & this connector ref'd by them.

        To actually delete it, remove it from the list of connectors in the Field
        class.
        """
        if dbug.LEV & dbug.DATA: print "Connector:conx_disconnect_thyself:Disconnecting ",self.m_id,"between",\
                self.m_cell0.m_id,"and",self.m_cell1.m_id
        # for simplicity's sake, we do the work rather than passing to
        # the object to do the work
        # delete the connector from its two cells
        if self.m_id in self.m_cell0.m_conx_dict:
            del self.m_cell0.m_conx_dict[self.m_id]
        if self.m_id in self.m_cell1.m_conx_dict:
            del self.m_cell1.m_conx_dict[self.m_id]
        # delete the refs to those two cells
        self.m_cell0 = None
        self.m_cell1 = None
