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
import types

# installed modules
from OSC import OSCServer, OSCClient, OSCMessage
#import pyglet

# local modules
from shared import config
from shared import debug

# local Classes

# Constants

OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
REPORT_FREQ = config.report_frequency

# init debugging
dbug = debug.Debug()

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is
# set to False
def handle_timeout(self):
    self.timed_out = True

class OSCHandler(object):

    """Set up OSC server and other handlers."""

    def __init__(self, osc_server, osc_clients, field=None):
        self.m_field = field
        self.m_run = True

        try:
            (name, host, port) = osc_server[0]
        except:
            print "System:Unable to create OSC handler with server=",osc_server
            sys.exit(1)
        self.m_oscserver = OSCServer( (host, port) )
        print "System:init server: %s:%s"%(host, port)
        self.m_oscserver.timeout = OSCTIMEOUT
        self.m_oscserver.print_tracebacks = True

        self.m_osc_clients = {}
        for i in range(len(osc_clients)):
            (name, host, port) = osc_clients[i]
            for j in range(i):
                (oldname, oldhost, oldport) = osc_clients[j]
                if host == oldhost and port == oldport:
                    self.m_osc_clients[name] = self.m_osc_clients[oldname]
                    print "System:init %s:same as %s"%(name,oldname)
                    break
            if not name in self.m_osc_clients:
                try:
                    self.m_osc_clients[name] = OSCClient()
                except:
                    print "System:Unable to create OSC handler with client=",(name,host,port)
                self.m_osc_clients[name].connect( (host, port) )
                print "System:init %s: %s:%s"%(name,host,port)
            self.send_to(name,OSCPATH['ping'],[0])

        self.m_xmin = 0
        self.m_ymin = 0
        self.m_xmax = 0
        self.m_ymax = 0

        """
        self.eventfunc = update({
            # common
            'ping': self.event_ping,
            'ack': self.event_ack,
        })
        """

        self.eventfunc.update({
            # common
            'ping': self.event_ping,
            'ack': self.event_ack,

            # from tracker
            'track_start': self.event_tracking_start,
            'track_stop': self.event_tracking_stop,
            'track_entry': self.event_tracking_entry,
            'track_exit': self.event_tracking_exit,
            'track_frame': self.event_tracking_frame,
            'track_minx': self.event_tracking_set,
            'track_miny': self.event_tracking_set,
            'track_maxx': self.event_tracking_set,
            'track_maxy': self.event_tracking_set,
            'track_npeople': self.event_tracking_set,
            'track_groupdist': self.event_tracking_set,
            'track_ungroupdist': self.event_tracking_set,
            'track_fps': self.event_tracking_set,
            'track_update': self.event_tracking_update,
            'track_leg': self.event_tracking_leg,
            'track_body': self.event_tracking_body,
            'track_group': self.event_tracking_group,
            'track_geo': self.event_tracking_geo,
        })

        # add a method to an instance of the class
        self.m_oscserver.handle_timeout = types.MethodType(handle_timeout, 
                                                           self.m_oscserver)

        # How to make this match partial paths? 
        # Esp /ui/cond/type/param match /ui/cond/
        for i in self.eventfunc:
            self.m_oscserver.addMsgHandler(OSCPATH[i], self.eventfunc[i])

        # We are enumerating paths
        # Esp /ui/cond/type/param match /ui/cond/
        try:
            for path in self.eventfunc_enum:
                self.m_oscserver.addMsgHandler(path, self.eventfunc_enum[path])
        except NameError:
            pass

        # this registers a 'default' handler (for unmatched messages), 
        # an /'error' handler, an '/info' handler.
        # And, if the client supports it, a '/subscribe' &
        # '/unsubscribe' handler
        self.m_oscserver.addDefaultHandlers()
        self.m_oscserver.addMsgHandler("default", self.default_handler)
        # TODO: Handle errors from OSCServer
        #self.m_oscserver.addErrorHandlers()
        #self.m_oscserver.addMsgHandler("error", self.default_handler)
        self.honey_im_home()

    def each_frame(self):
        # clear timed_out flag
        self.m_oscserver.timed_out = False
        # handle all pending requests then return
        while not self.m_oscserver.timed_out:
            self.m_oscserver.handle_request()

    def user_callback(self, path, tags, args, source):
        # which user will be determined by path:
        # we just throw away all slashes and join together what's left
        user = ''.join(path.split("/"))
        # tags will contain 'fff'
        # args is a OSCMessage with data
        # source is where the message came from (in case you need to reply)
        if dbug.LEV & dbug.MSGS: print ("Now do something with", user,args[2],args[0],1-args[1]) 

    def quit_callback(self, path, tags, args, source):
        # don't do this at home (or it'll quit blender)
        self.m_run = False

    #
    # General OUTGOING
    #

    def send_to(self, clientkey, path, args):
        """Send OSC Message to one client."""
        try:
            self.m_osc_clients[clientkey].send(OSCMessage(path,args))
            if (dbug.LEV & dbug.MSGS) and args:
                print "OSC:Send to %s: %s %s" % (clientkey,path,args)
        except:
            if dbug.LEV & dbug.MSGS:
                print "OSC:Send:Unable to reach host",clientkey
            return False
        return True

    def send_laser(self, path, args):
        """Send OSC Message to one client."""
        self.send_to('laser', path, args)
        self.send_to('recorder', path, args)

    def send_downstream(self, path, args):
        """Send OSC Message to one client."""
        self.send_to('visual', path, args)
        self.send_to('sound', path, args)
        self.send_to('recorder', path, args)
        self.send_to('laser', path, args)

    def send_to_all_clients(self, path, args):
        """Broadcast to all the clients."""
        for clientkey, client in self.m_osc_clients.iteritems():
            self.send_to(clientkey, path, args)

    def honey_im_home(self):
        """Broadcast a hello message to the network."""
        pass

    #
    # General INCOMING
    #

    def default_handler(self, path, tags, args, source):
        if dbug.LEV & dbug.MORE: print "OSC:default_handler:No handler registered for ", path
        return None

    def event_ping(self, path, tags, args, source):
        if len(args)<1:
            # Possibly ping from touchosc which doesn't include code
            return
        ping_code = args[0]
        source_ip = source[0]
        if dbug.LEV & dbug.MSGS:
            print "OSC:ping from %s:code:%s" % (source_ip, ping_code)
        for clientkey, client in self.m_osc_clients.iteritems():
            target_ip = client.address()[0]
            if target_ip == source_ip:
                try:
                    self.sendto(clientkey, OSCPATH('ack'), ping_code)
                except:
                    if dbug.LEV & dbug.MSGS:
                        print "OSC:event_ping:unable to ack to", clientkey

    def event_ack(self, path, tags, args, source):
        if dbug.LEV & dbug.MSGS: print "OSC:event_ack:code",args[0]
        return None

    #
    # Tracking INCOMING
    #

    def event_tracking_start(self, path, tags, args, source):
        """Tracking system is starting.

        Sent before first /pf/update message for that target
        args:
            no args

        """
        #frame = args[0]
        if dbug.LEV & dbug.MSGS: print "OSC:event_track_start"

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        if dbug.LEV & dbug.MSGS: print "OSC:event_track_set:",path,args,source
        if path == OSCPATH['track_minx']:
            self.m_xmin = args[0]
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmin_field=(self.m_xmin,self.m_field.m_ymin_field))
        elif path == OSCPATH['track_miny']:
            self.m_ymin = args[0]
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmin_field=(self.m_field.m_xmin_field,self.m_ymin))
        elif path == OSCPATH['track_maxx']:
            self.m_xmax = args[0]
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmax_field=(self.m_xmax,self.m_field.m_ymax_field))
        elif path == OSCPATH['track_maxy']:
            self.m_ymax = args[0]
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_set:set_scaling(",\
                    (self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            # we might not have everything yet, but we udate with what we have
            self.m_field.set_scaling(pmax_field=(self.m_field.m_xmax_field,self.m_ymax))
        elif path == OSCPATH['track_npeople']:
            self.m_field.check_people_count(args[0])
            return
        elif path == OSCPATH['track_groupdist']:
            self.m_field.update(groupdist=args[0])
            return
        elif path == OSCPATH['track_ungroupdist']:
            self.m_field.update(ungroupdist=args[0])
            return
        elif path == OSCPATH['track_fps']:
            self.m_field.update(oscfps=args[0])
            return
        #if self.m_xmin and self.m_ymin and self.m_xmax and self.m_ymax:
            #print "set_scaling(",(self.m_xmin,self.m_ymin),",",(self.m_xmax,self.m_ymax),")"
            #self.m_field.set_scaling((self.m_xmin,self.m_ymin),(self.m_xmax,self.m_ymax))
            #self.m_field.updateScreen()
            

    def event_tracking_entry(self, path, tags, args, source):
        """Event when person enters field.

        Sent before first /pf/update message for that target
        args:
            frame - frame number
            t - time of frame (elapsed time in seconds since
            beginning of run)
            target - UID of target
            channel - channel number assigned
        """
        #print "OSC:event_track_entry:",path,args,source
        #print "args:",args,args[0],args[1],args[2]
        frame = args[0]
        time = args[1]
        id = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_track_entry:cell:",id
        self.m_field.create_cell(id)

    def event_tracking_exit(self, path, tags, args, source):
        """Event when person exits field.

        args:
             frame - frame number
             t - time of frame (elapsed time in seconds since beginning of run)
             target - UID of target

        """
        #print "OSC:event_track_exit:",path,args,source
        frame = args[0]
        time = args[1]
        id = args[2]
        if dbug.LEV & dbug.MSGS: print "OSC:event_track_exit:cell:",id
        #print "BEFORE: cells:",self.m_field.m_cell_dict
        #print "BEFORE: conx:",self.m_field.m_conx_dict
        self.m_field.del_cell(id)
        #print "AFTER: cells:",self.m_field.m_cell_dict
        #print "AFTER: conx:",self.m_field.m_conx_dict

    def event_tracking_body(self, path, tags, args, source):
        """Information about people's movement within field.

        Update position of target.
        args:
            frame - frame number 
            target - UID of target
            x,y - position of person within field in m
            ex,ey - standard error of measurement (SEM) of position, in meters 
            spd, heading - estimate of speed of person in m/s, heading in degrees
            espd, eheading - SEM of spd, heading
            facing - direction person is facing in degees
            efacing - SEM of facing direction
            diam - estimated mean diameter of legs
            sigmadiam - estimated sigma (sqrt(variance)) of diameter
            sep - estimated mean separation of legs
            sigmasep - estimated sigma (sqrt(variance)) of sep
            leftness - measure of how likely leg 0 is the left leg
            visibility - number of frames since a fix was found for either leg
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        frame = args[0]
        id = args[1]
        x = args[2]       # comes in meters
        y = args[3]
        ex = args[4]
        ey = args[5]
        spd = args[6]
        heading = args[7]
        espd = args[8]
        eheading = args[9]
        facing = args[10]
        efacing = args[11]
        diam = args[12]
        sigmadiam = args[13]
        sep = args[14]
        sigmasep = args[15]
        leftness = args[16]
        vis = args[17]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_body:no uid",id,"in registered cell list"
        if frame%REPORT_FREQ['debug'] == 0:
            if dbug.LEV & dbug.MSGS: 
                print "    OSC:event_track_body:id:",id,"pos:", (x, y), "data:", \
                        ex, ey, spd, espd, facing, efacing, diam, sigmadiam, \
                        sep, sigmasep, leftness, vis
        self.m_field.update_body(id, x, y, ex, ey, spd, espd, facing, efacing, 
                           diam, sigmadiam, sep, sigmasep, leftness, vis)

    def event_tracking_leg(self, path, tags, args, source):
        """Information about individual leg movement within field.

        Update position of leg.
        args:
            frame - frame number 
            id - UID of target
            leg - leg number (0..nlegs-1)
            nlegs - number of legs target is modeled with 
            x,y - position within field in m
            ex,ey - standard error of measurement (SEM) of position, in meters 
            spd, heading - estimate of speed of leg in m/s, heading in degrees
            espd, eheading - SEM of spd, heading
            visibility - number of frames since a positive fix
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        frame = args[0]
        id = args[1]
        leg = args[2]
        nlegs = args[3]
        x = args[4]       # comes in meters
        y = args[5]
        ex = args[6]
        ey = args[7]
        spd = args[8]
        heading = args[9]
        espd = args[10]
        eheading = args[11]
        vis = args[12]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_leg:no uid",id,"in registered cell list"
        if frame%REPORT_FREQ['debug'] == 0:
            if dbug.LEV & dbug.MSGS: 
                print "    OSC:event_track_leg:id:", id, "leg:", leg, "pos:", (x,y), \
                "data:", ex, ey, spd, espd, heading, eheading, vis
        self.m_field.update_leg(id, leg, nlegs, x, y, ex, ey, spd, espd, 
                                   heading, eheading, vis)

    def event_tracking_update(self, path, tags, args, source):
        """Information about people's movement within field.

        Update position of target.
        args:
            /pf/update frame t target x y vx vy major minor groupid groupsize channel
                frame - frame number
                t - time of frame (elapsed time in seconds)
                target - UID of target, always increments
                x,y - position within field in meters
                vx,vy - estimate of velocity in m/s
                major,minor - major/minor axis size in m
                groupid - id number of group (0 if not in any group)
                groupsize - number of people in group (including this person)
                channel - channel number assigned
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        frame = args[0]
        time = args[1]
        id = args[2]
        if id not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_update:no uid",id,"in registered cell list"
        x = args[3]       # comes in meters
        y = args[4]
        vx = args[5]
        vy = args[6]
        major = args[7]
        minor = args[8]
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        #print "OSC:event_track_update:",path,args,source
        if frame%REPORT_FREQ['debug'] == 0:
            #print "OSC:event_track_update:",path,args,source
            if dbug.LEV & dbug.MSGS: 
                print " OSC:event_track_update:id:",id,"pos:", (x, y), "data:", \
                        vx, vy, major, minor, gid, gsize
        self.m_field.update_cell(id, x, y, vx, vy, major, minor, gid, gsize, 
                                 frame=frame)

    def event_tracking_group(self, path, tags, args, source):
        """Information about people's movement within field.

        Update info about group
        /pf/group frame gid gsize duration centroidX centroidY diameter
        args:
            frame - frame number
            gid - group ID 
            gsize - number of people in group
            duration - time since first formed in seconds
            centroidX, centroidY - location of centroid of group
            diameter - current diameter (mean distance from centroid)
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        frame = args[0]
        gid = args[1]
        gsize = args[2]       # comes in meters
        duration = args[3]
        x = args[4]
        y = args[5]
        diam = args[6]
        if gid not in self.m_field.m_group_dict:
            if dbug.LEV & dbug.MSGS: print "OSC:event_track_group:no gid",gid,"in group list"
        if frame%REPORT_FREQ['debug'] == 0:
            if dbug.LEV & dbug.MSGS: 
                print "    OSC:event_track_group:gid:",gid, "pos:", (x, y), "data:", \
                        gsize, duration, diam
        self.m_field.update_group(gid, gsize, duration, x, y, diam)

    def event_tracking_geo(self, path, tags, args, source):
        """Information about people's movement within field.

        Update info about group
        /pf/geo frame target fromcenter fromothers fromexit
        args:
            frame - frame number 
            uid - UID of target
            fromcenter -target's distance from geographic center of everyone
            fromnearest - target's distance from the nearest other person (-1 if nobody else)
            fromexit - This person's distance from nearest exit from tracked area
        """
        for index, item in enumerate(args):
            if item == 'nan':
                args[index] = None
        frame = args[0]
        uid = args[1]
        fromcenter = args[2]       # comes in meters
        fromnearest = args[3]
        fromexit = args[4]
        if uid not in self.m_field.m_cell_dict:
            if dbug.LEV & dbug.MSGS: 
                print "OSC:event_track_geo:no uid",uid,"in registered cell list"
        if frame%REPORT_FREQ['debug'] == 0:
            if dbug.LEV & dbug.MSGS: 
                print "    OSC:event_track_geo:uid:",uid, "data:", \
                        fromcenter, fromnearest, fromexit
        self.m_field.update_geo(uid, fromcenter, fromnearest, fromexit)

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            frame - frame number
        """
        #print "OSC:event_track_frame:",path,args,source
        frame = args[0]
        self.m_field.update(frame=frame)
        if frame%REPORT_FREQ['debug'] == 0:
            #print "OSC:event_track_update:",frame
            if dbug.LEV & dbug.MSGS: print "    OSC:event_track_frame::",frame
        return None

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        if dbug.LEV & dbug.MSGS: print "OSC:event_track_stop:",path,args,source
        return None

if __name__ == "__main__":
        
    from myfieldelements import MyField

    # initialize field
    field = MyField()
    #field.init_screen()

    #osc = OSCHandler(field)

    keep_running = True
    while keep_running:

        # call user script
        osc.each_frame()
        keep_running = osc.m_run and field.m_still_running

    osc.m_oscserver.close()
