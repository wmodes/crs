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

# installed modules

# local modules
from shared import config

# local classes
from shared import debug
from shared.cell import Cell
from circle import Circle

# constants
LOGFILE = config.logfile

DEF_DIAM = config.default_diam
DEF_LINECOLOR = config.default_linecolor
DEF_GROUPCOLOR = config.default_groupcolor
DEF_BODYCOLOR = config.default_bodycolor
DEF_GUIDECOLOR = config.default_guidecolor
DEF_BKGDCOLOR = config.default_bkgdcolor
DRAW_BODIES = config.draw_bodies

# init debugging
dbug = debug.Debug()

class MyCell(Cell):
    """Represents one person/object on the floor.

    Create a cell as a subclass of the basic data element.

    Stores the following values:
        m_color: color of cell

    makeBasicShape: create the set of arcs that will define the shape

    """

    def __init__(self, field, id, x=None, y=None, vx=None, vy=None, major=None,
                 minor=None, gid=None, gsize=None, color=None):
        if color is None:
            self.m_color = DEF_LINECOLOR
        else:
            self.m_color = color
        self.m_body_color = DEF_BODYCOLOR
        self.m_shape = Circle()
        self.m_bodyshape = Circle()
        super(MyCell, self).__init__(field, id, x, y, vx, vy, major, minor,
                                     gid, gsize)

    def update(self, x=None, y=None, vx=None, vy=None, major=None,
               minor=None, gid=None, gsize=None, color=None, visible=None):
        """Store basic info and create a DataElement object"""
        if color is not None:
            self.m_color = color
        super(MyCell, self).update(x, y, vx, vy, major, minor, gid, gsize,
                                   visible)

    def draw(self):
        if self.m_x is not None and self.m_y is not None:
            self.m_shape.update(self.m_field, (self.m_x, self.m_y),
                                self.m_diam/2,
                                color=self.m_color,
                                solid=False)
            self.m_field.m_osc.send_laser(OSCPATH['graph_begin_cell'],[self.m_id])
            self.m_shape.draw()
            if DRAW_BODIES:
                self.m_bodyshape.update(self.m_field, (self.m_x, self.m_y),
                                          self.m_body_diam/2, 
                                          color=self.m_body_color,
                                          solid=True)
                self.m_bodyshape.draw()
            self.m_field.m_osc.send_laser(OSCPATH['graph_end_cell'],[self.m_id])


