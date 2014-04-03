#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conductor subsystem module contains main loop and majority of important classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "conductorsys.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import logging
import warnings 
import time
import daemon
import pprint
import random

# installed modules
import numpy

# local modules
import config
import oschandlers

# constants
LOGFILE = config.logfile
AVGT_SHORT = config.avg_time_short
AVGT_MED = config.avg_time_med
AVGT_LONG = config.avg_time_long

T1 = "    "
T2 = "        "
T3 = "            "

FREQ = {'regular':1, 'once':2, 'event':3, 'repeat':4, 'timed':5}

OSCPORT = config.oscport
OSCHOST = config.oschost if config.oschost else "localhost"
OSCTIMEOUT = config.osctimeout
OSCPATH = config.oscpath
OSCTYPE = config.osctype

# create logger
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=LOGFILE,level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')


# basic data elements

class Field(object):
    """An object representing the field.  """

    def __init__(self):
        # we could use a list here which would make certain things easier, but
        # we need to do deletions and references pretty regularly.
        self.m_samp = 0
        self.m_cell_dict = {}
        self.m_conx_dict = {}
        self.m_xmin = 0
        self.m_xmax = 0
        self.m_ymin = 0
        self.m_ymax = 0
        self.m_npeople = 0
        #self.allpaths = []

    def setparam(self, xmin=None,xmax=None,ymin=None,ymax=None,npeople=None):
        if xmin is not None:
            self.m_xmin = xmin
        if xmax is not None:
            self.m_xmax = xmax
        if ymin is not None:
            self.m_ymin = ymin
        if ymax is not None:
            self.m_ymax = ymax
        if npeople is not None:
            self.m_npeople = npeople

    # Cells

    def createCell(self, id):
        # create cell
        cell = Cell(id)
        # add to the cell list
        self.m_cell_dict[id] = cell

    def updateCell(self,id,x=None,y=None,vx=None,vy=None,major=None,minor=None,
                   gid=None,gsize=None):
        cell = self.m_cell_dict[id]
        cell.update(x,y,vx,vy,major,minor,gid,gsize)
        cell.calcStuff()

    def delCell(self, id):
        cell = self.m_cell_dict[id]
        # delete all connectors from master list of connectors
        for conxid in cell.m_conx_dict:
            if conxid in self.m_conx_dict:
                del self.m_conx_dict[conxid]
        # have cell disconnect all of its connections and refs
        if id in self.m_cell_dict:
            cell.cellDisconnect()
            # delete from the cell master list of cells
            del self.m_cell_dict[id]

    # Connectors

    def createConnector(self, id, cell0, cell1):
        # create connector - note we pass self since we want a back reference
        # to field instance
        # NOTE: Connector class takes care of storing the cells as well as
        # telling each of the two cells that they now have a connector
        connector = Connector(self, id, cell0, cell1)
        # add to the connector list
        self.m_conx_dict[id] = connector

    def updateConnector(self,id,somestuff):
        # TODO: Add some stuff
        connector = self.m_conx_dict[id]
        connector.update(somestuff)

    def delConnector(self,id):
        if id in self.m_conx_dict:
            # delete the connector in the cells attached to the connector
            self.m_connectior_dict[id].conxDisconnect()
            # delete from the connector list
            del self.m_conx_dict[id]

    # Distances 

    def dist_sqd(self,cell0,cell1):
        return ((cell0.m_location[0]-cell1.m_location[0])**2 + 
                (cell0.m_location[1]-cell1.m_location[1])**2)

    def calcDistances(self):
        # TODO: Implement a more efficient distance algorithm
        # http://stackoverflow.com/questions/22720864/efficiently-calculating-a-eucl
        self.distance = {}
        # ridiculously simple iterating over the arrays
        for id0,c0 in self.m_cell_dict.iteritems():
            for id1,c1 in self.m_cell_dict.iteritems():
                conxid = str(id0)+'.'+str(id1)
                conxid_ = str(id1)+'.'+str(id0)
                if c0 != c1 and not (conxid in self.distance):
                #if c0 != c1 and not (conxid in self.m_cell_dict) and \
                        #not (conxid_ in self.m_cell_dict):
                    dist = self.dist_sqd(c0,c1)
                    #print "Calculating distance",conxid,"dist:",dist
                    self.distance[conxid] = dist
                    self.distance[conxid_] = dist
                    #self.distance[str(c1.m_id)+'.'+str(c0.m_id)] = dist
                    if dist < MIN_CONX_DIST:
                        self.createConnector(conxid,c0,c1)

    # status

    def cellStatus(self,id):
        cell = self.m_cell_dict[id]
        print T1+"Cell",id
        print T2+"location: ("+str(cell.m_x)+","+str(cell.m_y)+")"
        print T2+"speednow:",cell.m_speed_now
        print T2+"avgspeed:",cell.m_speed_short,cell.m_speed_med,cell.m_speed_long
        print T2+"avgveloc:",cell.m_vel_short,cell.m_vel_med,cell.m_vel_long

    def conxStatus(self,id):
        conx = self.m_cell_dict[id]
        print T1+"Connector "+str(id)+" between cells "+str(conx.cell0)+" and "+str(conx.cell1)

    def fullStatus(self):
        print "Full Status:"
        print T1+"Frame:",self.m_samp
        for id in self.m_cell_dict:
            self.cellStatus(id)
        for id in self.m_conx_dict:
            self.conxStatus(id)


# Updates and events

class Update(object):
    """An object representing an update or report on events within the field.
    
    Parameters we can track:
    * freq - how freq update is sent out and when
    * type - event, attribute, or connection type
    * uid - user id of a person (or group)
    * gid - group id of a group
    * value - numerical value relevant to type
    * time - how long (in frames) this attribute has been set
    
    """

    def __init__(self, update_mgr, freq, type, uid=0, uid2=0, gid=0, value=0, max=0):
        self.m_update_mgr = update_mgr
        self.m_freq = freq
        self.m_type = type
        self.m_uid = uid
        self.m_uid2 = uid2
        self.m_gid = gid
        self.m_value = value
        self.m_maxcount = max
        self.m_count = 0

        self.UPDATEFUNC = {
            'artifact': self.update_artifact,
            'fromcenter': self.update_fromcenter,
            'fromothers': self.update_fromothers,
            'dance': self.update_dance,
            'speed': self.update_speed,
            'kinetic': self.update_kinetic,
            'lopside': self.update_lopside,
            'kinetic': self.update_kinetic,
            'interactive': self.update_interactive,
            'timelong': self.update_timelong,
            'biggroup1': self.update_biggroup1,
            'biggroup2': self.update_biggroup2,
            'fision': self.update_fision,
            'fusion': self.update_fusion,
            'friends': self.update_friends,
            'grouped': self.update_grouped,
            'coord': self.update_coord,
            'fof': self.update_fof,
            'leastconx': self.update_leastconx,
            'mirror': self.update_mirror,
            'nearby': self.update_nearby,
            'strangers': self.update_strangers,
            'tag': self.update_tag,
            'irlbuds': self.update_irlbuds,
            'rollcall': self.update_rollcall,
        }

    def updateUpdate(self, value):
        self.m_value = value

    def killUpdate(self):
        self.m_count = self.m_maxcount

    def sendUpdate(self):
        # for the "timed" freq, an update is sent at the start and end.
        # otherwise, we send an update everytime until the timer runs out
        # or the update is killed
        if self.m_freq == FREQ['timed'] and \
             (self.m_count != 0 and self.m_count != self.m_maxcount-1):
            return
        UPDATEFUNC[self.m_type]()

    def update_artifact(self):
        """suspected artifact
        Indication: Velocity drops to zero for several frames and other values 
            don't change either
        Interal: update sent
        OSC: /attribute,"artifact",uid,1.0,time
        """
        print OSCPATH['attribute']+',"'+OSCTYPE['attribute']+'",'+\
            str(self.m_uid)+",1.0,"+self.m_count

    def update_fromcenter(self):
        """distance from center
        Indication: Distance from geographic center of people
        Internal: Geographical center computed each frame, distance computed;
            update send
        OSC: /attribute,"fromcenter",uid,distance
        """
        pass

    def update_fromothers(self):
        """distance from others
        Indication: Distance from nearest other people
        Internal: Smallest value taken from column of distance matrix; update
            sent
        OSC: /attribute,"fromothers",uid,distance
        """
        pass

    def update_dance(self):
        """Person dancing to the music
        Indication: Motion tempo matches music tempo
        Internal: data added to person's record; update sent
        OSC: /attribute,"dance",uid,1.0,time
        """
        pass

    def update_speed(self):
        """Fast traversal
        Indication: Person has high average speed and high average velocity
        Internal: data added to person's record; update sent
        OSC: /attribute,"speed",uid,1.0,time
        """
        pass

    def update_kinetic(self):
        """Kinetic movement
        Indication: Person has high average speed and low average velocity
        Internal: data added to person's record; update sent
        OSC: /attribute,"kinetic",uid,1.0,time
        """
        pass

    def update_lopside(self):
        """unusual ratio between minor and major axis
        Indication: Person has high ratio between major and minor axis
        Internal: data added to person's record; update sent
        OSC: /attribute,"lopside",uid,1.0,time
        """
        pass

    def update_kinetic(self):
        """Stationary movement
        Indication: Person has low average speed and low average velocity
        Internal: data added to person's record; update sent
        OSC: /attribute,"kinetic",uid,0.0,time
        """
        pass

    def update_interactive(self):
        """Super interactive, lots of interaction over time
        Indication: Person has high count of interactions
        Internal: data added to person's record; update sent
        OSC: /attribute,"interactive",uid,1.0,time
        """
        pass

    def update_timelong(self):
        """Longtime in space
        Indication: Length of time in space is larger than threshold
        Internal: data added to person's record; update sent
        OSC: /attribute,"timelong",uid,1.0,time
        """
        pass

    def update_biggroup1(self):
        """Group threshold1
        Indication: Group size reaches threashold size
        Internal: update sent
        OSC: /attribute,"biggroup1",uid,1.0,time
        """
        pass

    def update_biggroup2(self):
        """Group threshold2
        Indication: Group size reaches threashold size
        Internal: update sent
        OSC: /attribute,"biggroup2",uid,1.0,time
        """
        pass

    def update_fision(self):
        """Persons increase distance during cell collision
        Indication: Centers plus radii overlap with increasing distance
        Internal: relationship data updated; connector created; update sent
        OSC: /event,"fision",uid1,uid2,1.0
        """
        pass

    def update_fusion(self):
        """Persons decrease distance during cell collision
        Indication: Centers plus radii overlap with decreasing distance
        Internal: relationship data updated; update sent
        OSC: /event,"fusion",uid1,uid2,1.0
        """
        pass

    def update_friends(self):
        """People appear to be friendly
        Indication: Stood close together for some time
        Internal: data added to person's record; new connector created; update
            sent
        notification
        OSC: /conx,"friends",uid1,uid2,1.0
        """
        pass

    def update_grouped(self):
        """People were grouped together recently
        Indication: Were part of a group together
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"grouped",uid1,uid2,1.0
        """
        pass

    def update_coord(self):
        """Coordinated movement
        Indication: Two people have similar avg speed and avg velocity
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"coord",uid1,uid2,1.0
        """
        pass

    def update_fof(self):
        """Friend of a friend
        Indication: Two people who share a connection with another
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"fof",uid1,uid2,1.0
        """
        pass

    def update_leastconx(self):
        """Least connected
        Indication: Two people who have no or the longest chain of connections
        Internal: data added to person's record; new connector created; update
            sent
        notification
        OSC: /conx,"leastconx",uid1,uid2,1.0
        """
        pass

    def update_mirror(self):
        """Coordinated movment mirrorwise
        Indication: Two people have similar avg speed and avg velocity but 
            opposite current velocity
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"mirror",uid1,uid2,1.0
        """
        pass

    def update_nearby(self):
        """Neighbors
        Indication: Two people who are merely near each other
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"nearby",uid1,uid2,1.0
        """
        pass

    def update_strangers(self):
        """Don't know each other
        Indication: No connections have been made between these people yet
        Internal: new connector created; update sent
        OSC: /conx,"strangers",uid1,uid2,1.0
        """
        pass

    def update_tag(self):
        """Possible touch or tag
        Indication: high speed approach someone, enter their space, high 
            speed withdrawl
        Internal: data added to person's record; new connector created; update
            sent
        OSC: /conx,"tag",uid1,uid2,1.0
        """
        pass

    def update_irlbuds(self):
        """In Real Life friends
        Indication: Entered field near each other
        Internal: data added to person's record; update sent
        OSC: /conx,"irlbuds",uid1,uid2,1.0
        """
        pass

    def update_rollcall(self):
        """People highlighted in field
        Indication: Depends on scene
        Internal: Conductor lists actively highlighted cells; update sent
        OSC: /rollcall [list of uids]
        """
        pass


class UpdateMgr(object):
    """An object that manages the various kinds of updates.

    Kind of updates (freq):
    * Regular updates (rollcall, fromcenter, fromothers)
        maxcount = 0
    * Report once when event happens (artifact, biggroup, empty)
        maxcount = 1
    * Event reported repeatedly until event ends (fission, fusion)
        maxcount = 0
    * Report start and repeatedly until behavior ends (fast, kinetic, artifact)
        maxcount = 0
    * Report start and when timer end (friends, groups, coord)
        maxcount = timer_value
    * Report start, when timer ends, & occ revisit (interactive, timelong, irlbuds)
        maxcount = timer_value

    """

    def __init__(self):
        self.m_active_updates = {}

    def sendAllUpdates(self):
        for i in self.m_active_updates:
            i.sendUpdate()

    def countUpdates(self):
        for i in self.m_active_updates:
            # increase the count
            m_count += 1
            # if not perpetual update and counter has reached max num
            # TODO: Double check for off-by-one errror here
            if i.m_maxcount > 0 and i.m_count >= i.m_maxcount:
                # remove update
                self.m_active_updates.remove(i)


# Basic data elements

class GraphElement(object):

    """Basic data element represented by cells and connectors.

    Stores the following values
        m_color: color of this element (DEF_LINECOLOR)
        m_leffects: list of effects

    addEffect: add an effect to the list of effects that will act on this
        object
    applyEffects: apply all the effects in the list to the arcs that make
        up this object

    """

    def __init__(self, effects=None):
        self.m_effects_list = []
        if effects is not None:
            self.m_effects_list += effects
        # TODO: init points, index, color

    def addEffects(self, effects):
        # we don't append because we might be adding multiple effects
        # and we test for None because we are OCD
        if effects is not None:
            self.m_effects_list += effects

    def delEffects(self, effect):
        if effect in self.m_effects_list:
            self.m_effects_list.remove(effect)

    def applyEffects():
        pass

    def setVisible():
        self.m_visible = True

    def setInvisible():
        self.m_visible = False

    def draw(self):
        self.m_shape.draw()


class Cell(GraphElement):

    """Represents one person/object on the floor.

    Create a cell as a subclass of the basic data element.
    
    Stores the following values:
        m_location: center of cell
        m_orient: orientation from the default (DEF_ORIENT)

    """

    def __init__(self,id,x=0,y=0,vx=0,vy=0,major=0,minor=0,gid=0,gsize=0,
                 effects=None):
        """Store basic info and create a GraphElement object"""
        # stuff we get from tracking subsys
        self.m_id = id
        self.m_x = x
        self.m_y = y
        self.m_vx = vx
        self.m_vy = vy
        self.m_major = major
        self.m_minor = minor
        self.m_gid = gid
        self.m_gsize = gsize
        # state of the cell
        self.m_visible = True
        self.m_conx_dict = {}
        # stuff we can easily calculate
        #   is it worth it to save x & y velocity separately?
        #   yes, because just the velocity vector will always be positive
        self.m_speed_short = 0   # running average speed (avg of abs value)
        self.m_speed_med = 0
        self.m_speed_long = 0
        self.m_velx_short = 0  # running average vector velocity (avg w + & -)
        self.m_vely_short = 0
        self.m_vel_short = 0
        self.m_velx_med = 0
        self.m_vely_med = 0
        self.m_vel_med = 0
        self.m_velx_long = 0
        self.m_vely_long = 0
        self.m_vel_long = 0
        
        GraphElement.__init__(self, effects)


    def update(self,x=None,y=None,vx=None,vy=None,major=None,minor=None,gid=None,gsize=None,
               effects=None):
        """Store basic info and create a GraphElement object"""
        if x is not None:
            self.m_x = x
        if y is not None:
            self.m_y = y
        if vx is not None:
            self.m_vx = vx
        if vy is not None:
            self.m_vy = vy
        if major is not None:
            self.m_major = major
        if minor is not None:
            self.m_minor = minor
        if gid is not None:
            self.m_gid = gid
        if gsize is not None:
            self.m_gsize = gsize
        if effects is not None:
            self.m_effects_list += effects

    def calcStuff(self):
        """Calculate the easy things we can calculate."""
        # running average speed - avg of abs(velocity)
        self.m_speed_now = (self.m_vx**2 + self.m_vy**2)**0.5
        self.m_speed_short = self.m_speed_short + \
                             ((self.m_speed_now-self.m_speed_short)/AVGT_SHORT+1)
        self.m_speed_med = self.m_speed_med + \
                             ((self.m_speed_now-self.m_speed_med)/AVGT_MED+1)
        self.m_speed_long = self.m_speed_long + \
                             ((self.m_speed_now-self.m_speed_long)/AVGT_LONG+1)
        # running average velocity - we keep x & y separate to keep direction
        self.m_velx_short = self.m_velx_short + \
                             ((self.m_vx-self.m_velx_short)/AVGT_SHORT+1)
        self.m_vely_short = self.m_vely_short + \
                             ((self.m_vy-self.m_vely_short)/AVGT_SHORT+1)
        self.m_vel_short = (self.m_velx_short**2 + self.m_vely_short**2)**0.5
        self.m_velx_med = self.m_velx_med + \
                             ((self.m_vx-self.m_velx_med)/AVGT_MED+1)
        self.m_vely_med = self.m_vely_med + \
                             ((self.m_vy-self.m_vely_med)/AVGT_MED+1)
        self.m_vel_med = (self.m_velx_med**2 + self.m_vely_med**2)**0.5
        self.m_velx_long = self.m_velx_long + \
                             ((self.m_vx-self.m_velx_long)/AVGT_LONG+1)
        self.m_vely_long = self.m_vely_long + \
                             ((self.m_vy-self.m_vely_long)/AVGT_LONG+1)
        self.m_vel_long = (self.m_velx_long**2 + self.m_vely_long**2)**0.5

    def addConnector(self, connector):
        self.m_conx_dict[connector.m_id] = connector

    def delConnector(self, connector):
        if connector.m_id in self.m_conx_dict:
            del self.m_conx_dict[connector.m_id]

    def cellDisconnect(self):
        """Disconnects all the connectors and refs it can reach.
        
        To actually delete it, remove it from the list of cells in the Field
        class.
        """
        print "Cell: Disconnecting",self.m_id
        # we make a copy because we can't iterate over the dict if we are
        # deleting stuff from it!
        new_connector_dict = self.m_conx_dict.copy()
        # for each connector attached to this cell...
        for connector in new_connector_dict.values():
            # OPTION: for simplicity's sake, we do the work rather than passing to
            # the object to do the work
            # delete the connector from its two cells
            if connector.m_id in connector.m_cell0.m_conx_dict:
                del connector.m_cell0.m_conx_dict[connector.m_id]
            if connector.m_id in connector.m_cell1.m_conx_dict:
                del connector.m_cell1.m_conx_dict[connector.m_id]
            # delete cells ref'd from this connector
            connector.m_cell0 = None
            connector.m_cell1 = None
            # now delete from this cell's list
            if connector.m_id in self.m_conx_dict:
                del self.m_conx_dict[connector.m_id]

            # OPTION: Let the objects do the work
            #connector.conxDisconnect()
            # we may not need this because the connector calls the same thing
            # for it's two cells, including this one
            #self.delConnector(connector)

class Connector(GraphElement):

    """Represents a connector between two cells.

    Create a connector as a subclass of the basic data element.
    
    Stores the following values:
        m_cell0, m_cell1: the two cells connected by this connector

    makeBasicShape: create the set of arcs that will define the shape

    """

    def __init__(self, field, id, cell0, cell, effects=None):
        """Store basic info and create a GraphElement object"""
        self.m_id = id
        # store the cells we are connected to
        self.m_cell0 = cell0
        self.m_cell1 = cell1
        # tell the cells themselves that they now own a connector
        cell0.addConnector(self)
        cell1.addConnector(self)
        GraphElement.__init__(self, effects)

    def conxDisconnect(self):
        """Disconnect cells this connector refs & this connector ref'd by them.
        
        To actually delete it, remove it from the list of connectors in the Field
        class.
        """
        print "Conx: Disconnecting",self.m_id,"between cells",\
                self.m_cell0.m_id,"and",self.m_cell1.m_id
        # OPTION: for simplicity's sake, we do the work rather than passing to
        # the object to do the work
        # delete the connector from its two cells
        if self.m_id in self.m_cell0.m_conx_dict:
            del self.m_cell0.m_conx_dict[self.m_id]
        if self.m_id in self.m_cell1.m_conx_dict:
            del self.m_cell1.m_conx_dict[self.m_id]
        # delete the refs to those two cells
        self.m_cell0 = None
        self.m_cell1 = None

        # OPTION: We let the objects do the work
        # delete the connector from its two cells
        #self.m_cell0.delConnector(self)
        #self.m_cell1.delConnector(self)
        # delete cells ref'd from this connector
        #self.m_cell0 = None
        #self.m_cell1 = None


if __name__ == "__main__":

    # initialize field
    field = Field()

    osc = oschandlers.OSCHandler(field)
    # simulate a "game engine"
    while osc.m_run:
        # main loop
        # call user script
        osc.each_frame()

    osc.m_server.close()
