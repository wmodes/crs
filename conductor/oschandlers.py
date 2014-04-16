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
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import sys
import time
from time import sleep

# installed modules
from OSC import OSCServer

# local modules
import config
import conductorsys

# Constants
OSCPORT = config.oscport
OSCHOST = config.oschost if config.oschost else "localhost"
OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is
# set to False
def handle_timeout(self):
    self.timed_out = True


class OSCHandler(object):

    """Set up OSC server and other handlers."""

    def __init__(self, field):
        self.m_field = field
        self.m_server = OSCServer( (OSCHOST, OSCPORT) )
        self.m_server.timeout = OSCTIMEOUT
        self.m_run = True

        self.m_xmin = 0
        self.m_ymin = 0
        self.m_xmax = 0
        self.m_ymax = 0

        self.EVENTFUNC = {
            'ping': self.event_tracking_ping,
            'start': self.event_tracking_start,
            'stop': self.event_tracking_stop,
            'entry': self.event_tracking_entry,
            'exit': self.event_tracking_exit,
            'update': self.event_tracking_update,
            'frame': self.event_tracking_frame,
            'minx': self.event_tracking_set,
            'miny': self.event_tracking_set,
            'maxx': self.event_tracking_set,
            'maxy': self.event_tracking_set,
            'npeople': self.event_tracking_set,
        }

        # add a method to an instance of the class
        import types
        self.m_server.handle_timeout = types.MethodType(handle_timeout, self.m_server)

        for i in self.EVENTFUNC:
            self.m_server.addMsgHandler(OSCPATH[i], self.EVENTFUNC[i])

    # user script that's called by the game engine every frame
    def each_frame(self):
        # clear timed_out flag
        self.m_server.timed_out = False
        # handle all pending requests then return
        while not self.m_server.timed_out:
            self.m_server.handle_request()

    def user_callback(self, path, tags, args, source):
        # which user will be determined by path:
        # we just throw away all slashes and join together what's left
        user = ''.join(path.split("/"))
        # tags will contain 'fff'
        # args is a OSCMessage with data
        # source is where the message came from (in case you need to reply)
        #print ("Now do something with", user,args[2],args[0],1-args[1]) 

    def quit_callback(self, path, tags, args, source):
        self.m_run = False

    # Event handlers

    def event_tracking_ping(self, path, tags, args, source):
        """Ping from tracking system."""
        #print "OSC: ping:",args,source
        pass

    def event_tracking_start(self, path, tags, args, source):
        """Tracking system is starting.

        Sent before first /pf/update message for that target
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        print "OSC: start:",args

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        split = path.split("/")
        param = split.pop()
        print "OSC: set:",path,param,args,source
        if param == OSCPATH_SET_DICT['minx']:
            self.m_field.setparam(xmin=int(100*args[0]))
        elif param == OSCPATH_SET_DICT['miny']:
            self.m_field.setparam(ymin=int(100*args[0]))
        elif param == OSCPATH_SET_DICT['maxx']:
            self.m_field.setparam(xmax=int(100*args[0]))
        elif param == OSCPATH_SET_DICT['maxy']:
            self.m_field.setparam(ymax=int(100*args[0]))
        elif param == OSCPATH_SET_DICT['npeople']:
            self.m_field.setparam(npeople=args[0])
        else:
            pass

    def event_tracking_entry(self, path, tags, args, source):
        """Event when person enters field.

        Sent before first /pf/update message for that target
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since
            beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        print "OSC: entry:",args
        sample = args[0]
        time = args[1]
        id = args[2]
        self.m_field.createCell(id)

    def event_tracking_exit(self, path, tags, args, source):
        """Event when person exits field.

        args:
             samp - sample number
             t - time of sample (elapsed time in seconds since beginning of run)
             target - UID of target

        """
        print "OSC: exit:",args
        sample = args[0]
        time = args[1]
        id = args[2]
        self.m_field.delCell(id)

    def event_tracking_update(self, path, tags, args, source):
        """Information about people's movement within field.

        Update position of target.
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            x,y - position within field in units - increasing in value towards right and down
            vx,vy - estimate of velocity in m/s
            major,minor - major/minor axis size in m
            groupid - id number of group
            groupsize - number of people in group
            channel - channel number assigned

        """
        #print "OSC: update:",args
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = 0
        samp = args[0]
        time = args[1]
        id = args[2]
        x = int(100*args[3])       # comes in meters, convert to cm
        y = int(100*args[4])
        vx = int(100*args[5])
        vy = int(100*args[6])
        major = int(100*args[7]/2)
        minor = int(100*args[8]/2)
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        # TODO: if gid is not equal to 0 than we have a grouping, we need to
        # stop mapping the cell(s) that are not getting updated in new frames
        # alternately, we can just turn all cells invisible each frame and then
        # make them visible as we get an update
        #print "field.updateCell(",id,",",(x,y),",",major,")"
        self.m_field.updateCell(id,x,y,vx,vy,major,minor,gid,gsize)
        # TODO: What happens to connections when someone joins a group? Oh god.
        # In our OSC messages, when two cells become a group, a gid is assigned 
        # the groupsize is incremented, and only one of the cells gets updated
        # Like so:
        #   /pf/update 410 28.8 2 1.1 -1.4 -1.2 -0.2 nan nan 1 2 2
        #   /pf/update 410 28.8 4 0.9 -1.0 -0.2 -2.4 nan nan 1 2 4
        #   /pf/update 411 28.8 4 0.9 -1.0 nan nan nan nan 1 2 4
        #   /pf/update 412 29.0 4 0.9 -1.0 nan nan nan nan 1 2 4

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            samp - sample number

        """
        self.m_field.m_samp = args[0]
        #print "OSC: frame:",args
        self.m_field.fullStatus()

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        print "OSC: stop:",args


if __name__ == "__main__":

    field = conductorsys.Field()
    osc = OSCHandler(field)
    # simulate a "game engine"
    while osc.m_run:
        # main loop
        # call user script
        osc.each_frame()

    osc.m_server.close()
