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
__author__ = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from time import time
from math import sqrt
from itertools import combinations
from copy import copy
from cmath import phase, pi

# installed modules

# local modules
import config
import logging

# constants to make program text cleaner
CELL_AVG = config.cell_avg_triggers
CELL_MEM = config.cell_memory_time
CELL_QUAL = config.cell_qualifying_triggers
CELL_AGE = config.cell_max_age

CONX_AVG = config.connector_avg_triggers
CONX_MEM = config.connector_memory_time
CONX_QUAL = config.connector_qualifying_triggers
CONX_AGE = config.connector_max_age

# init logging
logger = logging.getLogger(__name__)

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

    def __init__(self, field=None, condglobal=1, cellglobal=1):
        self.m_field = field
        self.m_condglobal = condglobal
        self.m_cellglobal = cellglobal
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
            #'transfer': self.test_conx_transfer
            }
        self.event_tests = {
            #
            # Events
            #
            'touch': self.test_event_touch,
            'tag': self.test_event_tag
            }

        self.m_avg_table = {}
        self.m_dist_table = {}
        self.m_current_eid=1
        
    def update(self, field=None, condglobal=None, cellglobal=None):
        if field != None:
            self.m_field = field
        if condglobal != None:
            self.m_condglobal = condglobal
        if cellglobal != None:
            self.m_cellglobal = cellglobal

    def update_cell_param(self, atype, param, value):
        mod_array = None
        if param == "trigger":
            mod_array = CELL_AVG
            if value < .01:
                value = .01
        elif param == "memory":
            mod_array = CELL_MEM
        elif param == "maxage":
            mod_array = CELL_AGE
        elif param == "qual":
            mod_array = CELL_QUAL
        if mod_array is not None:
            mod_array[atype] = value

    def update_conx_param(self, atype, param, value):
        mod_array = None
        if param == "trigger":
            mod_array = CONX_AVG
            if value < .01:
                value = .01
        elif param == "memory":
            mod_array = CONX_MEM
        elif param == "maxage":
            mod_array = CONX_AGE
        elif param == "qual":
            mod_array = CONX_QUAL
        elif param == "qualmax":
            mod_array = CONX_QUAL
            atype = atype+"-max"
        elif param == "qualmin":
            mod_array = CONX_QUAL
            atype = atype+"-min"
        if mod_array is not None:
            mod_array[atype] = value


    #
    # Connection housekeeping
    #   Yes, I know this shoud be refactored so that cell and conx are the same
    #   code, but time is critical #techdebt
    #

    def update_all_conx(self):
        """Test for and create new connections.

        iterate over all the pair combos in the cell dictionary:
          do each test and save the result
          if a connection does not exist already and the avg is above the trigger
            create a connection
          if a connection exists
            update the value

       Age and expire connectors.
        Note that we should do this before we discover and create new
        connections. That way they are not prematurly aged.

        iterate over every connector
            iterate over ever attr
                if decay time of type is not zero (no decay)
                    if value of attr is zero or less
                        delete atrr and maybe conx
                    else
                        record the new value
        """
        #logger.debug("update_all_conx")
        # Make a copy so we don't run into problems when deleting connections
        new_conx_dict = copy(self.m_field.m_conx_dict)

        # iterate over every connector
        for cid, connector in new_conx_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for atype, attr in new_attr_dict.iteritems():
                if atype in CONX_AGE:
                    max_age = CONX_AGE[atype]
                else:
                    max_age = CONX_AGE["default"]
                if atype in CONX_AVG:
                    avg_trigger = CONX_AVG[atype]
                else:
                    avg_trigger = CONX_AVG["default"]

                since_update = time() - attr.m_updatetime
                if max_age > 0:
                    attr.set_freshness(1 - (since_update/max_age))

                # Check if we should remove this attribute
                # (when they are no longer triggered and it has been at least max_age since a trigger).
                if attr.m_value < avg_trigger and since_update > max_age:
                    logger.info("expired connection %s %s: value=%.2f,since_update=%.2f",cid, atype, attr.m_value, since_update)
                    attr.set_freshness(0.0)
                    # send "del conx" osc msg
                    self.m_field.m_osc.nix_conx_attr(cid, atype)
                    # delete attr and maybe conx
                    self.m_field.del_conx_attr(cid, atype)

        # Now add new connections
        for (cell0, cell1) in list(combinations(self.m_field.m_cell_dict.values(), 2)):
            uid0 = cell0.m_id
            uid1 = cell1.m_id
            if self.m_field.is_cell_good_to_go(cell0.m_id) and \
                    self.m_field.is_cell_good_to_go(cell1.m_id):
                # get cid
                cid = self.m_field.get_cid(uid0, uid1)
                # calc distance once
                self.m_dist_table[cid] = self.dist(cell0, cell1)
                for atype, conx_test in self.conx_tests.iteritems():
                    running_avg = conx_test(cid, atype, cell0, cell1)
                    if atype in CONX_AVG:
                        avg_trigger = CONX_AVG[atype]
                    else:
                        avg_trigger = CONX_AVG["default"]

                    if running_avg >= avg_trigger and not self.m_field.check_for_conx_attr(uid0, uid1, atype):
    					# Debug message for new connections only
                        logger.info("triggerred connection %s %s: avg (%.3f) >= trigger (%.3f)",cid, atype, running_avg, avg_trigger)

                    # Update all existing connections, and create new ones if triggered
                    if running_avg >= avg_trigger or self.m_field.check_for_conx_attr(uid0, uid1, atype):
                        # create or update connection
                        self.m_field.update_conx_attr(cid, uid0, uid1, atype, running_avg, running_avg >= avg_trigger)
                for etype, event_test in self.event_tests.iteritems():
                    if etype in CONX_AGE:
                        max_age = CONX_AGE[etype]
                    else:
                        max_age = 5

                    score = event_test(cid, etype, cell0, cell1)
                    if score > 0:
                        eid=self.m_field.find_or_delete_event(uid0, uid1, etype,max_age)
                        if eid==None:
                            eid=self.m_current_eid
                            self.m_current_eid+=1
                            logger.info("triggerred event %s %s between %d and %d with score %.3f, maxage=%.2f",eid, etype, uid0, uid1, score,max_age)
                            self.m_field.new_event(eid, uid0, uid1, etype, score)
                            
    def record_conx_avg(self, uid, atype, sample):
        """Track Exponentially decaying weighted moving averages (ema) in an indexed dict."""
        index = str(uid)+'-'+str(atype)
        if atype in CONX_MEM:
            mem_time = CONX_MEM[atype]
        else:
            mem_time = CONX_MEM["default"]
        if mem_time:
            k = 1 - 1/(config.framerate*float(mem_time))
            if index in self.m_avg_table:
                old_avg = self.m_avg_table[index]
            else:
                old_avg = 0
            self.m_avg_table[index] = k*old_avg + (1-k)*sample
        else:
            self.m_avg_table[index] = sample
        return self.m_avg_table[index]

    def get_conx_avg(self, uid, atype):
        """Retreive Exponentially decaying weighted moving averages (ema) in an indexed dict."""
        index = str(uid)+'-'+str(atype)
        if index in self.m_avg_table:
            return self.m_avg_table[index]
        self.m_avg_table[index] = 0
        return 0

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

        Age and expire connectors.
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
        #logger.debug( "update_all_cells")
        new_cell_dict = copy(self.m_field.m_cell_dict)

        # iterate over every connector
        for uid, connector in new_cell_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for atype, attr in new_attr_dict.iteritems():
                if atype in CELL_AGE:
                    max_age = CELL_AGE[atype]
                else:
                    max_age = CELL_AGE["default"]
                if atype in CELL_AVG:
                    avg_trigger = CELL_AVG[atype]
                else:
                    avg_trigger = CELL_AVG["default"]

                since_update = time() - attr.m_updatetime
                if max_age > 0:
                    attr.set_freshness(1-(since_update/max_age))

                # Check if we should remove this attribute (when they are no longer triggered and it has been at least max_age since a trigger).
                if attr.m_value < avg_trigger and since_update > max_age:
                    logger.info("expired cell %s %s: value=%.2f, trigger=%.2f,since_update=%.2f",uid, atype, attr.m_value, avg_trigger, since_update)
                    attr.set_freshness(0.0)
                    # send "del cell" osc msg
                    self.m_field.m_osc.nix_cell_attr(uid, atype)
                    # delete attr and maybe cell
                    self.m_field.del_cell_attr(uid, atype)
                    # actually we want to keep the avg
                    #if index in self.m_avg_table:
                        #del self.m_avg_table[index]


        # Now add new attributes, update existing ones
        for uid in self.m_field.m_cell_dict:
            if self.m_field.is_cell_good_to_go(uid):
                for atype, cell_test in self.cell_tests.iteritems():
                    running_avg = cell_test(uid, atype)
                    if atype in CELL_AVG:
                        avg_trigger = CELL_AVG[atype]
                    else:
                        avg_trigger = CELL_AVG["default"]

                    if running_avg >= avg_trigger and not self.m_field.check_for_cell_attr(uid, atype):
                        logger.info("triggered cell %s attribute %s: avg (%.2f) > trigger (%.2f)",uid, atype, running_avg, avg_trigger)

                    # Update all existing attributes, and create new ones if triggered
                    if running_avg >= avg_trigger or self.m_field.check_for_cell_attr(uid, atype):
                        # update or create
                        self.m_field.update_cell_attr(uid, atype, running_avg, running_avg >= avg_trigger)

    def record_cell_avg(self, uid, atype, sample):
        """Track Exponentially decaying weighted moving averages (ema) in an indexed dict."""
        index = str(uid)+'-'+str(atype)
        if atype in CELL_MEM:
            mtime = CELL_MEM[atype]
        else:
            mtime = CELL_MEM["default"]
        if index in self.m_avg_table:
            old_avg = self.m_avg_table[index]
        else:
            old_avg = 0
        if float(mtime)*config.framerate <= 1:
            self.m_avg_table[index] = sample
        else:
            k = 1 - 1/(config.framerate*float(mtime))
            self.m_avg_table[index] = k*old_avg + (1-k)*sample
        return self.m_avg_table[index]

    def get_cell_avg(self, uid, atype):
        """Retreive Exponentially decaying weighted moving averages (ema) in an indexed dict."""
        index = str(uid)+'-'+str(atype)
        if index in self.m_avg_table:
            return self.m_avg_table[index]
        self.m_avg_table[index] = 0
        return 0

    # Gather or calculate whether conditions are met for connection

    def dist(self, cell0, cell1):
        return sqrt((cell0.m_x - cell1.m_x)**2 + (cell0.m_y - cell1.m_y)**2)

    #
    # Connections Tests
    #

    def test_conx_grouped(self, cid, atype, cell0, cell1):
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
        return self.record_conx_avg(cid, atype, score)

    def test_conx_friends(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
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
        if not atype in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'",atype)
            return 0
        max_dist = CONX_QUAL[atype]
        score = max(0, 1 - float(dist) / max_dist)
        # we record our score in our running avg table
        return self.record_conx_avg(cid, atype, score)

    def test_conx_contact(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
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
        if dist < CONX_QUAL[atype]:
            score = 1.0
        else:
            score = 0
        # we record our score in our running avg table
        return self.record_conx_avg(cid, atype, score)

    def test_conx_coord(self, cid, atype, cell0, cell1):
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
#        tmplogger = logging.getLogger(__name__+".coord")
        if not 'coord-min' in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'", 'coord-min')
            return 0
        min_spd = CONX_QUAL['coord-min']
        spd0 = sqrt(cell0.m_vx**2+cell0.m_vy**2)
        spd1 = sqrt(cell1.m_vx**2+cell1.m_vy**2)
        if spd0 < min_spd or spd1 < min_spd:
            score = 0.01
        else:
            score = min(1,max(0,(cell0.m_vx*cell1.m_vx+cell0.m_vy*cell1.m_vy)/(spd0*spd1)))   #BST-use correlation between velocities instead
        avgscore = self.record_conx_avg(cid, atype, score)
#        tmplogger.debug( "coord: spd0=%.2f (%.2f,%.2f), spd1=%.2f (%.2f,%.2f), score=%.3f, avg=%.3f",spd0, cell0.m_vx, cell0.m_vy, spd1, cell1.m_vx, cell1.m_vy, score, avgscore)

        # we record our score in our running avg table
        return avgscore

    def test_conx_fof(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Are these cells connected through a third person?
        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_irlbuds(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
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
        if not atype in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'", atype)
            return 0
        max_dist = CONX_QUAL[atype]
        if dist < max_dist:
            score = 1.0
        else:
            score = 0.0

        # we record our score in our running avg table to make it into a fraction of time that these 2 people were within max_dist of each other
        return self.record_conx_avg(cid, atype, score)

    def test_conx_leastconx(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Are these individuals among the least connected in the field?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_mirror(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Are individuals moving in a mirrorwise way?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_nearby(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Are cells near each other but not otherwise connected?

        **Implemented & Not Tested

        Meets the following conditions:
            1. If cells do not share a connections
            2. If cells are not in a group with each other
            3. If dist of cells are > nearby-min and < nearby-max
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
        if not 'nearby-min' in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'", 'nearby-min')
            return 0
        min_dist = CONX_QUAL['nearby-min']
        if not 'nearby-max' in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'", 'nearby-max')
            return 0
        max_dist = CONX_QUAL['nearby-max']
        if cell_dist < min_dist or cell_dist > max_dist:
            return 0
        # nearby-max = 0; nearby-min = 1.0
        return 1.0 - ((cell_dist-min_dist) / (max_dist-min_dist))

    def test_conx_strangers(self, cid, atype, cell0, cell1):
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
        if not 'strangers-min' in CONX_QUAL:
            logger.error("No connector_qualifying_triggers set for type '%s'", 'strangers-min')
            return 0
        min_age = CONX_QUAL['strangers-min']
        if age0 < min_age or age1 < min_age:
            score = 0.01
        else:
            if cell0.m_gid == cell1.m_gid and cell0.m_gid != 0:
                score = 0.0
            else:
                score = 1.0
        # we record our score in our running avg table
        return self.record_conx_avg(cid, atype, score)

    def test_conx_chosen(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Did the conductor choose these people to be connected?

        **Not Yes Implemented

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_conx_facing(self, cid, atype, cell0, cell1):
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
        if cell0.m_gid != cell1.m_gid or cell0.m_gid == 0 or cell1.m_gid == 0:
            # get the facing angles of the two cells
            angle0 = cell0.m_body.m_facing%360
            angle1 = cell1.m_body.m_facing%360
            # get min qualifying angle
            if not atype in CONX_QUAL:
                logger.error("No connector_qualifying_triggers set for type '%s'", atype)
                return 0
            min_angle = CONX_QUAL[atype]
            # calculate the angle from cell0 to cell1
            # FIXME: Tracker is sending the "facing away" angle rather than
            # facing -- later when it is fixed, we can remove "+ 180"
            phi0 = phase(complex(cell1.m_x-cell0.m_x,cell1.m_y-cell0.m_y)) *180/pi - 90
            # get diff btwn the angle of cell0 and the angle to cell1
            diff0 = abs(phi0 - angle0)
            if diff0 > 180:
                diff0 = diff0 - 360
            elif diff0 < -180:
                diff0 = diff0 + 360
            diff0 = abs(diff0)
            if diff0 < min_angle:
                score0 = 1.0
            else:
                score0 = 0.0

            # reverse phi to get angle from cell1 to cell0
            phi1 = (phi0 + 180) % 360
            # get diff btwn the angle of cell1 and the angle to cell0
            diff1 = abs(phi1 - angle1)
            if diff1 > 180:
                diff1 = diff1 - 360
            if diff1 < -180:
                diff1 = diff1 + 360
            diff1 = abs(diff1)
            if diff1 < min_angle:
                score1 = 1.0
            else:
                score1=0.0
            score = score0 * score1
            self.record_conx_avg(cid, atype, score)
            if score0 * score1:
                msg=" ".join([str(x) for x in [ "facing:Frame:",self.m_field.m_frame,", CID:", cid, "HOLY SHIT, NOT ZERO"]])
            else:
                msg=" ".join([str(x) for x in [ "facing:Frame:",self.m_field.m_frame,", CID:", cid]])
            msg=msg+ "    facing angle0=%d, phi0=%d, diff0=%d, score0=%.2f"%(angle0,phi0,diff0,score0)
            msg=msg+ "    facing angle1=%d, phi1=%d, diff1=%d, score1=%.2f"%(angle1,phi1,diff1,score1)
            msg=msg+ "    facing: instantaneous score=%.2f, avg=%.2f"%(score,self.get_conx_avg(cid,atype))
            logging.getLogger(__name__+".facing").debug(msg)

        # we record our score in our running avg table
        return self.get_conx_avg(cid, atype)

    #
    # Happenings
    #

    def test_conx_fusion(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
        """Are cells currently fusing/fisioning?

        **Implemented & Successfully Tested

        Meets the following conditions:
            [1. Is it even possible? check if geo->fromnearest for both cells is 
                between fusion-min and fusion-max - UNNECESSARY]
            2. Are they not in a group together already? Are cell's m_gid different?
            3. Is distance between fusion-min and fusion-max?
        Returns:
            1.0 - ((cell_dist-min_dist) /
                      (max_dist-min_dist))
        """
        # if they are not in a group together
        if cell0.m_gid and cell0.m_gid == cell1.m_gid:
            return 0
        cell_dist = self.dist(cell0, cell1)
        # Is distance between fusion-min and fusion-max?
        if not 'fusion-min' in CONX_QUAL:
            logging.error("No connector_qualifying_triggers set for type '%s'", 'fusion-min')
            return 0
        min_dist = CONX_QUAL['fusion-min']
        if not 'fusion-max' in CONX_QUAL:
            logging.error("No connector_qualifying_triggers set for type '%s'", 'fusion-max')
            return 0
        max_dist = CONX_QUAL['fusion-max']
        if cell_dist > max_dist or \
               cell_dist < min_dist:
            return 0
        return 1.0 - ((cell_dist-min_dist) /
                      (max_dist-min_dist))

    def test_conx_transfer(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
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

    def test_event_touch(self, cid, atype, cell0, cell1):
        """Are these two people touching?
        Evaluates the folllowing criteria
            1. Is distance between cells < contact_dist
            score = 1.0 if dist is within physical threshold
        Returns:
            score
        """
        # we calculate a score
        # we get the distance between cells
        dist = self.m_dist_table[cid]
        relvel=[cell0.m_vx-cell1.m_vx,cell0.m_vy-cell1.m_vy]	# Net velocity of cell0
        relpos=[cell1.m_x-cell0.m_x,cell1.m_y-cell0.m_y]			# Net position of cell1 relative to cell0
        relspeed=(relvel[0]*relpos[0]+relvel[1]*relpos[1])/sqrt(relpos[0]*relpos[0]+relpos[1]*relpos[1])
        if dist < CONX_QUAL[atype] and relspeed>0:
            if relspeed>1.0:
                score = 1.0
            else:
                score = relspeed
        else:
            score = 0.0
        # tmplogger = logging.getLogger(__name__+".touch")
        # tmplogger.info( "touch: cid=%s, pos0=(%.2f,%.2f), pos1=(%.2f, %.2f), vel0= (%.2f,%.2f), vel1= (%.2f,%.2f), relspeed=%.3f, dist=%.3f,score=%.3f", cid, cell0.m_x, cell0.m_y, cell1.m_x, cell1.m_y, cell0.m_vx, cell0.m_vy, cell1.m_vx, cell1.m_vy, relspeed, dist, score)
        return score

    def test_event_tag(self, cid, atype, cell0, cell1):   #pylint: disable=W0613
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

    def test_cell_dance(self, uid, atype):   #pylint: disable=W0613
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
        #return self.record_cell_avg(uid, atype, score)
        return 0

    def test_cell_interactive(self, uid, atype):
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
        if not atype in CELL_QUAL:
            logging.error("No cell_qualifying_triggers set for type '%s'", atype)
            return 0
        max_dist = CELL_QUAL[atype]
        if cell.m_fromnearest<0:
            score=0
        else:
            score = max(0, 1 - float(cell.m_fromnearest) / max_dist)
#        logging.debug("Interactive UID %d, max_dist=%f, fromnearest=%f, score = %f", uid,max_dist, cell.m_fromnearest,score)
        # we record our score in our running avg table
        return self.record_cell_avg(uid, atype, score)

    def test_cell_static(self, uid, atype):
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
        if not atype in CELL_QUAL:
            logging.error("No cell_qualifying_triggers set for type '%s'", atype)
            return 0
        max_vel = CELL_QUAL[atype]
        if spd<max_vel:
            score=1.0
        else:
            score=0.0
        avg=self.record_cell_avg(uid, atype, score)
        logging.getLogger(__name__+".static").debug("test_cell_static: uid=%s, spd=%.2f, max_vel=%.2f, score=%.2f,avg=%.2f", uid,spd,max_vel,score,avg)
        # we record our score in our running avg table
        return avg

    def test_cell_kinetic(self, uid, atype):
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
        if not atype in CELL_QUAL:
            logger.error("No cell_qualifying_triggers set for type '%s'", atype)
            return 0
        min_vel = CELL_QUAL[atype]
        if spd>min_vel:
            score=1.0
        else:
            score=0.0
        avg=self.record_cell_avg(uid, atype, score)
        logging.getLogger(__name__+".kinetic").debug("test_cell_kinetic: uid=%s, spd=%.2f, min_vel=%.2f, score=%.2f, avg=%.2f", uid,spd,min_vel,score,avg)
        
        # we record our score in our running avg table
        return avg

    def test_cell_fast(self, uid, atype):
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
        if not atype in CELL_QUAL:
            logging.error("No cell_qualifying_triggers set for type '%s'", atype)
            return 0
        max_vel = CELL_QUAL[atype]
        if spd>=max_vel:
            score=1.0
        else:
            score=0.0
        # we record our score in our running avg table
        return self.record_cell_avg(uid, atype, score)

    def test_cell_timein(self, uid, atype):
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
        if not atype in CELL_QUAL:
            logging.error("No cell_qualifying_triggers set for type '%s'", atype)
            return 0
        min_age = CELL_QUAL[atype]
        if min_age<=0:
            score=1
        else:
            score = max(0, min(1, (float(age) / min_age)-1))
        # we record our score in our running avg table
        return self.record_cell_avg(uid, atype, score)

    def test_cell_spin(self, uid, atype):   #pylint: disable=W0613
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
        #return self.record_cell_avg(uid, atype, score)
        return 0

    def test_cell_quantum(self, uid, atype):   #pylint: disable=W0613
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
        #return self.record_cell_avg(uid, atype, score)
        return 0

    def test_cell_jacks(self, uid, atype):   #pylint: disable=W0613
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
        #return self.record_cell_avg(uid, atype, score)
        return 0

    def test_cell_chosen(self, uid, atype):   #pylint: disable=W0613
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
        #return self.record_cell_avg(uid, atype, score)
        return 0
