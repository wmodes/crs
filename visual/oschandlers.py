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
import types

# installed modules
from OSC import OSCServer

# local modules
import config
import visualsys

# Constants
OSCPORT = config.oscport
OSCHOST = config.oschost if config.oschost else "localhost"
OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
FREQ_REG_REPORT = config.freq_regular_reports

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
        self.m_server.handle_timeout = types.MethodType(handle_timeout, self.m_server)

        for i in self.EVENTFUNC:
            self.m_server.addMsgHandler(OSCPATH[i], self.EVENTFUNC[i])

        # this registers a 'default' handler (for unmatched messages), 
        # an /'error' handler, an '/info' handler.
        # And, if the client supports it, a '/subscribe' &
        # '/unsubscribe' handler
        self.m_server.addDefaultHandlers()
        self.m_server.addMsgHandler("default", self.default_handler)
        # TODO: Handle errors from OSCServer
        #self.m_server.addErrorHandlers()
        #self.m_server.addMsgHandler("error", self.default_handler)
        self.honey_im_home()

    def honey_im_home(self):
        """Broadcast a hello message to the network."""
        # TODO: Broadcast hello message
        return True

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

    def default_handler(self, path, tags, args, source):
        #print "OSC:default_handler:No handler registered for ", path
        return None

    def event_tracking_ping(self, path, tags, args, source):
        return None

    def event_tracking_start(self, path, tags, args, source):
        """Tracking system is starting.

        Sent before first /pf/update message for that target
        args:
            [ aparently no params now]
            samp - sample number
            t - time of sample (elapsed time in seconds since beginning of run)
            target - UID of target
            channel - channel number assigned

        """
        #sample = args[0]
        #print "OSC:event_start:",sample
        print "OSC:event_start"

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        print "OSC:event_set:",path,args,source
        if path == OSCPATH['minx']:
            self.m_xmin = int(100*args[0])
            # we might not have everything yet, but we udate with what we have
            self.m_field.setScaling(pmin_field=(self.m_xmin,self.m_field.m_ymin_field))
        elif path == OSCPATH['miny']:
            self.m_ymin = int(100*args[0])
            # we might not have everything yet, but we udate with what we have
            self.m_field.setScaling(pmin_field=(self.m_field.m_xmin_field,self.m_ymin))
        elif path == OSCPATH['maxx']:
            self.m_xmax = int(100*args[0])
            # we might not have everything yet, but we udate with what we have
            self.m_field.setScaling(pmax_field=(self.m_xmax,self.m_field.m_ymax_field))
        elif path == OSCPATH['maxy']:
            self.m_ymax = int(100*args[0])
            # we might not have everything yet, but we udate with what we have
            self.m_field.setScaling(pmax_field=(self.m_field.m_xmax_field,self.m_ymax))
        elif path == OSCPATH['npeople']:
            self.m_field.checkPeopleCount(args[0])
        print "setScaling(",(self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
        # we used to resize the screen, not we just rescale the action within
        # the screen
        #self.m_field.setScreen()
        """if self.m_xmin and self.m_ymin and self.m_xmax and self.m_ymax:
            print "setScaling(",(self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            self.m_field.setScaling((self.m_xmin,self.m_ymin),(self.m_xmax,self.m_ymax))
            self.m_field.updateScreen()"""
            

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
        #print "OSC:event_entry:",path,args,source
        #print "args:",args,args[0],args[1],args[2]
        sample = args[0]
        time = args[1]
        id = args[2]
        print "OSC:event_entry:cell:",id
        self.m_field.createCell(id)

    def event_tracking_exit(self, path, tags, args, source):
        """Event when person exits field.

        args:
             samp - sample number
             t - time of sample (elapsed time in seconds since beginning of run)
             target - UID of target

        """
        #print "OSC:event_exit:",path,args,source
        sample = args[0]
        time = args[1]
        id = args[2]
        print "OSC:event_exit:cell:",id
        #print "BEFORE: cells:",self.m_field.m_cell_dict
        #print "BEFORE: conx:",self.m_field.m_connector_dict
        self.m_field.delCell(id)
        #print "AFTER: cells:",self.m_field.m_cell_dict
        #print "AFTER: conx:",self.m_field.m_connector_dict

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
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = 0
        sample = args[0]
        time = args[1]
        id = args[2]
        # TODO: Create cell if we don't have a record of it
        # TODO: If npeople doesn't match our record of how many people, we drop
        # them all and let the above functionality handle them
        if id not in self.m_field.m_cell_dict:
            print "Error: no id",id,"in registered id list"
            return False
        x = int(100*args[3])       # comes in meters, convert to cm
        y = int(100*args[4])
        vx = int(100*args[5])
        vy = int(100*args[6])
        major = int(100*args[7]/2)
        minor = int(100*args[8]/2)
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        #print "OSC:event_update:",path,args,source
        if sample%FREQ_REG_REPORT == 0:
            #print "OSC:event_update:",path,args,source
            print "    OSC:event_update:id:",id,"pos:",(x,y),"axis:",major
        # TODO: if gid is not equal to 0 than we have a grouping, we need to
        # stop mapping the cell(s) that are not getting updated in new frames
        # alternately, we can just turn all cells invisible each frame and then
        # make them visible as we get an update
        #print "field.updateCell(",id,",",(x,y),",",major,")"
        self.m_field.updateCell(id,(x,y),major)
        # TODO: What happens to connections when someone joins a group? Oh god.
        # In our OSC messages, when two cells become a group, a gid is assigned 
        # the groupsize is incremented, and only one of the cells gets updated
        # Like so:
        #   /pf/update 410 28.8 2 1.1 -1.4 -1.2 -0.2 nan nan 1 2 2
        #   /pf/update 410 28.8 4 0.9 -1.0 -0.2 -2.4 nan nan 1 2 4
        #   /pf/update 411 28.8 4 0.9 -1.0 nan nan nan nan 1 2 4
        #   /pf/update 412 29.0 4 0.9 -1.0 nan nan nan nan 1 2 4
        #print "OSC:event_update: Done"

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            samp - sample number

        """
        #print "OSC:event_frame:",path,args,source
        sample = args[0]
        if sample%FREQ_REG_REPORT == 0:
            #print "OSC:event_update:",path,args,source
            print "    OSC:event_frame::",sample
        return None

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        print "OSC:event_stop:",path,args,source
        return None

if __name__ == "__main__":
        
    # initialize field
    field = visualsys.Field()
    # initialize pyglet 
    field.initScreen()

    # pyglet stuff
    #visualsys.pyglet.app.run()

    osc = OSCHandler(field)

    keep_running = True
    while keep_running:

        visualsys.pyglet.clock.tick()

        for window in visualsys.pyglet.app.windows:
            window.switch_to()
            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()

        # do all the things
        #field.on_cycle()
        # call user script
        osc.each_frame()
        keep_running = osc.m_run and field.m_still_running

    osc.m_server.close()
