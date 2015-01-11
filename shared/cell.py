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


__appname__ = "cell.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules
from shared import config

# local classes
from shared.attr import Attr
from shared.body import Body
from shared.leg import Leg
from shared import debug

# constants
LOGFILE = config.logfile

MAX_LEGS = config.max_legs
DEF_DIAM = config.default_diam
DIAM_PAD = config.diam_padding     # increased diam of circle around bodies

# init debugging
dbug = debug.Debug()


class Cell(object):
    """Represents one person/object on the floor.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: the id of this cell (unique, but not enforced)
        m_x, m_y: center of cell (coordinate tupple in m)
        m_vx, m_vy: center of cell (coordinate tupple in m)
        m_body_diam: diam of the person within the cell (m)
        m_diam: diam of the cell surrounding the person (m)
        m_visible: is this cell displayed currently? (boolean)
        m_conx_dict: connectors attached to this cell (index by cid)
        m_attr_dict: dict of attrs applied to this cell (indexed by type)
        m_leglist: list of Leg objects
        m_body: Body object
        m_gid: GID of group this cell belongs to
        m_fromcenter: dist cell is from geo center of everyone
        m_fromnearest: dist cell is from another person
        m_fromexit: dist cell is from exit
        m_createtime: time that cell was created
        m_updatetime: time that cell was last updated
        m_frame: last frame in which we were updated

    update: set center, readius, and attrs
    geoupdate: set geo data for cell
    set_attrs: add attrs to the attrs list
    add_connector: add new connector to the list connected to this cell
    del_connector: delete a connector from the list connected to this cell

    """

    def __init__(self, field, id, x=None, y=None, vx=None, vy=None, major=None, 
                    minor=None, gid=None, gsize=None, visible=None, frame=None):
        # passed params
        self.m_field=field
        self.m_id = id
        self.m_x = x
        self.m_y = y
        self.m_vx = vx
        self.m_vy = vy
        if major is None:
            self.m_major = DEF_DIAM
            self.m_body_diam = DEF_DIAM
            self.m_diam = DEF_DIAM + DIAM_PAD
        else:
            self.m_major = major
            self.m_body_diam = major
            self.m_diam = major + DIAM_PAD
        self.m_minor = minor
        self.m_gid = gid
        self.m_gsize = gsize
        #TODO: Move this to graphics engine
        self.m_diam = self.m_body_diam + DIAM_PAD
        if visible is None:
            self.m_visible = True
        #
        # init vars
        self.m_attr_dict = {}
        self.m_conx_dict = {}
        self.m_body = Body(field, id)
        # create an array of leg instances
        self.m_leglist = []
        for i in range(MAX_LEGS):
            self.m_leglist.append(Leg(field, id, i))
        self.m_fromcenter = 0
        self.m_fromnearest = 0
        self.m_fromexit = 0
        self.m_createtime = time()
        self.m_updatetime = time()
        self.m_frame = frame

    def update(self, x=None, y=None, vx=None, vy=None, major=None, 
                    minor=None, gid=None, gsize=None, visible=None,     
                    frame=None):
        """Store basic info and create a DataElement object"""
        if x is not None:
            self.m_x = x
        if y is not None:
            self.m_y = y
        if vx is not None:
            self.m_vx = vx
        if vy is not None:
            self.m_vy = vy
        if major is not None:
            self.m_major = major
            self.m_body_diam = major
            self.m_diam = major + DIAM_PAD
        if minor is not None:
            self.m_minor = minor
        if gid is not None:
            self.m_gid = gid
        if gsize is not None:
            self.m_gsize = gsize
        if visible is not None:
            self.m_visible = visible
        if frame is not None:
            self.m_frame = frame
        self.m_updatetime = time()

    def geoupdate(self, fromcenter=None, fromnearest=None, fromexit=None):
        """Store geo data for cell."""
        if fromcenter is not None:
            self.m_fromcenter = fromcenter
        if fromnearest is not None:
            self.m_fromnearest = fromnearest
        if fromexit is not None:
            self.m_fromexit = fromexit
        self.m_updatetime = time()

    def update_body(self, x=None, y=None, ex=None, ey=None, 
                 spd=None, espd=None, facing=None, efacing=None, 
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        self.m_body.update(x, y, ex, ey, spd, espd, facing, efacing, 
                           diam, sigmadiam, sep, sigmasep, leftness, vis)

    def update_leg(self, leg, nlegs=None, x=None, y=None, 
                 ex=None, ey=None, spd=None, espd=None, 
                 heading=None, eheading=None, vis=None):
        self.m_leglist[leg].update(nlegs, x, y, ex, ey, spd, espd, 
                                   heading, eheading, vis)

    def add_attr(self, type, value):
        self.m_attr_dict[type] = Attr(type, self.m_id, value)

    def update_attr(self, type, value):
        if type not in self.m_attr_dict:
            self.m_attr_dict[type] = Attr(type, self.m_id, value)
        else:
            self.m_attr_dict[type].update(value)

    def del_attr(self, type):
        if type in self.m_attr_dict:
            del self.m_attr_dict[type]

    def add_connector(self, connector):
        self.m_conx_dict[connector.m_id] = connector

    def del_connector(self, connector):
        if connector.m_id in self.m_conx_dict:
            del self.m_conx_dict[connector.m_id]

    def cell_disconnect(self):
        """Disconnects all the connectors and refs it can reach.
        
        To actually delete it, remove it from the list of cells in the Field
        class.
        """
        if dbug.LEV & dbug.DATA: print "Cell:cell_disconnect:Disconnecting ",self.m_id
        # we make a copy because we can't iterate over the dict if we are
        # deleting stuff from it!
        new_conx_dict = self.m_conx_dict.copy()
        # for each connector attached to this cell...
        for connector in new_conx_dict.values():
            # OPTION: for simplicity's sake, we do the work rather than passing to
            # the object to do the work
            # delete the connector from its two cells
            if connector.m_id in connector.m_cell0.m_conx_dict:
                del connector.m_cell0.m_conx_dict[connector.m_id]
            if connector.m_id in connector.m_cell1.m_conx_dict:
                del connector.m_cell1.m_conx_dict[connector.m_id]
            # delete cells ref'd from this connector
            connector.m_cell0 = None
            connector.m_cell1 = None
            # now delete from this cell's list
            if connector.m_id in self.m_conx_dict:
                del self.m_conx_dict[connector.m_id]

            # OPTION: Let the objects do the work
            #connector.conx_disconnect_thyself()
            # we may not need this because the connector calls the same thing
            # for it's two cells, including this one
            #self.del_connector(connector)

