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

COND_DIST = config.conductor_distances
COND_TIMES = config.conductor_times
COND_LAT = config.conductor_latitude
COND_DECAY = config.conductor_decay

# init debugging
dbug = debug.Debug()


class Conductor(object):
    """An object representing the conductor.

    Stores the following values:
        m_field: store a back ref to the field that called us

    send_rollcall: send the current rollcall to concerned systems

    """

    def __init__(self, field):
        self.m_field = field
        self.connection_funcs = {
            'coord': self.test_coord,
            'fof': self.test_fof,
            'friends': self.test_friends,
            'grouped': self.test_grouped    ,
            'irlbuds': self.test_irlbuds,
            'leastconx': self.test_leastconx,
            'mirror': self.test_mirror,
            'nearby': self.test_nearby,
            'strangers': self.test_strangers,
            'tag': self.test_tag,
            'chosen': self.test_chosen,
            'facing': self.test_facing,
            'contact': self.test_contact,
            'fusion': self.test_fusion,
            'transfer': self.test_transfer,
        }

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
        #TODO: Do I need a deepcopy here?
        new_conx_dict = copy(self.m_field.m_conx_dict)
        # iterate over every connector
        for cid,connector in new_conx_dict.iteritems():
            new_attr_dict = copy(connector.m_attr_dict)
            # iterate over ever attr
            for type,attr in new_attr_dict.iteritems():
                # if decay time of type is not zero (no decay)
                if COND_DECAY[type]:
                    # if value of attr is zero or less
                    if attr.m_value == 0:
                        # delete atrr and maybe conx
                        self.m_field.del_conx_attr(cid, type)
                    else:
                        # calc new value based on time and decay rate
                        age = time() - attr.m_timestamp
                        newvalue = attr.m_origvalue - (age/COND_DECAY[type])
                        #print "KILLME:",cid,type,"timestmp:",attr.m_timestamp,"age:",age,"orig:",attr.m_origvalue,"newvalue:",newvalue
                        # if new value is < 0, we'll set it to 0
                        if newvalue <= 0:
                            if dbug.LEV & dbug.MORE: 
                                print "Conduct:age_and_expire_conx:Expired:",cid,type
                            newvalue = 0
                        # record the new value
                        attr.update(newvalue)

    def update_all_connections(self):
        """Test for and create new connections."""

        # iterate over all the pair combos in the cell dictionary:
        #   do each test and save the result
        #   if the result is non-zero
        #       if a connection does not exist already
        #           create a connection
        #       else
        #           update the value?
        # anything else? they should be picked up when the conductor does its
        # regular reports
        #   
        if dbug.LEV & dbug.MORE: 
            print "Conduct:update_all_conx"
        for (cell0,cell1) in list(combinations(self.m_field.m_cell_dict.values(), 2)):
            if self.m_field.is_cell_good_to_go(cell0.m_id) and \
               self.m_field.is_cell_good_to_go(cell1.m_id):
                for type,func in self.connection_funcs.iteritems():
                    result = func(cell0, cell1)
                    if result:
                        if dbug.LEV & dbug.MORE: 
                            print "Conduct:update_conx:results:%s-%s,%s,%s"%(cell0.m_id,
                            cell1.m_id, type, result)
                        # if a connection/attr does not already exist already
                        if not self.m_field.check_for_conx_attr(cell0, cell1, type):
                            if dbug.LEV & dbug.COND: 
                                print "Conduct:update_conx:adding connector/attr"
                            # create one
                            self.m_field.update_conx_attr(cell0, cell1, type, result)
                        else:
                            if dbug.LEV & dbug.MORE: 
                                print "Conduct:update_conx:already there, bro"
                            


    # Gather or calculate whether conditions are met for connection

    def dist(self, cell0, cell1):
        return sqrt((cell0.m_x - cell1.m_x)**2 + (cell0.m_y - cell1.m_y)**2)

    def test_grouped(self, cell0, cell1):
        """Are cells currently grouped?
        
        Meets the following conditions:
            1. If cell->m_gid the same for each cell
            R: Then yes! (easy)
        Returns:
            value: 1.0 if connected, 0 if no,
        """
        # If cell->m_gid the same for each cell
        if cell0.m_gid == cell1.m_gid:
            return 1.0
        return 0

    def test_friends(self, cell0, cell1):
        """Are cells in proximity for some time? Pref facing each other?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1. 
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_contact(self, cell0, cell1):
        """Are cells in contact with each other?

        Meets the following conditions:
            1. Is distance between cells < contact_dist
            R: Then yes! (easy)
        Returns:
            value: 1.0 if connected, 0 if no
        """
        if self.dist(cell0, cell1) < COND_DIST['contact']:
            return 1.0
        return 0

    def test_coord(self, cell0, cell1):
        """Are individuals moving in a coordinated way.

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_fof(self, cell0, cell1):
        """Are these cells connected through a third person?

        Meets the following conditions:
            1. 
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_irlbuds(self, cell0, cell1):
        """Did these people come in together?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_leastconx(self, cell0, cell1):
        """Are these individuals among the least connected in the field?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_mirror(self, cell0, cell1):
        """Are individuals moving in a mirrorwise way?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_nearby(self, cell0, cell1):
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
        if cell_dist < COND_DIST['nearby_min'] or cell_dist > COND_DIST['nearby_max']:
            return 0
        # nearby_max = 0; nearby_min = 1.0
        return 1.0 - ((cell_dist-nearby_min) / (nearby_max-nearby_min))

    def test_strangers(self, cell0, cell1):
        """Are these cells unconnected? Have they never been connected?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1. Both cells been in space for some_time
            2. They have no connection in their history
        Returns:
            value: 1.0 if connected, 0 if no
        """
        # If cells been in space for some_time
        if cell0.age < COND_TIMES['some_time'] or \
            cell1.age < COND_TIMES['some_time']:
            return 0
        # They have no connection in their history
        if self.m_field.have_history(cell0.m_id,cell1.m_id):
            return 0
        return 1.0

    def test_tag(self, cell0, cell1):
        """Did one of these individuals tag the other?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_chosen(self, cell0, cell1):
        """Did the conductor choose these people to be connected?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0

    def test_facing(self, cell0, cell1):
        """Are cells facing each other over some time?

        Note: This requires something to be saved over time.
        Meets the following conditions:
            1. Are not in a group together
            2. ...
        Returns:
            value: 1.0 if connected, 0 if no
        """
        # if they are not in a group together
        if cell0.m_gid == cell1.m_gid:
            return 0
        return 0

    # Brief Happenings

    def test_fusion(self, cell0, cell1):
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
        if cell0.m_gid == cell1.m_gid:
            return 0
        cell_dist = self.dist(cell0, cell1)
        # Is distance between fusion_min and fusion_max?
        if cell_dist > COND_DIST['fusion_max'] or \
           cell_dist < COND_DIST['fusion_min']:
            return 0
        return 1.0 - ((cell_dist-COND_DIST['fusion_min']) /
                      (COND_DIST['fusion_max']-COND_DIST['fusion_min']))

    def test_transfer(self, cell0, cell1):
        """Is a transfer of highlight happening between these cells?

        Meets the following conditions:
            1.
        Returns:
            value: 1.0 if connected, 0 if no
        """
        return 0
    

    # Create connections


    # Check for expirations


