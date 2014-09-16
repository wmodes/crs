#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Header template file.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "header.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config
from shared import debug
from time import time

# local classes
from shared.cell import Cell
from shared.connector import Connector
from shared.group import Group
from shared.event import Event

# constants
LOGFILE = config.logfile
REPORT_FREQ = config.report_frequency
GROUP_DIST = config.group_distance
UNGROUP_DIST = config.ungroup_distance
OSC_FPS = config.framerate
XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field

MAX_LOST_PATIENCE = config.max_lost_patience

# init debugging
dbug = debug.Debug()

# TODO: Delete anything here that is specific to visualsys
class Field(object):
    """An object representing the field.  

    Here are the things we store:
        m_still_running: a flag for exiting the main loop
        m_our_cell_count: the running we count of how many cells we have
        m_reported_cell_count: what the tracking system reports
        m_cell_dict: dictionary of all cells we have
        m_conx_dict: dictionary of all connectors we have
        m_group_dict: dictionary of all groups we have
        m_event_dict: dictionary of all events we have
        m_suspect_cells: list of cells we suspect are dead
        m_suspect_groups: list of groups we suspect are dead
        m_frame: which frame is the tracker reporting
        m_scene: the current scene we are performing
        m_scene_variant: the current scene variant we are performing
        m_scene_value: value associated with scene
    
    """

    cellClass = Cell
    connectorClass = Connector
    groupClass = Group

    def __init__(self):
        self.m_still_running = True
        self.m_our_cell_count = 0
        self.m_reported_cell_count = 0
        # we could use a list here which would make certain things easier, but
        # we need to do deletions and references pretty regularly.
        self.m_cell_dict = {}
        self.m_conx_dict = {}
        self.m_group_dict = {}
        self.m_event_dict = {}
        # a dict of missing cells, indexed by cid
        self.m_suspect_cells = {}
        # a dict of missing groups, indexed by gid
        self.m_suspect_groups = {}
        #self.allpaths = []
        self.set_scaling((XMIN_FIELD,YMIN_FIELD),(XMAX_FIELD,YMAX_FIELD))
        self.m_xmin_field = XMIN_FIELD
        self.m_ymin_field = YMIN_FIELD
        self.m_xmax_field = XMAX_FIELD
        self.m_ymax_field = YMAX_FIELD
        self.m_giddist = GROUP_DIST
        self.m_ungroupdist = UNGROUP_DIST
        self.m_oscfps = OSC_FPS
        self.m_frame = 0
        self.m_scene = None
        self.m_scene_variant = None
        self.m_scene_value = None

    def update(self, groupdist=None, ungroupdist=None, oscfps=None,
               osc=None, frame=None):
        if groupdist is not None:
            self.m_giddist = groupdist
        if ungroupdist is not None:
            self.m_ungroupdist = ungroupdist
        if oscfps is not None:
            self.m_oscfps = oscfps
        if osc is not None:
            self.m_osc = osc
        if frame is not None:
            self.m_frame = frame
            if frame%REPORT_FREQ['debug'] == 0:
                print "Field:update:frame:",frame

    def update_scene(self, scene, variant, value):
        self.m_scene = scene
        self.m_scene_variant = variant
        self.m_scene_value = value

    # Scaling
    def set_scaling(self,pmin_field=None,pmax_field=None):
        """Set up scaling in the field.

        A word about graphics scaling:
         * The vision tracking system (our input data) measures in meters.

         So we will keep eveything internally in centemeters (so we can use ints
         instead of floats), and then convert it to the approriate units before 
         ...but we will probably be changing this to meter floats

         """

        if pmin_field is not None:
            self.m_xmin_field = pmin_field[0]
            self.m_ymin_field = pmin_field[1]
        if pmax_field is not None:
            self.m_xmax_field = pmax_field[0]
            self.m_ymax_field = pmax_field[1]
        if dbug.LEV & dbug.MORE: print "Field dims:", (self.m_xmin_field,
                self.m_ymin_field), (self.m_xmax_field, self.m_ymax_field)

    # Events
    #    /conductor/event [eid,"type",uid0,uid1,value,time]

    def update_event(self, eid, uid0=None, uid1=None, value=None, time=None):
        """Create event if it doesn't exist, update its info."""
        if eid not in self.m_event_dict:
            self.m_event_dict[eid] = Event(self, eid, uid0, uid1, value, time)
        else:
            self.m_event_dict[eid].update(uid0, uid1, value, time)

    def del_event(self,eid):
        if eid in self.m_event_dict:
            del self.m_event_dict[eid]

    # Groups
    #    /pf/group samp gid gsize duration centroidX centroidY diameter

    def create_group(self, gid):
        """Create group if it doesn't exist, update its info."""
        if gid:
            # If it already exists, don't create it
            if not gid in self.m_group_dict:
                # note: pass self since we want a back reference to field instance
                group = self.groupClass(self, gid)
                # add to the group list
                self.m_group_dict[gid] = group
                if dbug.LEV & dbug.FIELD: 
                    print "Field:create_group:Group",gid,"created"
                #self.m_our_group_count += 1
                #if dbug.LEV & dbug.FIELD:
                    #print "Field:create_group:count:",self.m_our_group_count
            # whether it is new or already existed,
            # let's make sure it is no longer suspect
            if gid in self.m_suspect_groups:
                if dbug.LEV & dbug.FIELD: 
                    print "Field:create_group:Group",gid,\
                          "was suspected lost but is now above suspicion"
                del self.m_suspect_groups[gid]

    def update_group(self, gid, gsize=None, duration=None, x=None, y=None,
                     diam=None):
        """Create group if it doesn't exist, update its info."""
        if dbug.LEV & dbug.MORE: 
            print "Field:update_group:Group",gid
        if gid:
            self.check_for_missing_group(gid)
            self.m_group_dict[gid].update(gsize, duration, x, y, diam)

    def del_group(self,gid):
        if gid in self.m_group_dict:
            self.m_group_dict[gid].drop_all_cells()
            del self.m_group_dict[gid]

    # Legs and Body

    def update_body(self, id, x=None, y=None, ex=None, ey=None, 
                 spd=None, espd=None, facing=None, efacing=None, 
                 diam=None, sigmadiam=None, sep=None, sigmasep=None,
                 leftness=None, vis=None):
        # first we make sure the cell exists and is not suspect
        self.check_for_missing_cell(id)
        # update body info
        self.m_cell_dict[id].update_body(x, y, ex, ey, spd, espd, facing, efacing, 
                           diam, sigmadiam, sep, sigmasep, leftness, vis)

    def update_leg(self, id, leg, nlegs=None, x=None, y=None, 
                 ex=None, ey=None, spd=None, espd=None, 
                 heading=None, eheading=None, vis=None):
        """ Update leg information.  """ 
        # first we make sure the cell exists and is not suspect
        self.check_for_missing_cell(id)
        # update leg info
        self.m_cell_dict[id].update_leg(leg, nlegs, x, y, ex, ey, spd, espd, 
                                   heading, eheading, vis)
    # Cells

    def create_cell(self, id):
        """Create a cell.  """
        # If it already exists, don't create it
        if not id in self.m_cell_dict:
            # note1: we access the cell class indirectly for local subclassing
            # note2: pass self since we want a back reference to field instance
            cell = self.cellClass(self, id)
            # add to the cell list
            self.m_cell_dict[id] = cell
            self.m_our_cell_count += 1
            if dbug.LEV & dbug.FIELD: print "Field:create_cell:count:",self.m_our_cell_count
        # but if it already exists
        else:
            # let's make sure it is no longer suspect
            if id in self.m_suspect_cells:
                if dbug.LEV & dbug.FIELD: print "Field:create_cell:Cell",id,"was suspected lost but is now above suspicion"
                del self.m_suspect_cells[id]

    def update_cell(self, id, x=None, y=None, vx=None, vy=None, major=None, 
                    minor=None, gid=None, gsize=None, visible=None, frame=None):
        """ Update a cells information."""
        if dbug.LEV & dbug.MORE: print "Field:update_cell:Cell",id
        self.check_for_missing_cell(id)
        # if group param is provided 
        # if it is zero, that is okay and noteworthy (means no group)
        if gid is not None:
            self.check_for_missing_group(gid)
            self.check_for_new_group(id, gid)
            # now update the cell's gid membership
            # this is redundant but okay
            self.m_cell_dict[id].m_gid = gid
            # if non-zero, add cell to cell_dict in group
            if gid:
                self.m_group_dict[gid].m_cell_dict[id] = self.m_cell_dict[id]
                if dbug.LEV & dbug.FIELD: 
                    print "Field:update_cell:Cell",id,"added to group", \
                            self.m_cell_dict[id].m_gid
        self.m_cell_dict[id].update(x, y, vx, vy, major, minor, gid, gsize,
                                    visible=visible, frame=frame)

    def check_for_cell_attr(self, uid, type):
        if uid in self.m_cell_dict:
            cell = self.m_cell_dict[uid]
            if type in cell.m_attr_dict:
                return True
        return False

    def update_cell_attr(self, uid, type, value):
        """Update an attribute to a cell, creating it if it doesn't exist."""
        self.check_for_missing_cell(uid)
        if dbug.LEV & dbug.MORE: 
            print "Field:update_cell_attr:",uid, type, value
        self.m_cell_dict[uid].update_attr(type, value)

    def del_cell_attr(self, uid, type):
        """Delete an attribute to a cell."""
        if uid in self.m_cell_dict:
            cell = self.m_cell_dict[uid]
            if type in cell.m_attr_dict:
                cell.del_attr(type)
                if dbug.LEV & dbug.FIELD: 
                    print "Field:del_cell_attr:del_attr:",uid,type

    def update_geo(self, id, fromcenter=None, fromnearest=None, fromexit=None):
        """Update geo info for cell."""
        self.check_for_missing_cell(id)
        self.m_cell_dict[id].geoupdate(fromcenter, fromnearest, fromexit)

    def del_cell(self, id):
        """Delete a cell.

        We used to delete all of it's connections, now we just delete it and
        let the connector sort it out. This allows us to defer connector
        deletion -- instead we keep a list of suspicious connectors. That way, 
        if the cells reappear, we can reconnect them without losing their
        connectors.

        However, this created a problem: When a cell was deleted and then later
        restored, its connectors were still referencing the previous cell.
        Therefore, when we iterate through the conxs, they are still taking
        their location from the former cell.  
            Solution 1: Delete the conx along with the cell
            Solution 2: When a cell reappears, refresh the connectors to 
                point to the new cell.
        We did Solution 2 for a while with the result being some ghost
        connections, now we will try Solution 1.

        """
        #cell = self.m_cell_dict[id]
        # delete all cell's connectors from master list of connectors
        #for conxid in cell.m_conx_dict:

        #    if conxid in self.m_conx_dict:
        #        del self.m_conx_dict[conxid]
        # have cell disconnect all of its connections and refs
        # Note: connector checks if cell still exists before rendering
        if id in self.m_cell_dict:
            #cell.cell_disconnect()
            # delete from the cell master list of cells
            if dbug.LEV & dbug.FIELD: 
                print "Field:del_cell:deleting",id
            # Solution 1: Delete the conx along with the cell
            new_conx_dict = self.m_cell_dict[id].m_conx_dict.copy()
            for cid,conx in new_conx_dict.iteritems():
                self.del_connector(cid)
            # Note that this only deletes the cell from the master list, but
            # doesn't destroy the instance, which may still be refd elsewhere.
            del self.m_cell_dict[id]
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            else:
                self.m_our_cell_count -= 1
            if dbug.LEV & dbug.FIELD: 
                print "Field:del_cell:count:",self.m_our_cell_count

    def check_people_count(self,reported_count):
        self.m_reported_cell_count = reported_count
        our_count = self.m_our_cell_count
        if dbug.LEV & dbug.FIELD: print "Field:check_people_count:count:",our_count,"- Reported:",self.m_reported_cell_count
        if reported_count != our_count:
            if dbug.LEV & dbug.FIELD: print "Field:check_people_count:Count mismatch"
            self.suspect_all_cells()
            self.m_out_cell_count = 0

    def suspect_cell(self, id):
        """Hide a cell.
        We don't delete cells unless we have to.
        Instead we add them to a suspect list (actually a count of how
        suspicous they are)
        """
        self.m_suspect_cells[id] = 1
        self.m_our_cell_count -= 1
        if dbug.LEV & dbug.FIELD: print "Field:suspect_cell:count:",self.m_our_cell_count

    def suspect_all_cells(self):
        if dbug.LEV & dbug.FIELD: print "Field:suspect_all_cells"
        for id in self.m_cell_dict:
            self.suspect_cell(id)
        self.m_our_cell_count = 0
        if dbug.LEV & dbug.FIELD: print "Field:suspect_cell:count:",self.m_our_cell_count

    # Connectors

    def get_cid(self, uid0, uid1):
        if uid0 < uid1:
            cid = str(uid0) + "-" + str(uid1)
        else:
            cid = str(uid1) + "-" + str(uid0)
        return cid

    def get_connector(self, cid):
        if cid in self.m_conx_dict:
            return self.m_conx_dict[cid]
        return None

    def create_connector(self, uid0, uid1):
        """Create connector and assign id."""
        cid = self.get_cid(uid0, uid1)
        cell0 = self.m_cell_dict[uid0]
        cell1 = self.m_cell_dict[uid1]
        # if a connector doesn't already exist between cells
        if cid in self.m_conx_dict:
            connector = self.m_conx_dict[cid]
        else:
            # create connector and add to the connector list
            # Note1: Connector class takes care of storing the cells as well as
            #   telling each of the two cells that they now have a connector
            # Note2: we pass self since we want a back reference to field instance
            connector = self.connectorClass(self, cid, cell0, cell1,
                                            frame=self.m_frame)
            self.m_conx_dict[cid] = connector
        return connector

    def update_connector(self, id, frame=None):
        """ Update a connector's information."""
        if dbug.LEV & dbug.MORE: print "Field:update_conx:Cell",id
        if id in self.m_conx_dict:
            self.m_conx_dict[id].update(frame=self.m_frame)

    def del_connector(self, cid):
        if cid in self.m_conx_dict:
            # make sure the cells that this connector is attached to, delete
            # refs to it
            self.m_conx_dict[cid].conx_disconnect_thyself()
            # remove from the connector list
            del self.m_conx_dict[cid]

    def check_for_conx_attr(self, uid0, uid1, type):
        connector = self.get_connector(self.get_cid(uid0, uid1))
        if not connector:
            return False
        if type not in connector.m_attr_dict:
            return False
        return True

    def update_conx_attr(self, cid, uid0, uid1, type, value):
        """Update an attribute to a connector, creating it if it doesn't exist."""
        self.check_for_missing_cell(uid0)
        self.check_for_missing_cell(uid1)
        self.check_for_missing_conx(cid, uid0, uid1)
        connector = self.m_conx_dict[cid]
        if dbug.LEV & dbug.MORE: 
            print "Field:update_conx_attr:",connector.m_id,type,value
        connector.update_attr(type, value)

    def del_conx_attr(self, cid, type):
        """Delete an attribute to a connector, removing the connector if the
        list is empty."""
        if cid in self.m_conx_dict:
            connector = self.m_conx_dict[cid]
            if type in connector.m_attr_dict:
                connector.del_attr(type)
                if dbug.LEV & dbug.FIELD: 
                    print "Field:del_conx_attr:del_attr:",cid,type
            if not len(connector.m_attr_dict):
                self.del_connector(cid)
                if dbug.LEV & dbug.FIELD: 
                    print "Field:del_conx_attr:del_conx:",cid

    # Checks and housekeeping

    def check_for_missing_group(self, gid):
        """Check for missing or suspect group, handle it.

        Possibilities:
            * Group does not exist:
                create it, remove from suspect list, update it, increment count
            * Group exists, but is on the suspect list
                remove from suspect list, increment count
            * Group exists in master list and is not suspect:
                update its info; count unchanged
        """
        # if the gid is a real group (non-zero)
        if gid:
            # and if group does not already exist
            if gid not in self.m_group_dict:
                self.create_group(gid)
                # create_group already does this.
                # remove from suspect list
                #if gid in self.m_suspect_groups:
                    #del self.m_suspect_groups[gid]
                if dbug.LEV & dbug.FIELD: print "Field:group_check:Group",gid,\
                            "was lost and has been recreated"
            # if group exists, but is on suspect list
            elif gid in self.m_suspect_groups:
                # remove from suspect list
                del self.m_suspect_groups[gid]
                if dbug.LEV & dbug.FIELD: print "Field:group_check:Group",gid,\
                            "was suspected lost but is now above suspicion"

    def check_for_new_group(self, id, gid):
        """If this is a new group, disconnect the old one."""
        # find the old group id
        former_gid = self.m_cell_dict[id].m_gid
        # if the group has changed, remove the cell from former group list
        if gid != former_gid:
            # if the old group is not zero (no group) and not None (undef)
            if former_gid:
                # find the actual group we're referring to
                if former_gid in self.m_group_dict:
                    former_group =  self.m_group_dict[former_gid]
                    # now delete the cell ref in the group's cell list
                    if id in former_group.m_cell_dict:
                        del former_group.m_cell_dict[id]
                    # if the length of this list is zero, we can nix the group
                    if not len(former_group.m_cell_dict):
                        self.del_group(former_gid)
        #TODO: When do we send the osc notice?

    def check_for_missing_cell(self, id):
        """Check for missing or suspect cell, handle it.

        Possibilities:
            * Cell does not exist:
                create it, remove from suspect list, update it, increment
                count, and refresh any connectors that point to it
            * Cell exists, but is on the suspect list
                remove from suspect list, increment count
            * Cell exists in master list and is not suspect:
                update its info; count unchanged
        """
        # if cell does not exist:
        if not id in self.m_cell_dict:
            # create it and increment count
            self.create_cell(id)
            # remove from suspect list
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            if dbug.LEV & dbug.FIELD: print "Field:cell_check:Cell",id,\
                        "was lost and has been recreated"
        # if cell exists, but is on suspect list
        elif id in self.m_suspect_cells:
            # remove from suspect list
            del self.m_suspect_cells[id]
            # increment count
            self.m_our_cell_count += 1
            if dbug.LEV & dbug.FIELD: print "Field:cell_check:Cell",id,\
                        "was suspected lost but is now above suspicion"

    def check_for_missing_conx(self, cid, uid0, uid1):
        """Check for missing or suspect conx, handle it.

        Possibilities:
            * Conx does not exist:
                create it, remove from suspect list, update it, increment
                count, and refresh any connectors that point to it
            * Conx exists, but is on the suspect list
                remove from suspect list, increment count
            * Conx exists in master list and is not suspect:
                update its info; count unchanged
        """
        # if conx does not exist:
        if not cid in self.m_conx_dict:
            # create it and increment count
            self.create_connector(uid0, uid1)

    def is_cell_good_to_go(self, id):
        """Test if cell is good to be rendered.
        Returns True if cell is on master list and not suspect.
        """
        if not id in self.m_cell_dict:
            return False
        if id in self.m_suspect_cells:
            return False
        cell = self.m_cell_dict[id]
        if not cell.m_visible or cell.m_x is None or cell.m_y is None:
            return False
        return True

    def is_conx_good_to_go(self, id):
        """Test if conx is good to be rendered.
        Returns True if cell is on master list and not suspect.
        """
        if not id in self.m_conx_dict:
            return False
        connector = self.m_conx_dict[id]
        if not connector.m_visible:
            return False
        if not self.is_cell_good_to_go(connector.m_cell0.m_id) or \
           not self.is_cell_good_to_go(connector.m_cell1.m_id):
            return False
        if connector.m_cell0.m_gid and \
           (connector.m_cell0.m_gid == connector.m_cell1.m_gid):
            return False
        return True

    def is_group_good_to_go(self, id):
        """Test if group is good to be rendered.
        Returns True if group is on master list and not suspect.
        """
        if id not in self.m_group_dict:
            return False
        if id in self.m_suspect_groups:
            return False
        if self.m_group_dict[id].m_x is None or self.m_group_dict[id].m_y is None:
            return False
        return True

    def check_for_lost_cell(self, uid):
        time_since_last_update = time() - self.m_cell_dict[uid].m_updatetime
        if time_since_last_update > MAX_LOST_PATIENCE:
            if dbug.LEV & dbug.FIELD: 
                print "Field:renderCell:Cell",\
                    "%d is suspected lost for %.2f sec"%\
                    (uid,time_since_last_update)
            self.del_cell(uid)

    def check_for_abandoned_cells(self):
        """Check to see if any cells have been abandoned."""
        # we make a copy because we can't iterate over the dict if we are
        # deleting stuff from it!
        new_cell_dict = self.m_cell_dict.copy()
        for uid,cell in new_cell_dict.iteritems():
            self.check_for_lost_cell(uid)
