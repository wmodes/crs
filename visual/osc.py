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

__appname__ = "osc.py"
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
import visualsys

# Constants
OSCPORT = config.oscport
OSCHOST = config.oschost if config.oschost else "localhost"
OSCTIMEOUT = config.osctimeout
OSCPATH_START = config.oscpath_start
OSCPATH_ENTRY = config.oscpath_entry
OSCPATH_EXIT = config.oscpath_exit
OSCPATH_UPDATE = config.oscpath_update
OSCPATH_FRAME = config.oscpath_frame
OSCPATH_STOP = config.oscpath_stop
OSCPATH_SET = config.oscpath_set
OSCPATH_SET_DICT = config.oscpath_set_dict

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

        # add a method to an instance of the class
        import types
        self.m_server.handle_timeout = types.MethodType(handle_timeout, self.m_server)

        self.m_server.addMsgHandler(OSCPATH_START, self.event_tracking_start)
        self.m_server.addMsgHandler(OSCPATH_ENTRY, self.event_tracking_entry)
        self.m_server.addMsgHandler(OSCPATH_EXIT, self.event_tracking_exit)
        self.m_server.addMsgHandler(OSCPATH_UPDATE, self.event_tracking_update)
        self.m_server.addMsgHandler(OSCPATH_FRAME, self.event_tracking_frame)
        self.m_server.addMsgHandler(OSCPATH_STOP, self.event_tracking_stop)
        for post in OSCPATH_SET_DICT:
            self.m_server.addMsgHandler(OSCPATH_SET+OSCPATH_SET_DICT[post],
                                        self.event_tracking_set)

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
        print ("Now do something with", user,args[2],args[0],1-args[1]) 

    def quit_callback(self, path, tags, args, source):
        # don't do this at home (or it'll quit blender)
        self.m_run = False

    # Event handlers

    def event_tracking_start(self, path, tags, args, source):
        """Tracking system is starting.

        Sent before first /pf/update message for that target
        args:
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        print "OSC start:",path,args,source

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        split = path.split("/")
        param = split.pop()
        print "OSC set:",path,param,args,source
        if param == OSCPATH_SET_DICT['minx']:
            self.m_xmin = int(100*args[0])
        elif param == OSCPATH_SET_DICT['miny']:
            self.m_ymin = int(100*args[0])
        elif param == OSCPATH_SET_DICT['maxx']:
            self.m_xmax = int(100*args[0])
        elif param == OSCPATH_SET_DICT['maxy']:
            self.m_ymax = int(100*args[0])
        elif param == OSCPATH_SET_DICT['npeople']:
            pass
        else:
            pass
        print "setting xmin:",self.m_xmin,"ymin:",self.m_ymin,"xmax:",self.m_xmax,"ymax:",self.m_ymax
        if self.m_xmin and self.m_ymin and self.m_xmax and self.m_ymax:
            print "updateScaling(",(self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            self.m_field.updateScaling((self.m_xmin,self.m_ymin),(self.m_xmax,self.m_ymax))
            self.m_field.updateScreen()
            

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
        print "OSC entry:",path,args,source
        print "args:",args,args[0],args[1],args[2]
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
        print "OSC exit:",path,args,source
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
        #print "OSC update:",path,args,source
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
        major = int(100*args[7])
        minor = int(100*args[8])
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        print "field.updateCell(",id,",",(x,y),",",major,")"
        print "field:",self.m_field
        self.m_field.updateCell(id,(x,y),major)

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            samp - sample number

        """
        print "OSC frame:",path,args,source
        pass

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        print "OSC stop:",path,args,source
        pass

if __name__ == "__main__":

    # initialize field
    field = visualsys.Field()
    # initialize pyglet 
    field.initScreen()

    def on_draw():
        start = time.clock()
        field.resetPathGrid()
        field.pathScoreCells()
        for key, connector in field.m_connector_dict.iteritems():
            connector.addPath(field.findPath(connector))
        field.m_screen.clear()
        field.renderAll()
        field.drawAll()
        #print "draw loop in",(time.clock() - start)*1000,"ms"

    field.m_screen.on_draw = on_draw
    #visualsys.pyglet.app.run()

    osc = OSCHandler(field)
    # simulate a "game engine"
    while osc.m_run:
        # do the game stuff:
        #for window in visualsys.pyglet.app.windows:
        field.m_screen.switch_to()
        field.m_screen.dispatch_events()
        field.m_screen.dispatch_event('on_draw')
        field.m_screen.flip()
        # call user script
        osc.each_frame()

    osc.m_server.close()
