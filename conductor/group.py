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


__appname__ = "group.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# local modules
import config

# local classes
from attr import Attr

class Group(object):
    """Represents a grouping of cells.

    /pf/group samp gid gsize duration centroidX centroidY diameter
    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: GID of group
        m_gsize: number of people in group (int)
        m_duration: time since first formed in seconds
        m_x,m_y: position within field in m
        m_diam: current diameter (float in m)
        m_cell_dict: dictionary of cells in this group (indexed by uid)
        m_attr_dict: dict of attrs applied to this cell (indexed by type)
        m_visible: is this group displayed currently? (boolean)

    """

    def __init__(self, field, id, gsize=None, duration=None, x=None, y=None,
                 diam=None):
        self.m_field=field
        self.m_id = id
        self.m_gsize = gsize
        self.m_duration = duration
        self.m_x = x
        self.m_y = y
        self.m_diam = diam
        self.m_cell_dict = {}
        self.m_attr_dict = {}
        self.m_visible = True

    def update(self, gsize=None, duration=None, x=None, y=None, diam=None,
                visible=None):
        if gsize is not None:
            self.m_gsize = gsize
        if duration is not None:
            self.m_duration = duration
        if x is not None:
            self.m_x = x
        if y is not None:
            self.m_y = y
        if diam is not None:
            self.m_diam = diam
        if visible is not None:
            self.m_visible = visible

    def add_attr(self, type, value):
        self.m_attr_dict[type] = Attr(type, self.m_id, value)

    def del_attr(self, type):
        if type in self.m_attr_dict:
            del self.m_attr_dict[type]

    def add_cell(self, uid):
        """Add cell to group."""
        if uid in self.m_field.m_cell_dict:
            self.m_cell_dict[uid] = self.m_field.m_cell_dict[uid]

    def drop_cell(self, uid):
        """Remove a cell from this group's list of cells."""
        if uid in self.m_cell_dict:
            del self.m_cell_dict[uid]

    def drop_all_cells(self):
        for uid in self.m_cell_dict:
            if uid in self.m_cell_dict:
                del self.m_cell_dict[uid]
