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

__appname__ = "leg.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# local modules
import config

class Leg(object):
    """Represents a leg within a cell.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_leg: leg number (0..nlegs-1)
        m_nlegs: number of legs target is modeled with
        m_x,m_y: position within field in m
        m_ex,m_ey: standard error of measurement (SEM) of position, in meters
        m_spd, heading: estimate of speed of leg in m/s, heading in degrees
        m_espd, eheading: SEM of spd, heading
        m_vis: number of frames since a positive fix was found for this leg

    """

    def __init__(self, field, id, leg=None, nlegs=None, x=None, y=None,
                 ex=None, ey=None, spd=None, espd=None,
                 heading=None, eheading=None, vis=None):
        self.m_field=field
        self.m_id = id
        self.m_leg = leg
        self.m_nlegs = nlegs
        self.m_x = x
        self.m_y = y
        self.m_ex = ex
        self.m_ey = ey
        self.m_spd = spd
        self.m_heading = heading
        self.m_espd = espd
        self.m_eheading = eheading
        self.m_vis = vis

    def update(self, leg=None, nlegs=None, x=None, y=None,
                 ex=None, ey=None, spd=None, espd=None,
                 heading=None, eheading=None, vis=None):
        if leg is not None:
            self.m_leg = leg
        if nlegs is not None:
            self.m_nlegs = nlegs
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
        if heading is not None:
            self.m_heading = heading
        if espd is not None:
            self.m_espd = espd
        if eheading is not None:
            self.m_eheading = eheading
        if vis is not None:
            self.m_vis = vis
