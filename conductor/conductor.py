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
from math import sqrt
from itertools import combinations
from copy import copy

# installed modules

# local modules
from shared import config
from shared import debug

# local classes

# constants

LOGFILE = config.logfile

OSCPATH = config.oscpath

FRAMERATE = config.framerate
CONX_MIN = config.connector_avg_min
CONX_AVG = config.connector_avg_triggers
CONX_TIME = config.connector_memory_time
CONX_DIST = config.connector_distance_triggers
CONX_AGE = config.connector_max_age
CONX_LAT = config.connector_latitude

# init debugging
dbug = debug.Debug()


class Conductor(object):
    """An object representing the conductor.

    Stores the following values:
        m_field: store a back ref to the field that called us
        connector_tests: an indexed list of handlers for testing connectors
        m_avg_table: keeps an indexed list of running averages

    send_rollcall: send the current rollcall to concerned systems

    """

    def __init__(self, field):
        self.m_field = field
        self.connector_tests = {
            'grouped': self.test_grouped,
            'contact': self.test_contact,
            'friends': self.test_friends,
            'coord': self.test_coord,
            #'mirror': self.test_mirror,
            #'fof': self.test_fof,
            'irlbuds': self.test_irlbuds,
            #'leastconx': self.test_leastconx,
            #'nearby': self.test_nearby,
            #'strangers': self.test_strangers,
            #'tag': self.test_tag,
            #'chosen': self.test_chosen,
            'facing': self.test_facing,
            #'fusion': self.test_fusion,
            #'transfer': self.test_transfer,
        }
        self.m_avg_table = {}
        self.m_dist_table = {}

    def update_all_connections(self):
        """Test for and create new connections.

        iterate over all the pair combos in the cell dictionary:
          do each test and save the result
          if the avg is above the trigger
              if a connection does not exist already
                  create a connection
              else
                  update the value?
        anything else? they should be picked up when the conductor does its
        regular reports
        """

        if dbug.LEV & dbug.MORE: 
            print "Conduct:update_all_conx"
        for (cell0,cell1) in list(combinations(self.m_field.m_cell_dict.values(), 2)):
            if self.m_field.is_cell_good_to_go(cell0.m_id) and \
                    self.m_field.is_cell_good_to_go(cell1.m_id):
                # get cid
                cid = self.m_field.get_cid(cell0,cell1)
                # calc distance once
                self.m_dist_table[cid] = self.dist(cell0, cell1)
                for type,test in self.connector_tests.iteritems():
                    running_avg = test(cid, cell0, cell1)
                    if type in CONX_AVG:
                        avg_trigger = CONX_AVG[type]
                    else:
                        avg_trigger = CONX_AVG['default']
                    if dbug.LEV & dbug.COND: 
                        if running_avg and avg_trigger:
                        #if avg_trigger:
                            print "Conduct:update_conx:results:id:", \
                                    "%s-%s %.2f"%(cid,type,running_avg), \
                                    "(trigger:%.2f)"%avg_trigger
                    # if running_avg is above trigger
                    if running_avg > avg_trigger:
                        #if dbug.LEV & dbug.MORE: 
                            #print "Conduct:update_conx:results:%s-%s,%s,%s"% \
                                    #(cell0.m_id, cell1.m_id, type, running_avg)
                        # if a connection/attr does not already exist already
                        #if not self.m_field.check_for_conx_attr(cell0, cell1, type):
                        if dbug.LEV & dbug.COND: 
                            if avg_trigger:
                                print "Conduct:update_conx:triggered:id:", \
                                        "%s-%s %.2f"%(cid,type,running_avg), \
                                        "(trigger:%.2f)"%avg_trigger
                            # create one
                        self.m_field.update_conx_attr(cid, cell0.m_id,
                                cell1.m_id, type, running_avg)
                        #else:
                            #if dbug.LEV & dbug.MORE: 
                                #print "Conduct:update_conx:already there, bro"
                    # if running_avg is under trigger value 
                    else:
                        if type in CONX_AGE:
                            max_age = CONX_AGE[type]
                        else:
                            max_age = CONX_AGE['default']
                        print "KILLME:Attr not triggered:",cid,type,max_age
                        #   AND decay time is zero, kill it
                        if not max_age:
                            # send "del conx" osc msg
                            self.m_field.m_osc.nix_cattr(cid, type)
                            # delete attr and maybe conx
                            self.m_field.del_conx_attr(cid, type)
                            index = str(cid)+'-'+str(type)
                            if index in self.m_avg_table:
                                del self.m_avg_table[index]
                            if dbug.LEV & dbug.COND: 
                                print "Conduct:update_conx:delete happening:",cid,type

    def record_running_avg(self,cid,type,sample):
        """Track Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(cid)+'-'+str(type)
        if type in CONX_TIME:
            time = CONX_TIME[type]
        else:
            time = CONX_TIME['default']
        k = 1 - 1/(FRAMERATE*float(time))
        if index in self.m_avg_table:
            old_avg = self.m_avg_table[index]
        else:
            old_avg = 0
        self.m_avg_table[index] = k*old_avg + (1-k)*sample
        return self.m_avg_table[index]

    def get_running_avg(self,cid,type):
        """Retreive Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(cid)+'-'+str(type)
        if index in self.m_avg_table:
            return self.m_avg_table[index]
        self.m_avg_table[index] = 0
        return 0

    def age_and_expire_connections(self):
        """Age and expire connectors.
        
        Note that we should do this before we discover and create new
        connections. That way they are not prematurly aged.

        iterate over every connector
            iterate over ever attr
                if decay time of type is not zero (no decay)
                    if value of attr is zero or less
                        delete atrr and maybe conx
                    else
                        calculate new value based on time and decay rate
                        if new value is < 0
                            we'll set it to 0
                        record the new value

        """
        if dbug.LEV & dbug.MORE: 
            print "Conduct:age_and_expire_conx"
        #print "KILLME:",self.m_field.m_conx_dict
        new_conx_dict = copy(self.m_field.m_conx_dict)
        # iterate over every connector
        for cid,connector in new_conx_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for type,attr in new_attr_dict.iteritems():
                if type in CONX_AGE:
                    max_age = CONX_AGE[type]
                else:
                    max_age = CONX_AGE['default']
                # if decay time of type is not zero (no decay)
                if max_age:
                    # if value of attr is zero or less
                    if attr.m_value <= CONX_MIN:
                        # send "del conx" osc msg
                        self.m_field.m_osc.nix_cattr(cid, type)
                        # delete attr and maybe conx
                        self.m_field.del_conx_attr(cid, type)
                        index = str(cid)+'-'+str(type)
                        if index in self.m_avg_table:
                            del self.m_avg_table[index]
                        if dbug.LEV & dbug.COND: 
                            print "Conduct:age_and_expire_conx:Expired:",cid,type
                    # if attr still has a non-zero value
                    else:
                        # calc new value based on time and decay rate
                        since_last = time() - attr.m_timestamp
                        age = time() - attr.m_createtime
                        newvalue = attr.m_origvalue - (since_last/max_age)
                        if dbug.LEV & dbug.COND: 
                            print "Conduct:age_and_expire_conx:",cid,type,\
                                "age:",age, "since_last:",since_last,\
                                "orig:",attr.m_origvalue, "newvalue:",newvalue
                        # if new value is < 0, we'll set it to 0
                        if newvalue <= 0:
                            if dbug.LEV & dbug.COND: 
                                print "Conduct:age_and_expire_conx:Expired:",cid,type
                            newvalue = 0
                        # record the new value
                        attr.decay_value(newvalue)

    # Gather or calculate whether conditions are met for connection

    def calc_all_distances(self):
        
        # first create an indexed array of numerical indecies
        i = 0
        for cid in self.m_field.m_conx_dict.iteritems():
            pass
        # we create a numpy array of the dimensions of our number of conx
        # we use scipy.spatial.distance.cdist to calc distance between pairs

    def dist(self, cell0, cell1):
        return sqrt((cell0.m_x - cell1.m_x)**2 + (cell0.m_y - cell1.m_y)**2)

    def test_grouped(self, cid, cell0, cell1):
        """Are cells currently grouped?
        
        Evaluates the folllowing criteria
            1. whether two people are in a group
            2: how long they've been grouped
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # If the gid is not-zero and cell->m_gid the same for each cell
        if cell0.m_gid and cell0.m_gid == cell1.m_gid:
            score = 1.0
        else:
            score = 0.0
        # we record our score in our running avg table
        return self.record_running_avg(cid,'grouped',score)

    def test_friends(self, cid, cell0, cell1):
        """Are cells in proximity for some time? Pref facing each other?

        Evaluates the folllowing criteria
            1. distance between people
            2. length of time they've been close
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        # we normalize this dist where 
        #   right on top of each other would be 1.0
        #   as far as you could get would be 0.0
        if 'friends' in CONX_DIST:
            max_dist = CONX_DIST['friends']
        else:
            max_dist = CONX_DIST['default']
        score = max(0, 1 - float(dist) / max_dist)
        # we record our score in our running avg table
        return self.record_running_avg(cid,'friends',score)

    def test_contact(self, cid, cell0, cell1):
        """Are cells in contact with each other?

        Evaluates the folllowing criteria
            1. Is distance between cells < contact_dist
            2: how long they've been grouped
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        if dist < CONX_DIST['contact']:
            score = 1.0
        else:
            score = 0
        # we record our score in our running avg table
        return self.record_running_avg(cid,'contact',score)

    def test_coord(self, cid, cell0, cell1):
        """Are individuals moving in a coordinated way.

        Evaluates the folllowing criteria
            1. similarity of velocities of two cells
                Note: Empirically  10m/s is highest vel
                    so 20m/s is the largest likely diff
            2. length of time they've been synchronized
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # score = 1 if the values are exactly the same
        # score = 0 if the values are very different
        vdist = sqrt((cell0.m_vx-cell1.m_vx)**2+(cell0.m_vy-cell1.m_vy)**2)
        if 'coord' in CONX_DIST:
            max_dist = CONX_DIST['coord']
        else:
            max_dist = CONX_DIST['default']
        score = max(0, 1 - float(vdist) / max_dist)
        # we record our score in our running avg table
        return self.record_running_avg(cid,'friends',score)

    def test_fof(self, cid, cell0, cell1):
        """Are these cells connected through a third person?

        Meets the following conditions:
            1. 
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_irlbuds(self, cid, cell0, cell1):
        """Did these people come in together? Have they spent most of their
        time together?

        Evaluates the folllowing criteria
            1. distance between people
            2. length of time they've been close
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        # we normalize this dist where 
        #   right on top of each other would be 1.0
        #   as far as you could get would be 0.0
        if 'irlbuds' in CONX_DIST:
            max_dist = CONX_DIST['irlbuds']
        else:
            max_dist = CONX_DIST['default']
        score = max(0, 1 - float(dist) / max_dist)
        # we record our score in our running avg table
        return self.record_running_avg(cid,'irlbuds',score)

    def test_leastconx(self, cid, cell0, cell1):
        """Are these individuals among the least connected in the field?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_mirror(self, cid, cell0, cell1):
        """Are individuals moving in a mirrorwise way?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_nearby(self, cid, cell0, cell1):
        """Are cells near each other but not otherwise connected?

        Meets the following conditions:
            1. If cells do not share a connections
            2. If cells are not in a group with each other
            3. If dist of cells are > nearby_min and < nearby_max
        Returns:
            value: how nearby are they? 1.0 = close
        """
        # If cells do not share a connections
        for conx in cell0.m_conx_dict.values():
            if (conx.m_cell0 == cell0 and conx.m_cell1 == cell1) or \
               (conx.m_cell0 == cell1 and conx.m_cell1 == cell0):
                return 0
        # If cell->m_gid are not the same for each cell
        if cell0.m_gid == cell1.m_gid:
            return 0
        # If dist of cells are < nearby_dist
        cell_dist = self.dist(cell0, cell1)
        mindist = CONX_DIST['nearby_min']
        maxdist = CONX_DIST['nearby_max']
        if cell_dist < mindist or cell_dist > maxdist:
            return 0
        # nearby_max = 0; nearby_min = 1.0
        return 1.0 - ((cell_dist-mindist) / (maxdist-mindist))

    def test_strangers(self, cid, cell0, cell1):
        """Are these cells unconnected? Have they never been connected?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1. Both cells been in space for some_time
            2. They have no connection in their history
        Returns:
            value: 1.0 if connected, 0 if no
        """
        # If cells been in space for some_time
        #if cell0.age < COND_TIMES['some_time'] or \
            #cell1.age < COND_TIMES['some_time']:
            #return 0
        # They have no connection in their history
        if self.m_field.have_history(cell0.m_id,cell1.m_id):
            return 0
        return 1.0

    def test_tag(self, cid, cell0, cell1):
        """Did one of these individuals tag the other?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_chosen(self, cid, cell0, cell1):
        """Did the conductor choose these people to be connected?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_facing(self, cid, cell0, cell1):
        """Are cells facing each other over some time?

        Evaluates the folllowing criteria
            1. are facing each other
            2. are not in a group together
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # score = 1 if their facing value is 180 degrees
        # score = 0 if they are facing in the same direction
        # score not added if they are in a cell together
        # if they are not in a group together
        if cell0.m_gid != cell1.m_gid:
            d0 = cell0.m_body.m_facing
            d1 = cell1.m_body.m_facing
            score = 1 - float(abs(180-abs(d0-d1)))/180
            self.record_running_avg(cid,'friends',score)
        # we record our score in our running avg table
        return self.get_running_avg(cid,'friends')

    # Brief Happenings

    def test_fusion(self, cid, cell0, cell1):
        """Are cells currently fusing/fisioning?
        
        Meets the following conditions:
            [1. Is it even possible? check if geo->fromnearest for both cells is 
                between fusion_min and fusion_max - UNNECESSARY]
            2. Are they not in a group together already? Are cell's m_gid different?
            3. Is distance between fusion_min and fusion_max?
        Returns:
            value: 1.0 if connected, 0 if no
        """
        # if they are not in a group together
        if cell0.m_gid and cell0.m_gid == cell1.m_gid:
            return 0
        cell_dist = self.dist(cell0, cell1)
        # Is distance between fusion_min and fusion_max?
        if cell_dist > CONX_DIST['fusion_max'] or \
           cell_dist < CONX_DIST['fusion_min']:
            return 0
        return 1.0 - ((cell_dist-CONX_DIST['fusion_min']) /
                      (CONX_DIST['fusion_max']-CONX_DIST['fusion_min']))

    def test_transfer(self, cid, cell0, cell1):
        """Is a transfer of highlight happening between these cells?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0
    

    # Create connections


    # Check for expirations


