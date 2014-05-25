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


__appname__ = "oschandlers.py"
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules
# noinspection PyUnresolvedReferences
from OSC import OSCServer, OSCClient, OSCMessage
#import pyglet

# local modules
from shared.oschandlers import OSCHandler
from shared import config
from shared import debug

# local Classes

# Constants
OSCSERVERHOST = config.osc_visual_host \
    if config.osc_visual_host else config.osc_default_host
OSCSERVERPORT = config.osc_visual_port \
    if config.osc_visual_port else config.osc_default_port

OSCTRACKHOST = config.osc_tracking_host \
    if config.osc_tracking_host else config.osc_default_host
OSCTRACKPORT = config.osc_tracking_port \
    if config.osc_tracking_port else config.osc_default_port

OSCSOUNDHOST = config.osc_sound_host \
    if config.osc_sound_host else config.osc_default_host
OSCSOUNDPORT = config.osc_sound_port \
    if config.osc_sound_port else config.osc_default_port

OSCCONDUCTHOST = config.osc_conductor_host \
    if config.osc_conductor_host else config.osc_default_host
OSCCONDUCTPORT = config.osc_conductor_port \
    if config.osc_conductor_port else config.osc_default_port

#OSCVISUALHOST = config.osc_visual_host \
#    if config.osc_visual_host else config.osc_default_host
#OSCVISUALPORT = config.osc_visual_port \
#    if config.osc_visual_port else config.osc_default_port

OSCLASERHOST = config.osc_laser_host \
    if config.osc_laser_host else config.osc_default_host
OSCLASERPORT = config.osc_laser_port \
    if config.osc_laser_port else config.osc_default_port

OSCRECORDERHOST = config.osc_recorder_host \
    if config.osc_recorder_host else config.osc_default_host
OSCRECORDERPORT = config.osc_recorder_port \
    if config.osc_recorder_port else config.osc_default_port

OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
REPORT_FREQ = config.report_frequency

# init debugging
dbug = debug.Debug()


class MyOSCHandler(OSCHandler):

    """Set up OSC server and other handlers."""

    def __init__(self, field):

        # build up connection array
        osc_server = [('server', OSCSERVERHOST, OSCSERVERPORT)]
        osc_clients = [
                ('tracker', OSCTRACKHOST, OSCTRACKPORT),
                ('sound', OSCSOUNDHOST, OSCSOUNDPORT),
                #('visual', OSCVISUALHOST, OSCVISUALPORT),
                ('conductor', OSCCONDUCTHOST, OSCCONDUCTPORT),
                ('laser', OSCLASERHOST, OSCLASERPORT),
                ('recorder', OSCRECORDERHOST, OSCRECORDERPORT),
            ]

        super(MyOSCHandler, self).__init__(field, osc_server, osc_clients)

    def honey_im_home(self):
        """Broadcast a hello message to the network."""
        self.send_to_all_clients(OSCPATH['visual_start'],[])
