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

__appname__ = "body.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
import config

# local classes
import debug

# constants
LOGFILE = config.logfile

MAX_LEGS = config.max_legs
DEF_DIAM = config.default_diam
DIAM_PAD = config.diam_padding     # increased diam of circle around bodies

# init debugging
dbug = debug.Debug()



class Body(object):

    """Represents a leg within a cell.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: UID of target
        m_x,m_y: position of person within field in m
        m_ex,m_ey: standard error of measurement (SEM) of position, in meters
        m_spd, m_heading: estimate of speed of person in m/s, heading in degrees
        m_espd, m_eheading: SEM of spd, heading
        m_facing: direction person is facing in degees
        m_efacing: SEM of facing direction
        m_diam: estimated mean diameter of legs
        m_sigmadiam: estimated sigma (sqrt(variance)) of diameter
        m_sep: estimated mean separation of legs
        m_sigmasep: estimated sigma (sqrt(variance)) of sep
        m_leftness: measure of how likely leg 0 is the left leg
        m_vis: number of frames since a positive fix was found for either leg

    """

    def __init__(self, field, b_id, x=None, y=None, ex=None, ey=None,
                 spd=None, espd=None, facing=None, efacing=None,
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        self.m_field=field
        self.m_id = b_id
        self.m_x = x
        self.m_y = y
        self.m_ex = ex
        self.m_ey = ey
        self.m_spd = spd
        self.m_espd = espd
        self.m_facing = facing
        self.m_efacing = efacing
        self.m_diam = diam
        self.m_sigmadiam = sigmadiam
        self.m_sep = sep
        self.m_sigmasep = sigmasep
        self.m_leftness = leftness
        self.m_vis = vis

    def update(self, x=None, y=None, ex=None, ey=None,
                 spd=None, espd=None, facing=None, efacing=None,
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        if x is not None:
            self.m_x = x
        if y is not None:
            self.m_y = y
        if ex is not None:
            self.m_ex = ex
        if ey is not None:
            self.m_ey = ey
        if spd is not None:
            self.m_spd = spd
        if espd is not None:
            self.m_espd = espd
        if facing is not None:
            self.m_facing = facing
        if efacing is not None:
            self.m_efacing = efacing
        if diam is not None:
            self.m_diam = diam
        if sigmadiam is not None:
            self.m_sigmadiam = sigmadiam
        if sep is not None:
            self.m_sep = sep
        if sigmasep is not None:
            self.m_sigmasep = sigmasep
        if leftness is not None:
            self.m_leftness = leftness
        if vis is not None:
            self.m_vis = vis
