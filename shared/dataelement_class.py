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
import config

# local classes
from debug import Debug

# constants
LOGFILE = config.logfile

DEF_RADIUS = config.default_radius
RAD_PAD = config.radius_padding     # increased radius of circle around bodies

# init debugging
dbug = Debug()

class Leg(object):
    """Represents a leg within a cell.

    Stores the following values:
         m_id: UID this leg belongs to
         m_leg: leg number (0..nlegs-1)
         m_nlegs: number of legs target is modeled with 
         m_x,m_y: position within field in cm
         m_ex,m_ey: standard error of measurement (SEM) of position, in cm
         m_spd: speed in cm/s
         m_espd: standard error of speed
         m_heading: direction of travel in degrees
         m_eheading: standard error in heading in degrees
         m_diam: diameter
         m_sigmadiam: standard error in diameter?
         m_sep: ??
         m_leftness: likelihood this is the left foot
         m_visibility: number of frames since a positive fix was found for this leg

    """

    def __init__(self, field, id, p=None, r=None):
        pass


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

    def update(self, p=None, r=None, effects=None):
        """Store basic info and create a DataElement object"""
        if p is not None:
            self.m_location = p
        if r is not None:
            self.m_body_radius = r
            self.m_radius = r*RAD_PAD
        if effects is not None:
            self.m_effects_list = effects

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

