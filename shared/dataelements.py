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

# installed modules


# local modules
from shared import config

# local classes
from shared import debug

# constants
LOGFILE = config.logfile

MAX_LEGS = config.max_legs
DEF_RADIUS = config.default_radius
RAD_PAD = config.radius_padding     # increased radius of circle around bodies

# init debugging
dbug = debug.Debug()

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
        m_location: center of cell (coordinate tupple in cm)
        m_body_radius: radius of the person within the cell (cm)
        m_radius: radius of the cell surrounding the person (cm)
        m_visible: is this cell displayed currently? (boolean)
        m_connector_dict: connectors attached to this cell
        m_effects_list: list of effects applied to this cell
        m_leglist: list of Leg objects
        m_body: Body object

    update: set center, readius, and effects
    set_location: set the location value for this cell as an XY tuple
    set_effects: add effects to the effects list
    add_connector: add new connector to the list connected to this cell
    del_connector: delete a connector from the list connected to this cell

    """

    def __init__(self, field, id, p=None, r=None, effects=None):
        self.m_field=field
        self.m_id = id
        if p is None:
            self.m_location = ()
        else:
            self.m_location = p
        if r is None:
            self.m_body_radius = DEF_RADIUS
        else:
            self.m_body_radius = r
        if effects is None:
            self.m_effects_list = []
        else:
            self.m_effects_list += effects
        self.m_radius = self.m_body_radius*RAD_PAD
        self.m_visible = True
        self.m_connector_dict = {}
        self.m_effects_list = []
        # create an array of leg instances
        self.m_body = Body(field, id)
        self.m_leglist = []
        for i in range(MAX_LEGS):
            self.m_leglist.append(Leg(field, id, i))

    def update(self, p=None, r=None, effects=None):
        """Store basic info and create a DataElement object"""
        if p is not None:
            self.m_location = p
            self.m_body.m_x = p[0]
            self.m_body.m_y = p[0]
        if r is not None:
            self.m_body_radius = r
            self.m_radius = r*RAD_PAD
        if effects is not None:
            self.m_effects_list = effects

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

    def set_location(self, p):
        self.m_location=p

    def add_effects(self, effects):
        self.m_effects_list += effects
        
    def apply_effects(self):
        pass

    def add_connector(self, connector):
        self.m_connector_dict[connector.m_id] = connector

    def del_connector(self, connector):
        if connector.m_id in self.m_connector_dict:
            del self.m_connector_dict[connector.m_id]

    #def render(self):
    # moved to subclass

    #def draw(self):
    # moved to subclass

    def cell_disconnect(self):
        """Disconnects all the connectors and refs it can reach.
        
        To actually delete it, remove it from the list of cells in the Field
        class.
        """
        if dbug.LEV & dbug.DATA: print "Cell:cell_disconnect:Disconnecting ",self.m_id
        # we make a copy because we can't iterate over the dict if we are
        # deleting stuff from it!
        new_connector_dict = self.m_connector_dict.copy()
        # for each connector attached to this cell...
        for connector in new_connector_dict.values():
            # OPTION: for simplicity's sake, we do the work rather than passing to
            # the object to do the work
            # delete the connector from its two cells
            if connector.m_id in connector.m_cell0.m_connector_dict:
                del connector.m_cell0.m_connector_dict[connector.m_id]
            if connector.m_id in connector.m_cell1.m_connector_dict:
                del connector.m_cell1.m_connector_dict[connector.m_id]
            # delete cells ref'd from this connector
            connector.m_cell0 = None
            connector.m_cell1 = None
            # now delete from this cell's list
            if connector.m_id in self.m_connector_dict:
                del self.m_connector_dict[connector.m_id]

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
        m_effects_list: a list of effects that apply to this connector
        m_path: the computed coordinate path from cell0 to cell1
        m_score: a score to help with sorting? I can't remember (check gridmap)
        m_visible: is this cell displayed currently? (boolean)

    add_effects: add effects to the effects list
    add_path: add a computed path to this connector
    conx_disconnect_thyself: Disconnect cells this connector refs

    """

    def __init__(self, field, id, cell0, cell1, effects=None):
        """Store basic info and create a DataElement object"""
        # process passed params
        self.m_field=field
        self.m_id = id
        self.m_cell0 = cell0
        self.m_cell1 = cell1
        if effects is None:
            self.m_effects_list = []
        else:
            self.m_effects_list += effects
        # init other values
        self.m_path = []
        self.m_score = 0
        self.m_visible = True
        # tell the cells themselves that they now own a connector
        cell0.add_connector(self)
        cell1.add_connector(self)

    def add_effects(self, effects):
        self.m_effects_list += effects

    def apply_effects(self):
        pass

    # move to subclass?
    def add_path(self,path):
        """Record the path of this connector."""
        self.m_path = path

    #def render(self):
    # moved to subclass

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
        if self.m_id in self.m_cell0.m_connector_dict:
            del self.m_cell0.m_connector_dict[self.m_id]
        if self.m_id in self.m_cell1.m_connector_dict:
            del self.m_cell1.m_connector_dict[self.m_id]
        # delete the refs to those two cells
        self.m_cell0 = None
        self.m_cell1 = None

