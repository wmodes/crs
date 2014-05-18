#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conductor classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "cwconductorelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time

# installed modules

# local modules
from shared import config
from shared import debug

# local classes

# constants

LOGFILE = config.logfile

OSCPATH = config.oscpath

# init debugging
dbug = debug.Debug()


class Conductor(object):
    """An object representing the conductor.

    Stores the following values:
        m_field: store a back ref to the field that called us

    send_rollcall: send the current rollcall to concerned systems

    """

    def __init__(self, field):
        self.m_field = field
    
    # Sending information

    def send_rollcall(self):
        """Sends the currently highlighted cells via OSC.
        
        /conductor/rollcall [uid,action,numconx]
        """
        for id,cell in self.m_field.m_cell_dict.iteritems():
            if cell.m_visible:
                action = "visible"
            else:
                action = "hidded"
            #TODO: Should the connector count only show visble connectors?
            self.m_field.m_osc.send_downstream(OSCPATH('conduct_rollcall'),
                    [id, action, len(cell.m_conx_dict)])

    def send_attrs(self):
        """Sends the current attributes of visble cells.
        
        /conductor/attr ["type",uid,value,time]
        """
        for uid, cell in self.m_field.m_cell_dict.iteritems():
            if cell.m_visible:
                for type, attr in cell.m_attrs_dict.iteritems():
                    duration = time() - attr.timestamp
                    self.m_field.m_osc.send_downstream(OSCPATH('conduct_attr'),
                            [type, uid, attr.value, duration])

    def send_conxs(self):
        """Sends the current descriptions of connectors.
        
        /conductor/conx [cid,"type",uid0,uid1,value,time]
        """
        for id,conx in self.m_field.m_conx_dict.iteritems():
            if conx.m_cell0.m_visible and conx.m_cell1.m_visible:
                for type, attr in conx.m_attrs_dict.iteritems():
                    duration = time() - attr.timestamp
                    self.m_field.m_osc.send_downstream(OSCPATH('conduct_conx'),
                            [id, type, conx.cell0.m_id, conx.cell1.m_id,
                            attr.value, duration])

    def nix_cattr(self, cid, type):
        """Sends OSC messages to announce the removal of connection attr.
        
        /conductor/conx [cid,"type",uid0,uid1,0.0,time]"""
        if cid in self.m_field.m_conx_dict:
            conx = self.m_field.m_conx_dict[cid]
            if type in conx.m_attrs_dict:
                attr = conx.m_attrs_dict[type]
                duration = time() - attr.timestamp
                self.m_field.m_osc.send_downstream(OSCPATH('conduct_conx'),
                        [cid, type, conx.cell0.m_id, conx.cell1.m_id,
                        0.0, duration])

    def nix_conxs(self, cid):                
        """Sends OSC messages to announce the removal of a connection.
        
        /conductor/conxbreak [cid,uid0,uid1]
        """
        if cid in self.m_field.m_conx_dict:
            conx = self.m_field.m_conx_dict[cid]
            for type,attr in conx.m_attrs_dict.iteritems():
                duration = time() - attr.timestamp
                self.m_field.m_osc.send_downstream(OSCPATH('conduct_conx'),
                        [cid, type, conx.cell0.m_id, conx.cell1.m_id, 0.0, duration])
            self.m_field.m_osc.send_downstream(OSCPATH('conduct_conxbreak'),
                    [cid, conx.cell0.m_id, conx.cell1.m_id])

    def send_gattrs(self):
        """Sends the current attributes of visible groups.
        
        /conductor/gattr ["type",gid,value,time]
        """
        for gid,group in self.m_field.m_group_dict.iteritems():
            if group.m_visible:
                for type,attr in group.m_attrs_dict.iteritems():
                    duration = time() - attr.timestamp
                    self.m_field.m_osc.send_downstream(OSCPATH('conduct_gattr'),
                            [type, gid, attr.value, duration])

    def send_events(self):
        """Sends notification of an ongoing event.
        
        /conductor/event ["type",uid0,uid1,value,time]
        """
        for id,event in self.m_field.m_event_dict.iteritems():
            duration = time() - event.timestamp
            self.m_field.m_osc.send_downstream(OSCPATH('conduct_event'),
                    [event.m_type, event.m_uid0, event.m_uid1, event.m_value, duration])

    # 

