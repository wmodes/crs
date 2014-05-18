#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Subclassed field class.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "myfieldelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config
from shared import debug

# local classes
from shared.fieldelements import Field
from mydataelements import MyCell,MyConnector

# constants

LOGFILE = config.logfile

DEF_RADIUS = config.default_radius

RAD_PAD = config.radius_padding     # increased radius of circle around bodies

XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field
BLOCK_FUZZ = config.fuzzy_area_for_cells

MIN_CONX_DIST = config.minimum_connection_distance

MAX_LOST_PATIENCE = config.max_lost_patience

# init debugging
dbug = debug.Debug()


class MyField(Field):
    """An object representing the field.  """

    cellClass = MyCell
    connectorClass = MyConnector

    def __init__(self):

        self.m_xmin_field = XMIN_FIELD
        self.m_ymin_field = YMIN_FIELD
        self.m_xmax_field = XMAX_FIELD
        self.m_ymax_field = YMAX_FIELD
        super(MyField, self).__init__()


    # Scaling

    def set_scaling(self,pmin_field=None,pmax_field=None):
        """Set up scaling in the field.

        A word about graphics scaling:
         * The vision tracking system (our input data) measures in meters.
         * The laser DAC measures in uh, int16? -32,768 to 32,768
         * Pyglet measures in pixels at the screen resolution of the window you create
         * The pathfinding units are each some ratio of the smallest expected radius

         So we will keep eveything internally in centemeters (so we can use ints
         instead of floats), and then convert it to the appropriate units before 
         display depending on the output mode

         """

        if pmin_field is not None:
            self.m_xmin_field = pmin_field[0]
            self.m_ymin_field = pmin_field[1]
        if pmax_field is not None:
            self.m_xmax_field = pmax_field[0]
            self.m_ymax_field = pmax_field[1]
