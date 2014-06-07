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
from cmath import phase,pi

# installed modules

# local modules
from shared import config
from shared import debug

# local classes

# constants

LOGFILE = config.logfile

OSCPATH = config.oscpath

FRAMERATE = config.framerate

DEFAULT = 'default'
DEFAULT_MIN = 'default-min'
DEFAULT_MAX = 'default-max'

CELL_MIN = config.cell_avg_min
CELL_AVG = config.cell_avg_triggers
CELL_MEM = config.cell_memory_time
CELL_QUAL = config.cell_qualifying_triggers
CELL_AGE = config.cell_max_age
CELL_LAT = config.cell_latitude

CONX_MIN = config.connector_avg_min
CONX_AVG = config.connector_avg_triggers
CONX_MEM = config.connector_memory_time
CONX_QUAL = config.connector_qualifying_triggers
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

    Every algorithm that calculates an attribute, starts with a score which is
    clculated in a weighted running average, using a decay rate configured for
    that attribute. The current running average is returned.  Whether that 
    returned value triggers the attribute or not depends on whether it meets 
    the configurable trigger set in the config.

    Thus, every attribute has five critical aspects about it, four of them 
    configurable:

        1. The algorithm that determines the score in this moment.
        2. The "qualifying_trigger" that may specify distance, velocity, or 
            degrees for the algorithm
        3. The "memory_time" or how far back we are averaging
        4. The "avg_trigger" that when the running average is greater than 
            triggers the attribute
        5. The "max_age" or how long the attribute stays around once 
            triggered (it diminishes to 0 in this time)
    """

    def __init__(self, field):
        self.m_field = field
        self.cell_tests = {
            'dance': self.test_cell_dance,
            'interactive': self.test_cell_interactive,
            'static': self.test_cell_static,
            'kinetic': self.test_cell_kinetic,
            'fast': self.test_cell_fast,
            'timein': self.test_cell_timein,
            'spin': self.test_cell_spin,
            'quantum': self.test_cell_quantum,
            'jacks': self.test_cell_jacks,
            'chosen': self.test_cell_chosen,
        }

        self.conx_tests = {
            'grouped': self.test_conx_grouped,
            'contact': self.test_conx_contact,
            'friends': self.test_conx_friends,
            'coord': self.test_conx_coord,
            #'mirror': self.test_conx_mirror,
            #'fof': self.test_conx_fof,
            'irlbuds': self.test_conx_irlbuds,
            #'leastconx': self.test_conx_leastconx,
            'nearby': self.test_conx_nearby,
            'strangers': self.test_conx_strangers,
            #'tag': self.test_conx_tag,
            #'chosen': self.test_conx_chosen,
            'facing': self.test_conx_facing,
            #
            # Happenings
            #
            'fusion': self.test_conx_fusion,
            #'transfer': self.test_conx_transfer,
            #
            # Events
            #
            'touch': self.test_conx_touch,
            'tag': self.test_conx_tag,
        }

        self.m_avg_table = {}
        self.m_dist_table = {}

    #
    # Connection housekeeping
    #   Yes, I know this shoud be refactored so that cell and conx are the same
    #   code, but time is critical #techdebt
    #

    def update_all_conx(self):
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
            uid0 = cell0.m_id
            uid1 = cell1.m_id
            if self.m_field.is_cell_good_to_go(cell0.m_id) and \
                    self.m_field.is_cell_good_to_go(cell1.m_id):
                # get cid
                cid = self.m_field.get_cid(uid0, uid1)
                # calc distance once
                self.m_dist_table[cid] = self.dist(cell0, cell1)
                for type,conx_test in self.conx_tests.iteritems():
                    running_avg = conx_test(cid, type, cell0, cell1)
                    if type in CONX_AVG:
                        avg_trigger = CONX_AVG[type]
                    else:
                        avg_trigger = CONX_AVG[DEFAULT]
                    if dbug.LEV & dbug.COND: 
                        #if running_avg and avg_trigger:
                        if running_avg > CONX_MIN:
                            print "Conduct:update_conx:post_test:id:", \
                                    "%s-%s %.2f"%(cid,type,running_avg), \
                                    "(trigger:%.2f)"%avg_trigger
                    # if running_avg is above trigger
                    if running_avg > avg_trigger:
                        #if dbug.LEV & dbug.MORE: 
                            #print "Conduct:update_conx:results:%s-%s,%s,%s"% \
                                    #(cell0.m_id, cell1.m_id, type, running_avg)
                        # if a connection/attr does not already exist already
                        #if not self.m_field.check_for_conx_attr(uid0, uid1, type):
                        if dbug.LEV & dbug.MORE: 
                            print "Conduct:update_conx:triggered:id:", \
                                    "%s-%s %.2f"%(cid,type,running_avg), \
                                    "(trigger:%.2f)"%avg_trigger
                        # create one
                        self.m_field.update_conx_attr(cid, uid0, uid1, 
                                                    type, running_avg)
                        #else:
                            #if dbug.LEV & dbug.MORE: 
                                #print "Conduct:update_conx:already there, bro"
                    # if running_avg is under trigger value 
                    else:
                        if type in CONX_AGE:
                            max_age = CONX_AGE[type]
                        else:
                            max_age = CONX_AGE[DEFAULT]
                        #   AND decay time is zero, kill it
                        if not max_age:
                            if self.m_field.check_for_conx_attr(uid0, uid1, type):
                                # send "del conx" osc msg
                                self.m_field.m_osc.nix_conx_attr(cid, type)
                                # delete attr and maybe conx
                                self.m_field.del_conx_attr(cid, type)
                                index = str(cid)+'-'+str(type)
                                # actually we want to keep the avg
                                #if index in self.m_avg_table:
                                    #del self.m_avg_table[index]
                                if dbug.LEV & dbug.COND: 
                                    print "Conduct:update_conx:delete happening:",cid,type

    def record_conx_avg(self, id, type, sample):
        """Track Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(id)+'-'+str(type)
        if type in CONX_MEM:
            mem_time = CONX_MEM[type]
        else:
            mem_time = CONX_MEM[DEFAULT]
        if mem_time:
            k = 1 - 1/(FRAMERATE*float(mem_time))
            if index in self.m_avg_table:
                old_avg = self.m_avg_table[index]
            else:
                old_avg = 0
            self.m_avg_table[index] = k*old_avg + (1-k)*sample
        else:
            self.m_avg_table[index] = sample
        return self.m_avg_table[index]

    def get_conx_avg(self, id, type):
        """Retreive Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(id)+'-'+str(type)
        if index in self.m_avg_table:
            return self.m_avg_table[index]
        self.m_avg_table[index] = 0
        return 0

    def age_expire_conx(self):
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
        new_conx_dict = copy(self.m_field.m_conx_dict)
        if len(new_conx_dict) and (dbug.LEV & dbug.COND): 
            print "Conduct:age_and_expire_conx"
        # iterate over every connector
        for cid,connector in new_conx_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for type,attr in new_attr_dict.iteritems():
                if type in CONX_AGE:
                    max_age = CONX_AGE[type]
                else:
                    max_age = CONX_AGE[DEFAULT]
                # if value of attr is greater than zero
                if attr.m_value > CONX_MIN:
                    # if decay time of type is not zero (no decay)
                    if max_age:
                        # HERE is where we calc the decay 
                        # calc new value based on time and decay rate
                        age = time() - attr.m_createtime
                        since_update = time() - attr.m_updatetime
                        # The following only works because value and
                        # age/max_age are on the same scale, that is, they are
                        # both unit values (0-1.0)
                        newvalue = attr.m_origvalue - (since_update/max_age)
                        # if new value is < 0, we'll set it to 0
                        if newvalue <= 0:
                            newvalue = 0
                        # record the new value
                        attr.decay_value(newvalue)
                        if dbug.LEV & dbug.COND: 
                            print "    Aging:%s-%s"%(cid,type),\
                                  "age:%.2f"%age,\
                                  "since_update:%.2f"%since_update,\
                                  "orig_value:%.2f"%attr.m_origvalue,\
                                  "new_value:%.2f"%attr.m_value
                # the value of attr is zero, ie, it has decayed to nothin
                else:
                    # send "del conx" osc msg
                    self.m_field.m_osc.nix_conx_attr(cid, type)
                    # delete attr and maybe conx
                    self.m_field.del_conx_attr(cid, type)
                    index = str(cid)+'-'+str(type)
                    # actually we want to keep the avg
                    #if index in self.m_avg_table:
                        #del self.m_avg_table[index]
                    if dbug.LEV & dbug.COND: 
                        print "    Expired:%s-%s"%(cid,type),\
                              "(faded away to nothin')"


    #
    # Cell housekeeping
    #

    def update_all_cells(self):
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
            print "Conduct:update_all_cells"
        for uid,cell in self.m_field.m_cell_dict.iteritems():
            if self.m_field.is_cell_good_to_go(uid):
                for type, cell_test in self.cell_tests.iteritems():
                    running_avg = cell_test(uid, type)
                    if type in CELL_AVG:
                        avg_trigger = CELL_AVG[type]
                    else:
                        avg_trigger = CELL_AVG[DEFAULT]
                    if dbug.LEV & dbug.COND: 
                        #if running_avg and avg_trigger:
                        if running_avg > CONX_MIN:
                            print "Conduct:update_cell:post_test:id:", \
                                    "%s-%s %.2f"%(uid,type,running_avg), \
                                    "(trigger:%.2f)"%avg_trigger
                    # if running_avg is above trigger
                    if running_avg > avg_trigger:
                        #if dbug.LEV & dbug.MORE: 
                            #print "Conduct:update_cell:results:%s-%s,%s,%s"% \
                                    #(cell0.m_id, cell1.m_id, type, running_avg)
                        # if a connection/attr does not already exist already
                        #if not self.m_field.check_for_cell_attr(uid0, uid1, type):
                        if dbug.LEV & dbug.COND: 
                            print "Conduct:update_cell:triggered:id:", \
                                    "%s-%s %.2f"%(uid,type,running_avg), \
                                    "(trigger:%.2f)"%avg_trigger
                        # update or create one
                        self.m_field.update_cell_attr(uid, type, running_avg)
                        #else:
                            #if dbug.LEV & dbug.MORE: 
                                #print "Conduct:update_cell:already there, bro"
                    # if running_avg is under trigger value 
                    else:
                        if type in CELL_AGE:
                            max_age = CELL_AGE[type]
                        else:
                            max_age = CELL_AGE[DEFAULT]
                        #   AND decay time is zero, kill it
                        if not max_age:
                            #TODO: is uid avail here? XXX
                            if self.m_field.check_for_cell_attr(uid, type):
                                # send "del cell" osc msg
                                self.m_field.m_osc.nix_cell_attr(cid, type)
                                # delete attr and maybe cell
                                self.m_field.del_cell_attr(cid, type)
                                index = str(cid)+'-'+str(type)
                                # actually we want to keep the avg
                                #if index in self.m_avg_table:
                                    #del self.m_avg_table[index]
                                if dbug.LEV & dbug.COND: 
                                    print "Conduct:update_cell:delete happening:",cid,type

    def record_cell_avg(self, id, type, sample):
        """Track Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(id)+'-'+str(type)
        if type in CELL_MEM:
            time = CELL_MEM[type]
        else:
            time = CELL_MEM[DEFAULT]
        k = 1 - 1/(FRAMERATE*float(time))
        if index in self.m_avg_table:
            old_avg = self.m_avg_table[index]
        else:
            old_avg = 0
        self.m_avg_table[index] = k*old_avg + (1-k)*sample
        return self.m_avg_table[index]

    def get_cell_avg(self, id, type):
        """Retreive Exponentially decaying weighted moving averages (ema) in an 
        indexed dict."""
        index = str(id)+'-'+str(type)
        if index in self.m_avg_table:
            return self.m_avg_table[index]
        self.m_avg_table[index] = 0
        return 0

    def age_expire_cells(self):
        """Age and expire connectors.
        
        Note that we should do this before we discover and create new
        connections. That way they are not prematurly aged.

        iterate over every connector
            iterate over ever attr
                if decay time of type is not zero (no decay)
                    if value of attr is zero or less
                        delete atrr and maybe cell
                    else
                        calculate new value based on time and decay rate
                        if new value is < 0
                            we'll set it to 0
                        record the new value

        """
        new_cell_dict = copy(self.m_field.m_cell_dict)
        if len(new_cell_dict) and (dbug.LEV & dbug.COND): 
            print "Conduct:age_and_expire_cell"
        # iterate over every connector
        for uid,connector in new_cell_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for type,attr in new_attr_dict.iteritems():
                if type in CELL_AGE:
                    max_age = CELL_AGE[type]
                else:
                    max_age = CELL_AGE[DEFAULT]
                # if value of attr is greater than zero
                if attr.m_value > CELL_MIN:
                    # if decay time of type is not zero (no decay)
                    if max_age:
                        # HERE is where we calc the decay
                        # calc new value based on time and decay rate
                        age = time() - attr.m_createtime
                        since_update = time() - attr.m_updatetime
                        # the following only works because value and 
                        # age/max_age are both unit values (0-1.0)
                        newvalue = attr.m_origvalue - (since_update/max_age)
                        # if new value is < 0, we'll set it to 0
                        if newvalue <= 0:
                            newvalue = 0
                        # record the new value
                        attr.decay_value(newvalue)
                        if dbug.LEV & dbug.COND: 
                            print "    Aging:&s-%s"%uid,type,\
                                  "age:%.2f"%age,\
                                  "since_update:%.2f"%since_update,\
                                  "orig_value:%.2f"%attr.m_origvalue,\
                                  "new_value:%.2f"%attr.m_value
                # the value of attr is zero, ie, it has decayed to nothin
                else:
                    # send "del cell" osc msg
                    self.m_field.m_osc.nix_cell_attr(uid, type)
                    # delete attr and maybe cell
                    self.m_field.del_cell_attr(uid, type)
                    # actually we want to keep the avg
                    #if index in self.m_avg_table:
                        #del self.m_avg_table[index]
                    if dbug.LEV & dbug.COND: 
                        print "    Expired:%s-%s"%(uid,type),\
                              "(faded away to nothin')"

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

    #
    # Connections Tests
    #

    def test_conx_grouped(self, cid, type, cell0, cell1):
        """Are cells currently grouped?
        
        **Implemented & Successfully Tested

        Evaluates the folllowing criteria
            1. whether two people are in a group
            2: how long they've been grouped
            Score = 0.0 not in group, 1.0 if in group
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
        return self.record_conx_avg(cid, type, score)

    def test_conx_friends(self, cid, type, cell0, cell1):
        """Are cells in proximity for some time? Pref facing each other?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria
            1. distance between people
            2. length of time they've been close
            score = max(0, 1 - float(dist) / max_dist)
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        # we normalize this dist where 
        #   right on top of each other would be 1.0
        #   as far as you could get would be 0.0
        if type in CONX_QUAL:
            max_dist = CONX_QUAL[type]
        else:
            max_dist = CONX_QUAL[DEFAULT_MAX]
        score = max(0, 1 - float(dist) / max_dist)
        # we record our score in our running avg table
        return self.record_conx_avg(cid, type, score)

    def test_conx_contact(self, cid, type, cell0, cell1):
        """Are cells in contact with each other?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria
            1. Is distance between cells < contact_dist
            2: how long they've been grouped
            score = 1.0 if dist is within physical threshold
                  = 0.0 if dist is greater than phsical threshold
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        if dist < CONX_QUAL[type]:
            score = 1.0
        else:
            score = 0
        # we record our score in our running avg table
        return self.record_conx_avg(cid, type, score)

    def test_conx_coord(self, cid, type, cell0, cell1):
        """Are individuals moving in a coordinated way.

        **Implemented & Not Tested

        Evaluates the folllowing criteria
            1. similarity of velocities of two cells
                Note: Empirically  10m/s is highest vel
                    so 20m/s is the largest likely diff
            2. The similar velocities can't be near zero
            3. length of time they've been synchronized
            score = max(0, 1 - float(dist_of_velocities) / max_dist)
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # score = 1 if the values are exactly the same
        # score = 0 if the values are very different
        if 'coord-min-vel' in CONX_QUAL:
            min_spd = CONX_QUAL['coord-min-vel']
        else:
            min_spd = CONX_QUAL[DEFAULT_MIN]
        spd0 = sqrt(cell0.m_vx**2+cell0.m_vy**2)
        spd1 = sqrt(cell1.m_vx**2+cell1.m_vy**2)
        if spd0 < min_spd or spd1 < min_spd:
            score = 0.01
        else:
            if 'coord-max-vdiff' in CONX_QUAL:
                max_vdiff = CONX_QUAL['coord-max-vdiff']
            else:
                max_vdiff = CONX_QUAL[DEFAULT_MAX]
            #vdiff = sqrt((cell0.m_vx-cell1.m_vx)**2+(cell0.m_vy-cell1.m_vy)**2)
            #score = max(0, 1 - float(vdiff) / max_vdiff)
            score=min(1,max(0,(cell0.m_vx*cell1.m_vx+cell0.m_vy*cell1.m_vy)/(spd0*spd1)))   #BST-use correlation between velocities instead

        # we record our score in our running avg table
        return self.record_conx_avg(cid, type, score)

    def test_conx_fof(self, cid, type, cell0, cell1):
        """Are these cells connected through a third person?
        
        **Not Yes Implemented

        Meets the following conditions:
            1. 
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_irlbuds(self, cid, type, cell0, cell1):
        """Did these people come in together? Have they spent most of their
        time together?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria
            1. distance between people
            2. length of time they've been close
            score = max(0, 1 - float(dist) / max_dist)
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        # we normalize this dist where 
        #   right on top of each other would be 1.0
        #   as far as you could get would be 0.0
        if type in CONX_QUAL:
            max_dist = CONX_QUAL[type]
        else:
            max_dist = CONX_QUAL[DEFAULT_MAX]
        score = max(0, 1 - float(dist) / max_dist)
        # we record our score in our running avg table
        return self.record_conx_avg(cid, type, score)

    def test_conx_leastconx(self, cid, type, cell0, cell1):
        """Are these individuals among the least connected in the field?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_mirror(self, cid, type, cell0, cell1):
        """Are individuals moving in a mirrorwise way?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_nearby(self, cid, type, cell0, cell1):
        """Are cells near each other but not otherwise connected?

        **Implemented & Not Tested

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
        if 'nearby-min' in CONX_QUAL:
            min_dist = CONX_QUAL['nearby-min']
        else:
            min_dist = CONX_QUAL[DEFAULT_MIN]
        if 'nearby-max' in CONX_QUAL:
            max_dist = CONX_QUAL['nearby-max']
        else:
            max_dist = CONX_QUAL[DEFAULT_MAX]
        if cell_dist < min_dist or cell_dist > max_dist:
            return 0
        # nearby_max = 0; nearby_min = 1.0
        return 1.0 - ((cell_dist-min_dist) / (max_dist-min_dist))

    def test_conx_strangers(self, cid, type, cell0, cell1):
        """Are these cells unconnected? Have they never been connected?

        **Implemented & Not Tested

        Evaluates the folllowing criteria
            1. Both cells have been in the space for a while
            2. These two cells are not in a group
            Score = 0.0 in space for less than min time
                  = 1.0 if they are not in group together
                  = 0.0 if they are in group together
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # If the gid is not-zero and cell->m_gid the same for each cell
        age0 = time() - cell0.m_createtime 
        age1 = time() - cell1.m_createtime 
        if 'conx_strangers_min' in CONX_QUAL:
            min_age = CONX_QUAL['conx_strangers_min']
        else:
            min_age = CONX_QUAL[DEFAULT_MIN]
        if age0 < min_age or age1 < min_age:
            score = 0.01
        else:
            if cell0.m_gid != cell1.m_gid:
                score = 1.0
            else:
                score = 0.0
        # we record our score in our running avg table
        return self.record_conx_avg(cid, type, score)

    def test_conx_chosen(self, cid, type, cell0, cell1):
        """Did the conductor choose these people to be connected?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_facing(self, cid, type, cell0, cell1):
        """Are cells facing each other over some time?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria
            1. are not in a group together
            2. are facing each other
                a. find the angle from cell0 to cell1
                b. find the angle cell0 is facing
                c. find difference between them, and scale to unit scale
                d. repeat for cell1
                e. multiply two scores
            score = 1 - float(abs(180-abs(d0-d1)))/180
            TODO: use Brent's suggestion
        Returns:
            The exponentially decaying weighted moving average
        """
        # score = 1 if their facing value is 180 degrees
        # score = 0 if they are facing in the same direction
        # score not added if they are in a cell together
        # if they are not in a group together

        #TODO: Only if cells not in a group - Done
        #if True:
        if cell0.m_gid != cell1.m_gid:
            # get the facing angles of the two cells
            angle0 = cell0.m_body.m_facing%360
            angle1 = cell1.m_body.m_facing%360
            # get min qualifying angle
            if type in CONX_QUAL:
                min_angle = CONX_QUAL[type]
            else:
                min_angle = CONX_QUAL[DEFAULT]
            # calculate the angle from cell0 to cell1
            # FIXME: Tracker is sending the "facing away" angle rather than
            # facing -- later when it is fixed, we can remove "+ 180"
            phi0=phase(complex(cell1.m_x-cell0.m_x,
                                cell1.m_y-cell0.m_y)) *180/pi + 180
            # get diff btwn the angle of cell0 and the angle to cell1
            diff0 = abs(phi0 - angle0)
            if diff0 > 180:
                diff0 = diff0 - 360
            elif diff0 < -180:
                diff0 = diff0 + 360
            diff0 = abs(diff0)
            score0 = 1.0-min(diff0, min_angle)/min_angle
            # reverse phi to get angle from cell1 to cell0
            phi1 = (phi0 + 180) % 360
            # get diff btwn the angle of cell1 and the angle to cell0
            diff1 = abs(phi1 - angle1)
            if diff1 > 180:
                diff1 = diff1 - 360
            if diff1 < -180:
                diff1 = diff1 + 360
            diff1 = abs(diff1)
            score1 = 1.0-min(diff1, min_angle)/min_angle
            if dbug.LEV & dbug.MORE: 
                if score0 * score1:
                    print "facing:Frame:",self.m_field.m_frame,"HOLY SHIT, NOT ZERO"
                else:
                    print "facing:Frame:",self.m_field.m_frame
                print "    facing angle0=%d, phi0=%d, diff0=%d, score0=%.2f"%\
                      (angle0,phi0,diff0,score0)
                print "    facing angle1=%d, phi1=%d, diff1=%d, score1=%.2f"%\
                      (angle1,phi1,diff1,score1)
                print "    facing total score=%.2f"%(score0*score1)
            score = score0 * score1
            self.record_conx_avg(cid, type, score)
        # we record our score in our running avg table
        return self.get_conx_avg(cid, type)

    #
    # Happenings
    #

    def test_conx_fusion(self, cid, type, cell0, cell1):
        """Are cells currently fusing/fisioning?

        **Implemented & Successfully Tested

        Meets the following conditions:
            [1. Is it even possible? check if geo->fromnearest for both cells is 
                between fusion_min and fusion_max - UNNECESSARY]
            2. Are they not in a group together already? Are cell's m_gid different?
            3. Is distance between fusion_min and fusion_max?
        Returns:
            1.0 - ((cell_dist-min_dist) /
                      (max_dist-min_dist))
        """
        # if they are not in a group together
        if cell0.m_gid and cell0.m_gid == cell1.m_gid:
            return 0
        cell_dist = self.dist(cell0, cell1)
        # Is distance between fusion_min and fusion_max?
        if 'fusion-min' in CONX_QUAL:
            min_dist = CONX_QUAL['fusion-min']
        else:
            min_dist = CONX_QUAL[DEFAULT_MIN]
        if 'fusion-max' in CONX_QUAL:
            max_dist = CONX_QUAL['fusion-max']
        else:
            max_dist = CONX_QUAL[DEFAULT_MAX]
        if cell_dist > max_dist or \
               cell_dist < min_dist:
            return 0
        return 1.0 - ((cell_dist-min_dist) /
                      (max_dist-min_dist))

    def test_conx_transfer(self, cid, type, cell0, cell1):
        """Is a transfer of highlight happening between these cells?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    #
    # Event Tests
    #

    def test_conx_touch(self, cid, type, cell0, cell1):
        """Are these two people touching?

        **Not Implemented

        Evaluates the folllowing criteria
            1. Is distance between cells < contact_dist
            score = 1.0 if dist is within physical threshold
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        if dist < CONX_QUAL[type]:
            return 1.0
        else:
            return 0.0
        # we (don't) record our score in our running avg table
        #return self.record_conx_avg(cid, type, score)

    def test_conx_tag(self, cid, type, cell0, cell1):
        """Did one of these individuals tag the other?

        **Not Yes Implemented

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    #
    # Cell Tests
    #

    def test_cell_dance(self, uid, type):
        """Does this cell have a history of behavior that looks like dancing?

        **Not Yes Implemented

        Evaluates the folllowing criteria:
            1. xxx
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # evaluate something here
        # we record our score in our running avg table
        #return self.record_cell_avg(uid, type, score)
        return 0

    def test_cell_interactive(self, uid, type):
        """Does this cell have a history of being interactive?

        **Implemented & Not Tested

        Evaluates the folllowing criteria:
            2. Is this person near others under a dist threshold?
        Returns:
            The exponentially decaying weighted moving average
        """
        cell = self.m_field.m_cell_dict[uid]
        # we calculate a score
        # how close is this person to others?
        if type in CELL_QUAL:
            max_dist = CELL_QUAL[type]
        else:
            max_dist = CELL_QUAL[DEFAULT]
        score = max(0, 1 - float(cell.m_fromnearest) / max_dist)
        # we record our score in our running avg table
        return self.record_cell_avg(uid, type, score)

    def test_cell_static(self, uid, type):
        """Does this cell have a history of being immobile?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria:
            1. How close is this person's velocity to zero over time?
        Returns:
            The exponentially decaying weighted moving average
        """
        cell = self.m_field.m_cell_dict[uid]
        # we calculate a score
        spd = sqrt(cell.m_vx**2+cell.m_vy**2)
        if type in CELL_QUAL:
            max_vel = CELL_QUAL[type]
        else:
            max_vel = CELL_QUAL[DEFAULT]
        score = max(0, float(spd) / max_vel)
        # we record our score in our running avg table
        return self.record_cell_avg(uid, type, score)

    def test_cell_kinetic(self, uid, type):
        """Does this cell have a long history of going fast?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria:
            1. How close is this person's veolcity to the max over time?
        Returns:
            The exponentially decaying weighted moving average
        """
        cell = self.m_field.m_cell_dict[uid]
        # we calculate a score
        spd = sqrt(cell.m_vx**2+cell.m_vy**2)
        if type in CELL_QUAL:
            max_vel = CELL_QUAL[type]
        else:
            max_vel = CELL_QUAL[DEFAULT]
        score = min(1, float(spd) / max_vel)
        # we record our score in our running avg table
        return self.record_cell_avg(uid, type, score)

    def test_cell_fast(self, uid, type):
        """Does this cell have a short history of moving fast?

        **Implemented & Successfully Tested

        Evaluates the folllowing criteria:
            1. How close is this person's velocity to the max over short time?
        Returns:
            The exponentially decaying weighted moving average
        """
        cell = self.m_field.m_cell_dict[uid]
        # we calculate a score
        spd = sqrt(cell.m_vx**2+cell.m_vy**2)
        if type in CELL_QUAL:
            max_vel = CELL_QUAL[type]
        else:
            max_vel = CELL_QUAL[DEFAULT]
        score = min(1, float(spd) / max_vel)
        # we record our score in our running avg table
        return self.record_cell_avg(uid, type, score)

    def test_cell_timein(self, uid, type):
        """Does this cell have a history in the space?

        **Implemented & Not Tested

        Evaluates the folllowing criteria:
            1. Have they been in the space for a long time?
        Returns:
            The exponentially decaying weighted moving average
        """
        cell = self.m_field.m_cell_dict[uid]
        # we calculate a score
        age = time() - cell.m_createtime 
        if type in CELL_QUAL:
            min_age = CELL_QUAL[type]
        else:
            min_age = CELL_QUAL[DEFAULT]
        score = max(0, min(1, (float(age) / min_age)-1))
        # we record our score in our running avg table
        return self.record_cell_avg(uid, type, score)

    def test_cell_spin(self, uid, type):
        """Does this cell have a history of xxx?

        **Not Yes Implemented

        Evaluates the folllowing criteria:
            1. xxx
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # evaluate something here
        # we record our score in our running avg table
        #return self.record_cell_avg(uid, type, score)
        return 0

    def test_cell_quantum(self, uid, type):
        """Does this cell have a history of xxx?

        **Not Yes Implemented

        Evaluates the folllowing criteria:
            1. xxx
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # evaluate something here
        # we record our score in our running avg table
        #return self.record_cell_avg(uid, type, score)
        return 0

    def test_cell_jacks(self, uid, type):
        """Does this cell have a history of xxx?

        **Not Yes Implemented

        Evaluates the folllowing criteria:
            1. xxx
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # evaluate something here
        # we record our score in our running avg table
        #return self.record_cell_avg(uid, type, score)
        return 0

    def test_cell_chosen(self, uid, type):
        """Does this cell have a history of xxx?

        **Not Yes Implemented

        Evaluates the folllowing criteria:
            1. xxx
        Returns:
            The exponentially decaying weighted moving average
        """
        # we calculate a score
        # evaluate something here
        # we record our score in our running avg table
        #return self.record_cell_avg(uid, type, score)
        return 0
