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

__appname__ = "mygroup.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config

# local classes
from shared import debug
from shared.group import Group
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


class MyGroup(Group):
    """Represents a group on the floor.

    Create a group as a subclass of the basic data element.

    Stores the following values:
        m_color: color of cell

    """

    def __init__(self, field, id, gsize=None, duration=None, x=None, y=None,
                 diam=None, color=None):
        if color is None:
            self.m_color = DEF_GROUPCOLOR
        else:
            self.m_color = color
        self.m_shape = Circle()
        super(MyGroup, self).__init__(field, id, gsize, duration, x, y, diam)

    def update(self, gsize=None, duration=None, x=None, y=None,
                 diam=None, color=None):
        """Store basic info and create a DataElement object"""
        if color is not None:
            self.m_color = color
        super(MyGroup, self).update(gsize, duration, x, y, diam)

    def draw(self):
        if self.m_x is not None and self.m_y is not None:
            self.m_shape.update(self.m_field, (self.m_x, self.m_y),
                                self.m_diam/2, self.m_color, solid=False)
            self.m_shape.draw()