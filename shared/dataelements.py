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

__appname__ = "dataelements_class.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules
from shared import config

# local classes
from shared import debug

# constants
LOGFILE = config.logfile

MAX_LEGS = config.max_legs
DEF_DIAM = config.default_diam
DIAM_PAD = config.diam_padding     # increased diam of circle around bodies

# init debugging
dbug = debug.Debug()


class Attr(object):
    """Represents an attribute that is attached to a cell or connector.
    
    Stores the following values:
        m_type: The time of attr (str)
        m_id: UID, CID, GID, and EID of the parent object
        m_origvalue: A value associated with the attr
        m_value: A value associated with the attr
        m_timestamp: UTC unix time the event was created
    
    """

    def __init__(self, type, id, value=None):
        self.m_type = type
        self.m_id = id
        self.m_origvalue = value
        self.m_value = value
        self.m_timestamp = time()

    def update(self, value=None):
        if value is not None:
            self.m_value = value
        self.m_timestamp = time()


class Event(object):
    """Represents a grouping of cells.

    /conductor/event [eid,"type",uid0,uid1,value,time]
    Stores the following values:
        m_id: unique event ID
        m_type: one of the following:
        m_uid0: the UID of the first target
        m_uid1: the UID of the second target
        m_value: intensity of the effect (unit value)
        m_timestamp: UTC unix time the event was created (s)

    """

    def __init__(self, field, id, type=None, uid0=None, uid1=None, value=None):
        self.m_field=field
        self.m_id = id
        self.m_type = type
        self.m_uid0 = uid0
        self.m_uid1 = uid1
        self.m_value = value
        self.m_timestamp = time()

    def update(self, type=None, uid0=None, uid1=None, value=None):
        if type is not None:
            self.m_type = type
        if uid0 is not None:
            self.m_uid0 = uid0
        if uid1 is not None:
            self.m_uid1 = uid1
        if value is not None:
            self.m_value = value


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


class Body(object):

    """Represents a leg within a cell.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: UID of target
        x,y: position of person within field in m
        ex,ey: standard error of measurement (SEM) of position, in meters 
        spd, heading: estimate of speed of person in m/s, heading in degrees
        espd, eheading: SEM of spd, heading
        facing: direction person is facing in degees
        efacing: SEM of facing direction
        diam: estimated mean diameter of legs
        sigmadiam: estimated sigma (sqrt(variance)) of diameter
        sep: estimated mean separation of legs
        sigmasep: estimated sigma (sqrt(variance)) of sep
        leftness: measure of how likely leg 0 is the left leg
        vis: number of frames since a positive fix was found for either leg

    """

    def __init__(self, field, id, x=None, y=None, ex=None, ey=None, 
                 spd=None, espd=None, facing=None, efacing=None, 
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        self.m_field=field
        self.m_id = id
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


class Cell(object):
    """Represents one person/object on the floor.

    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: the id of this cell (unique, but not enforced)
        m_x, m_y: center of cell (coordinate tupple in cm)
        m_body_diam: diam of the person within the cell (cm)
        m_diam: diam of the cell surrounding the person (cm)
        m_visible: is this cell displayed currently? (boolean)
        m_conx_dict: connectors attached to this cell (index by cid)
        m_attr_dict: dict of attrs applied to this cell (indexed by type)
        m_leglist: list of Leg objects
        m_body: Body object
        m_gid: GID of group this cell belongs to
        m_timestamp: time that cell was created

    update: set center, readius, and attrs
    geoupdate: set geo data for cell
    set_attrs: add attrs to the attrs list
    add_connector: add new connector to the list connected to this cell
    del_connector: delete a connector from the list connected to this cell

    """

    def __init__(self, field, id, x=None, y=None, vx=None, vy=None, major=None, 
                    minor=None, gid=None, gsize=None, visible=None):
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
        self.m_attr_dict = {}
        #TODO: Move this to graphics engine
        self.m_diam = self.m_body_diam + DIAM_PAD
        if visible is None:
            self.m_visible = True
        #
        # init vars
        self.m_conx_dict = {}
        self.m_body = Body(field, id)
        # create an array of leg instances
        self.m_leglist = []
        for i in range(MAX_LEGS):
            self.m_leglist.append(Leg(field, id, i))
        self.m_gid = gid
        self.m_fromcenter = 0
        self.m_fromnearest = 0
        self.m_fromexit = 0
        self.m_timestamp = time()

    def update(self, x=None, y=None, vx=None, vy=None, major=None, 
                    minor=None, gid=None, gsize=None, visible=None):
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

    def geoupdate(self, fromcenter=None, fromnearest=None, fromexit=None):
        """Store geo data for cell."""
        if fromcenter is not None:
            self.m_fromcenter = fromcenter
        if fromnearest is not None:
            self.m_fromnearest = fromnearest
        if fromexit is not None:
            self.m_fromexit = fromexit

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

class Connector(object):

    """Represents a connector between two cells.
    
    Stores the following values:
        m_field: store a back ref to the field that called us
        m_id: the id of this connector (unique, but not enforced)
        m_cell0, m_cell1: the two cells connected by this connector
        m_attr_dict: dict of attrs applied to this conx (indexed by type)
        m_visible: is this cell displayed currently? (boolean)

    add_atts: add attrs to the attrs list
    conx_disconnect_thyself: Disconnect cells this connector refs

    """

    def __init__(self, field, id, cell0, cell1):
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

    def update(self, visible=None):
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

    def update_attr(self, type, value):
        """Update attr, create it if needed."""
        if type in self.m_attr_dict:
            self.m_attr_dict[type].update(value)
        else:
            self.m_attr_dict[type] = Attr(type, self.m_id, value)

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

