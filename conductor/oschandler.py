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
from time import time

# installed modules
from OSC import OSCServer, OSCClient, OSCMessage
#import pyglet

# local modules
import config
import logging

# Constants
OSCTIMEOUT = config.osctimeout
REPORT_FREQ = config.report_frequency

# init logging
logger=logging.getLogger(__name__)

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
        self.m_downClients={}
        self.m_missingHandlers={}
        
        try:
            (name, host, port) = osc_server[0]
        except:
            logger.fatal("System:Unable to create OSC handler with server="+str(osc_server),exc_info=True)
            sys.exit(1)
        self.m_oscserver = OSCServer( (host, port) )
        logger.info( "Initializing server at %s:%s"%(host, port))
        self.m_oscserver.timeout = OSCTIMEOUT
        self.m_oscserver.print_tracebacks = True

        self.m_osc_clients = {}
        for i in range(len(osc_clients)):
            (name, host, port) = osc_clients[i]
            for j in range(i):
                (oldname, oldhost, oldport) = osc_clients[j]
                if host == oldhost and port == oldport:
                    self.m_osc_clients[name] = self.m_osc_clients[oldname]
                    logger.warning( "%s same as %s"%(name,oldname))
                    break
            if not name in self.m_osc_clients:
                try:
                    self.m_osc_clients[name] = OSCClient()
                except:
                    logger.error( "Unable to create OSC handler for client %s at %s:%s"%(name,host,port),exc_info=True)
                self.m_osc_clients[name].connect( (host, port) )
                logger.info( "Connecting to %s at %s:%s"%(name,host,port))
            self.send_to(name,"/ping",[0])

        self.m_xmin = 0
        self.m_ymin = 0
        self.m_xmax = 0
        self.m_ymax = 0

        # common
        self.m_oscserver.addMsgHandler("/ping",self.event_ping)
        self.m_oscserver.addMsgHandler( "/ack",self.event_ack)

        # from tracker
        self.m_oscserver.addMsgHandler("/pf/started",self.event_tracking_start)
        self.m_oscserver.addMsgHandler("/pf/stopped",self.event_tracking_stop)
        self.m_oscserver.addMsgHandler("/pf/entry",self.event_tracking_entry)
        self.m_oscserver.addMsgHandler("/pf/exit",self.event_tracking_exit)
        self.m_oscserver.addMsgHandler("/pf/frame",self.event_tracking_frame)
        self.m_oscserver.addMsgHandler("/pf/set/minx",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/miny",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/maxx",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/maxy",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/npeople",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/groupdist",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/ungroupdist",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/set/fps",self.event_tracking_set)
        self.m_oscserver.addMsgHandler("/pf/update",self.event_tracking_update)
        self.m_oscserver.addMsgHandler("/pf/leg",self.event_tracking_leg)
        self.m_oscserver.addMsgHandler("/pf/body",self.event_tracking_body)
        self.m_oscserver.addMsgHandler("/pf/group",self.event_tracking_group)
        self.m_oscserver.addMsgHandler("/pf/geo",self.event_tracking_geo)

        # add a method to an instance of the class
        self.m_oscserver.handle_timeout = types.MethodType(handle_timeout, 
                                                           self.m_oscserver)

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
        logger.debug("user_callback( "+str(user)+" "+str(tags)+" "+str(args)+" "+str(source))

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
            if args:
                logger.debug( "Send to %s: %s %s" % (clientkey,path,args))
        except:
            lastError=self.m_downClients.get(clientkey,0)
            if time()-lastError >30:
                logger.warning("send_to: Unable to reach host %s (will suppress this warning for 30 seconds)"%(clientkey),exc_info=False)
                self.m_downClients[clientkey]=time()
            return False
        return True

    def send_laser(self, path, args):
        """Send OSC Message to one client."""
        self.send_to('laser', path, args)
        self.send_to('recorder', path, args)

    def send_downstream(self, path, args):
        """Send OSC Message to one client."""
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
        if not self.m_missingHandlers.get(path,False):
            logger.warning( "default_handler:No handler registered for "+path)
            self.m_missingHandlers[path]=True
        return None

    def event_ping(self, path, tags, args, source):
        if len(args)<1:
            # Possibly ping from touchosc which doesn't include code
            return
        ping_code = args[0]
        source_ip = source[0]
        logger.debug( "ping from %s:code:%s" % (source_ip, ping_code))
        for clientkey, client in self.m_osc_clients.iteritems():
            target_ip = client.address()[0]
            if target_ip == source_ip:
                try:
                    self.sendto(clientkey, "/ack", ping_code)
                except:
                    logger.warning("event_ping:unable to ack to "+str(clientkey),exc_info=False)

    def event_ack(self, path, tags, args, source):
        logger.debug( "event_ack:code "+str(args[0]))
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
        logger.info( "event_track_start")

    def event_tracking_set(self, path, tags, args, source):
        """Tracking subsystem is setting params.

        Send value of various parameters.
        args:
            minx, miny, maxx, maxy - bounds of PF in units
            npeople - number of people currently present

        """
        logger.debug( "event_track_set:"+str(path)+" "+str(args)+" "+str(source))
        if path =="/pf/set/minx":
            self.m_xmin = args[0]
        elif path == "/pf/set/miny":
            self.m_ymin = args[0]
        elif path == "/pf/set/maxx":
            self.m_xmax = args[0]
        elif path == "/pf/set/maxy":
            self.m_ymax = args[0]
        elif path == "/pf/set/npeople":
            self.m_field.check_people_count(args[0])
        elif path == "/pf/set/groupdist":
            self.m_field.update(groupdist=args[0])
        elif path == "/pf/set/ungroupdist":
            self.m_field.update(ungroupdist=args[0])
        elif path == "/pf/set/fps":
            self.m_field.update(oscfps=args[0])
            

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
        #print "event_track_entry:",path,args,source
        #print "args:",args,args[0],args[1],args[2]
        frame = args[0]
        time = args[1]
        id = args[2]
        logging.getLogger("cells").info("entry of cell "+str(id))
        self.m_field.create_cell(id)

    def event_tracking_exit(self, path, tags, args, source):
        """Event when person exits field.

        args:
             frame - frame number
             t - time of frame (elapsed time in seconds since beginning of run)
             target - UID of target

        """
        #print "event_track_exit:",path,args,source
        frame = args[0]
        time = args[1]
        id = args[2]
        logging.getLogger("cells").info("exit of cell "+str(id))
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
            logger.info( "event_track_body:no uid "+str(id)+" in registered cell list")
        if frame%REPORT_FREQ['debug'] == 0:
            logger.debug(" ".join(map(str,[ "    event_track_body:id:",id,"pos:", (x, y), "data:", \
                        ex, ey, spd, espd, facing, efacing, diam, sigmadiam, \
                        sep, sigmasep, leftness, vis])))
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
            logger.info( "event_track_leg:no uid "+str(id)+" in registered cell list")
        if frame%REPORT_FREQ['debug'] == 0:
            logger.debug(" ".join(map(str,["    event_track_leg:id:", id, "leg:", leg, "pos:", (x,y), \
                "data:", ex, ey, spd, espd, heading, eheading, vis])))
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
            logger.info( "event_track_update:no uid "+str(id)+" in registered cell list")
        x = args[3]       # comes in meters
        y = args[4]
        vx = args[5]
        vy = args[6]
        major = args[7]
        minor = args[8]
        gid = args[9]
        gsize = args[10]
        channel = args[11]
        #print "event_track_update:",path,args,source
        if frame%REPORT_FREQ['debug'] == 0:
            #print "event_track_update:",path,args,source
            logger.debug(" ".join(map(str,[ " event_track_update:id:",id,"pos:", (x, y), "data:", \
                        vx, vy, major, minor, gid, gsize])))
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
            logger.info( "event_track_group:no gid "+str(gid)+" in group list")
#        if frame%REPORT_FREQ['debug'] == 0:
        logger.debug(" ".join(map(str,["    event_track_group:gid:",gid, "pos:", (x, y), "data:",gsize, duration, diam])))
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
            logger.info("event_track_geo:no uid "+str(uid)+" in registered cell list")
        if frame%REPORT_FREQ['debug'] == 0:
            logger.debug(" ".join(map(str,["    event_track_geo:uid:",uid, "data:", \
                        fromcenter, fromnearest, fromexit])))
        self.m_field.update_geo(uid, fromcenter, fromnearest, fromexit)

    def event_tracking_frame(self, path, tags, args, source):
        """New frame event.

        args:
            frame - frame number
        """
        #print "event_track_frame:",path,args,source
        frame = args[0]
        self.m_field.update(frame=frame)
        if frame%REPORT_FREQ['debug'] == 0:
            logger.debug( "event_track_frame::"+str(frame))
        return None

    def event_tracking_stop(self, path, tags, args, source):
        """Tracking has stopped."""
        logger.info(" ".join(map(str,["event_tracking_stop: ",path,args,source])))
        return None

if __name__ == "__main__":
        
    from field import MyField

    # initialize field
    field = Field()
    #field.init_screen()

    #osc = OSCHandler(field)

    keep_running = True
    while keep_running:

        # call user script
        osc.each_frame()
        keep_running = osc.m_run and field.m_still_running

    osc.m_oscserver.close()
