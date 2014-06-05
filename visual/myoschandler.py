#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module that handles OSC messages.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""


__appname__ = "oschandler.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import itertools

# installed modules
# noinspection PyUnresolvedReferences
from OSC import OSCServer, OSCClient, OSCMessage
#import pyglet

# local modules
from shared.oschandler import OSCHandler
from shared import config
from shared import debug

# local Classes

# configure servers & clients properly
import socket
ip = socket.gethostbyname(socket.gethostname())
IAM = 'visual'
if ip == config.osc_ips_prod['localhost']:
    OSC_IPS = config.osc_ips_prod
    OSC_PORTS = config.osc_ports_prod
else:
    OSC_IPS = config.osc_ips_local
    OSC_PORTS = config.osc_ports_prod

# Constants

OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
REPORT_FREQ = config.report_frequency

# init debugging
dbug = debug.Debug()


class MyOSCHandler(OSCHandler):

    """Set up OSC server and other handlers."""

    def __init__(self, field):

        osc_server = []
        osc_clients = []

        # build up connection array
        for host in OSC_IPS:
            if host == IAM:
                print "System:Config server:",(host,OSC_IPS[host],
                        OSC_PORTS[host])
                osc_server = [('server', OSC_IPS[host], OSC_PORTS[host])]
            elif host == 'localhost' or host == 'default':
                continue
            else:
                print "System:Config client:",(host,OSC_IPS[host],
                        OSC_PORTS[host])
                osc_clients.append((host, OSC_IPS[host], OSC_PORTS[host]))

        self.eventfunc = {
            # from conductor
            'conduct_start': self.event_conduct_start,
            'conduct_stop': self.event_conduct_stop,
            'conduct_scene': self.event_conduct_scene,
            'conduct_rollcall': self.event_conduct_rollcall,
            'conduct_attr': self.event_conduct_attr,
            'conduct_conx': self.event_conduct_conx,
            'conduct_conxbreak': self.event_conduct_conxbreak,
            'conduct_gattr': self.event_conduct_gattr,
            'conduct_event': self.event_conduct_event,
        }

        super(MyOSCHandler, self).__init__(field, osc_server, osc_clients)

    def honey_im_home(self):
        """Broadcast a hello message to the network."""
        self.send_to_all_clients(OSCPATH['visual_start'],[])

    #
    # Conductor INCOMING
    #

    # from conductor
    def event_conduct_start(self, path, tags, args, source):
        """Conductor event: starting."""
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_start"

    def event_conduct_stop(self, path, tags, args, source):
        """Conductor event: stopping."""
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_stop"

    def event_conduct_scene(self, path, tags, args, source):
        """Conductor event: scene info.

        /conductor/scene ["scene","variant",value]
            scene: one of the following:
                "calibrate" - begin calibration process
                “empty” - begin empty field demo (usually after a time with npeople=0)
                “cellconx” - standard mode of highlighting cells and connections
                “tag” - limited highlights stolen by contact, including multiple steals
            variant: currently unused, but may specify variants of above
            value: (float) currently unused, but may specify values needed by above scenes
        """
        scene = args[0]
        variant = args[1]
        value = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_scene"
        self.m_field.update_scene(scene, variant, value)

    def event_conduct_rollcall(self, path, tags, args, source):
        """Conductor event: sending rollcall.

        /conductor/rollcall [uid,action,numconx]
            uid: UID of target
            action: either of two values
                "visible" - the person is "visible" to the system
                "hidden" - the person is not visible to the system
            numconx: The number of (visible?) connections attached to this person
        """
        uid = args[0]
        action = args[1]
        numconx = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_rollcall"
        #TODO: Don't hardcode values that should prob be in config
        self.m_field.update_cell(uid, visible=(action == 'visible'))

    def event_conduct_attr(self, path, tags, args, source):
        """Conductor event: cell attributes.

        /conductor/attr ["type",uid,value,time]
            type: one of the following:
                "dance" - Person dancing to the music
                "interactive" - Super interactive, lots of interaction over time
                etc
            uid: the UID of the target
            value: a unit value (0.0-1.0) representing the intensity of the attribute
            time: the length of time in seconds that the attribute has applied so far
        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_attr"
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        type = args[0]
        uid = args[1]
        if uid not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: 
                print "OSC:event_conduct_attr:no uid", uid, "in registered cell list"
        value = args[2]
        time = args[3]
        if self.m_field.m_frame%REPORT_FREQ['debug'] == 0:
            #print "OSC:event_track_update:",path,args,source
            if dbug.LEV & dbug.MSGS: 
                print " OSC:event_conduct_attr:uid:",uid,type,value,time
        #TODO: Deal with cid
        #TODO: Deal with 
        #self.m_field.update_conx_attr(cid, uid0, uid1, type, value)

    def event_conduct_conx(self, path, tags, args, source):
        """Conductor event: connector info.

        /conductor/conx ["type",”subtype”,cid, uid0,uid1,value,time]
            cid: connector id of the target
            type:
                persistent - joining people
                    with subtypes:
                        coord - Coordinated movement
                        fof - Friend of a friend
                        etc
                happening - evolving attribute
                    with subtypes
                        fusion - Person within fusion range
                        transfer - Highlight transfer from uid0 to uid1
            uid0: the UID of the first target
            uid1: the UID of the second target
            value: a unit value (0.0-1.0) representing the intensity of the attribute
            time: the length of time in seconds that the attribute has applied so far
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        type = args[0]
        subtype = args[1]
        cid = args[2]
        if cid not in self.m_field.m_conx_dict:
            if dbug.LEV & dbug.MSGS: 
                print "OSC:event_conduct_conx:no cid", cid, "in registered conx list"
        uid0 = args[3]
        uid1 = args[4]
        value = args[5]
        time = args[6]
        if self.m_field.m_frame%REPORT_FREQ['debug'] == 0:
            #print "OSC:event_track_update:",path,args,source
            if dbug.LEV & dbug.MSGS: 
                print " OSC:event_conduct_conx:cid:",cid,type,subtype,uid0,uid1,value
        #TODO: Deal with cid
        self.m_field.update_conx_attr(cid, uid0, uid1, subtype, value)

    def event_conduct_conxbreak(self, path, tags, args, source):
        """Conductor event: break connection.

        /conductor/conxbreak [cid,uid0,uid1]
            cid: connector id of the target
            uid0: the UID of the first target
            uid1: the UID of the second target
        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_conxbreak"
        cid = args[0]
        if cid not in self.m_field.m_conx_dict:
            if dbug.LEV & dbug.MSGS: 
                print "OSC:event_conduct_conxbreak:no cid", cid, "in registered conx list"
        uid0 = args[1]
        uid1 = args[2]
        self.m_field.del_connector(cid, uid0, uid1)

    def event_conduct_gattr(self, path, tags, args, source):
        """Conductor event: group attribute.

        /conductor/gattr ["type",gid,value,time]
            type: one of the following:
                "biggroup" - group size reaches threshold values 
                "static" - Stationary movement
                etc
            gid: the GID of the group (as provided by tracker)
            value: a unit value (0.0-1.0) representing the intensity of the attribute
            time: the length of time in seconds that the attribute has applied so far
        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_gattr"

    def event_conduct_event(self, path, tags, args, source):
        """Conductor event: discrete events.

        /conductor/event ["type",eid, uid0,uid1,value]
            eid: unique event ID
            type: one of the following:
                tag - A person just tagged someone
                contact - Extreme closeness (***)
            uid0: the UID of the first target
            uid1: the UID of the second target
            value: a unit value (0.0-1.0) representing the intensity of the effect
        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_conduct_event"

