#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visual subsystem module contains main loop and majority of important classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "visualsys.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import logging
import warnings 
import time
import daemon
import pprint
from random import randint
from itertools import chain
import random

# installed modules
import pyglet
from pyglet.window import key
import numpy

# local modules
import config
import pathfinder
from gridmap import GridMap
from pathfinder import PathFinder
import bezier
import oschandlers

# constants
LOGFILE = config.logfile
DEF_RADIUS = config.default_radius
DEF_ORIENT = config.default_orient
DEF_LINECOLOR = config.default_linecolor
DEF_BLOBCOLOR = config.default_blobcolor
DEF_GUIDECOLOR = config.default_guidecolor
DEF_BKGDCOLOR = config.default_bkgdcolor
DRAW_BLOBS = config.draw_blobs

RAD_PAD = config.radius_padding     # increased radius of circle around blobs
CURVE_SEGS = config.curve_segments  # number of line segs in a curve

XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field
XMIN_VECTOR = config.xmin_vector
YMIN_VECTOR = config.ymin_vector
XMAX_VECTOR = config.xmax_vector
YMAX_VECTOR = config.ymax_vector
XMIN_SCREEN = config.xmin_screen
YMIN_SCREEN = config.ymin_screen
XMAX_SCREEN = config.xmax_screen
YMAX_SCREEN = config.ymax_screen
DEF_MARGIN = config.default_margin
MODE_SCREEN = 0
MODE_VECTOR = 1
PATH_UNIT = config.path_unit
BLOCK_FUZZ = config.fuzzy_area_for_cells

MIN_CONX_DIST = config.minimum_connection_distance

MAX_LOST_PATIENCE = config.max_lost_patience

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
        self.m_still_running = True
        self.m_our_cell_count = 0
        self.m_reported_cell_count = 0
        # we could use a list here which would make certain things easier, but
        # we need to do deletions and references pretty regularly.
        # TODO: Consider making these dict into lists
        self.m_cell_dict = {}
        self.m_connector_dict = {}
        # a hash of counts of missing connectors, indexed by id
        self.m_suspect_conxs = {}
        # a hash of counts of missing cells, indexed by id
        self.m_suspect_cells = {}
        #self.allpaths = []
        self.setScaling((XMIN_FIELD,YMIN_FIELD), (XMAX_FIELD,YMAX_FIELD), 
                         (XMIN_VECTOR,YMIN_VECTOR), (XMAX_VECTOR,YMAX_VECTOR), 
                         (XMIN_SCREEN,YMIN_SCREEN), (XMAX_SCREEN,YMAX_SCREEN), 
                         PATH_UNIT, MODE_SCREEN)
        self.makePathGrid()

    # Screen stuff

    def initScreen(self):
        # initialize pyglet 
        #(xmax_screen,ymax_screen) = self.screenMax()
        #self.m_screen = pyglet.window.Window(width=xmax_screen,height=ymax_screen)
        width = self.m_xmax_screen - self.m_xmin_screen
        height = self.m_ymax_screen - self.m_ymin_screen
        print "field:initScreen"
        #pygopt = 'debug_gl'
        #pyglet.options[pygopt] = True
        #print "pyglet.options[",pygopt,"] = ",pyglet.options[pygopt]
        #pygopt = 'debug_gl_trace'
        #pyglet.options[pygopt] = True
        #print "pyglet.options[",pygopt,"] = ",pyglet.options[pygopt]
        #pygopt = 'debug_trace'
        #pyglet.options[pygopt] = True
        #print "pyglet.options[",pygopt,"] = ",pyglet.options[pygopt]
        self.m_screen = pyglet.window.Window(width=width,height=height,\
                             resizable=True,visible=False)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        # ... perform some additional initialisation
        pyglet.gl.glClearColor(*DEF_BKGDCOLOR)
        self.m_screen.clear()
        # register draw routing with pyglet
        # TESTED: These functions are being called correctly, and params are
        # being passed correctly
        self.m_screen.on_draw = self.on_draw
        self.m_screen.on_resize = self.on_resize
        self.m_screen.on_key_press = self.on_key_press
        self.m_screen.set_minimum_size(XMAX_SCREEN/4, YMAX_SCREEN/4)
        self.m_screen.set_visible()

    # pyglet stuff

    def resizeScreen(self):
        width = self.m_xmax_screen - self.m_xmin_screen
        height = self.m_ymax_screen - self.m_ymin_screen
        self.m_screen.set_size(width, height)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0

    def on_window_close(self,window):
        print "field:on_window_close"
        self.m_still_running = False
        event_loop.exit()
        return pyglet.event.EVENT_HANDLED

    def on_resize(self, width, height):
        self.setScaling(pmin_screen=(0,0),pmax_screen=(width,height))
        print "Field:on_resize:width=",width,"height=",height

    def on_draw(self):
        start = time.clock()
        #self.calcDistances()
        #self.resetPathGrid()
        #self.pathScoreCells()
        #self.pathfindConnectors()
        self.m_screen.clear()
        self.renderAll()
        self.drawAll()
        #print "draw loop in",(time.clock() - start)*1000,"ms"

    def on_key_press(self, symbol, modifiers):
        MOVEME = 25
        print "key press.",
        if symbol == pyglet.window.key.SPACE:
            print "SPACE"
            self.m_screen.clear()
            self.renderAll()
            return
        elif symbol == pyglet.window.key.LEFT:
            print "LEFT"
            rx = -MOVEME
            ry = 0
        elif symbol == pyglet.window.key.RIGHT:
            print "RIGHT"
            rx = MOVEME
            ry = 0
        elif symbol == pyglet.window.key.UP:
            print "UP"
            rx = 0
            ry = MOVEME
        elif symbol == pyglet.window.key.DOWN:
            print "DOWN"
            rx = 0
            ry = -MOVEME
        else:
            return
        # move cell
        #playcell.m_location = (playcell.m_location[0]+rx, playcell.m_location[1]+ry)

    # Scaling

    def setScaling(self,pmin_field=None,pmax_field=None,pmin_vector=None,pmax_vector=None,
                      pmin_screen=None,pmax_screen=None,path_unit=None,output_mode=None):
        """Set up scaling in the field.

        A word about graphics scaling:
         * The vision tracking system (our input data) measures in meters.
         * The laser DAC measures in uh, int16? -32,768 to 32,768
         * Pyglet measures in pixels at the screen resolution of the window you create
         * The pathfinding units are each some ratio of the smallest expected radius

         So we will keep eveything internally in centemeters (so we can use ints
         instead of floats), and then convert it to the appropriate units before 
         display depending on the output mode

         """

        if pmin_field is not None:
            self.m_xmin_field = pmin_field[0]
            self.m_ymin_field = pmin_field[1]
        if pmax_field is not None:
            self.m_xmax_field = pmax_field[0]
            self.m_ymax_field = pmax_field[1]
        if pmin_vector is not None:
            self.m_xmin_vector = pmin_vector[0]
            self.m_ymin_vector = pmin_vector[1]
        if pmax_vector is not None:
            self.m_xmax_vector  = pmax_vector[0]
            self.m_ymax_vector  = pmax_vector[1]
        if pmin_screen is not None:
            self.m_xmin_screen = pmin_screen[0]
            self.m_ymin_screen = pmin_screen[1]
        if pmax_screen is not None:
            self.m_xmax_screen = pmax_screen[0]
            self.m_ymax_screen = pmax_screen[1]
        if path_unit is not None:
            self.m_path_unit = path_unit
            self.m_path_scale = float(1)/path_unit
        if output_mode is not None:
            self.m_output_mode = output_mode
        xmin_field = self.m_xmin_field
        ymin_field = self.m_ymin_field
        xmax_field = self.m_xmax_field
        ymax_field = self.m_ymax_field
        xmin_vector = self.m_xmin_vector
        ymin_vector = self.m_ymin_vector
        xmax_vector = self.m_xmax_vector
        ymax_vector = self.m_ymax_vector
        xmin_screen = self.m_xmin_screen
        ymin_screen = self.m_ymin_screen
        xmax_screen = self.m_xmax_screen
        ymax_screen = self.m_ymax_screen

        # in order to find out how to display this,
        #   1) we find the aspect ratio (x/y) of the screen or vector (depending on the
        #      mode). 
        #   2) Then if the aspect ratio (x/y) of the reported field is greater, we
        #      set the x axis to stretch to the edges of screen (or vector) and then use
        #      that value to determine the scaling.
        #   3) But if the aspect ratio (x/y) of the reported field is less than,
        #      we set the y axis to stretch to the top and bottom of screen (or
        #      vector) and use that value to determine the scaling.

        # our default margins, one will be overwriten below
        self.m_xmargin = int(xmax_screen*DEF_MARGIN)
        self.m_ymargin = int(ymax_screen*DEF_MARGIN)

        # aspect ratios used only for comparison
        field_aspect = float(xmax_field-xmin_field)/(ymax_field-ymin_field)
        if self.m_output_mode == MODE_SCREEN:
            display_aspect = float(xmax_screen-xmin_screen)/(ymax_screen-ymin_screen)
        else:
            display_aspect = float(xmax_vector-xmin_vector)/(ymax_vector-ymin_vector)
        if field_aspect > display_aspect:
            print "Longer in the x dimension"
            field_xlen=xmax_field-xmin_field
            if field_xlen:
                self.m_vector_scale = \
                    float(xmax_vector-xmin_vector)/field_xlen
                self.m_screen_scale = \
                    float(xmax_screen-xmin_screen-(self.m_xmargin*2))/field_xlen
                self.m_ymargin = \
                    int(((ymax_screen-ymin_screen)-((ymax_field-ymin_field)*self.m_screen_scale)) / 2)
        else:
            print "Longer in the y dimension"
            field_ylen=ymax_field-ymin_field
            if field_ylen:
                self.m_vector_scale = \
                    float(ymax_vector-ymin_vector)/field_ylen
                self.m_screen_scale = \
                    float(ymax_screen-ymin_screen-(self.m_ymargin*2))/field_ylen
                self.m_xmargin = \
                    int(((xmax_screen-xmin_screen)-((xmax_field-xmin_field)*self.m_screen_scale)) / 2)
        #print "Field dims:",(xmin_field,ymin_field),(xmax_field,ymax_field)
        print "Screen dims:",(xmin_screen,ymin_screen),(xmax_screen,ymax_screen)
        #print "Screen scale:",self.m_screen_scale
        #print "Screen margins:",(self.m_xmargin,self.m_ymargin)
        print "Used screen space:",self.rescale_pt2out((xmin_field,ymin_field)),self.rescale_pt2out((xmax_field,ymax_field))

    # Everything

    def renderAll(self):
        """Render all the cells and connectors."""
        self.renderAllCells()
        self.renderAllConnectors()

    def drawAll(self):
        """Draw all the cells and connectors."""
        self.drawGuides()
        #self.drawAllCells()
        #self.drawAllConnectors()

    # Guides

    def drawGuides(self):
        # draw boundaries of field (if in screen mode)
        if self.m_output_mode == MODE_SCREEN:
            pyglet.gl.glColor3f(DEF_GUIDECOLOR[0],DEF_GUIDECOLOR[1],DEF_GUIDECOLOR[2])
            points = [(self.m_xmin_field,self.m_ymin_field),
                      (self.m_xmin_field,self.m_ymax_field),
                      (self.m_xmax_field,self.m_ymax_field),
                      (self.m_xmax_field,self.m_ymin_field)]
            #print "boundary points (field):",points
            index = [0,1,1,2,2,3,3,0]
            screen_pts = self.rescale_pt2out(points)
            #print "boundary points (screen):",screen_pts
            # boundary points (screen): [(72, 73), (72, 721), (1368, 721), (1368, 73)]
            #print "proc screen_pts:",tuple(chain(*screen_pts))
            # proc screen_pts: (72, 73, 72, 721, 1368, 721, 1368, 73)
            #print "PYGLET:pyglet.graphics.draw_indexed(",len(screen_pts),", pyglet.gl.GL_LINES,"
            #print "           ",index
            #print "           ('v2i',",tuple(chain(*screen_pts)),"),"
            #print "       )"
            # TESTED: This callis sending the correct params
            pyglet.graphics.draw_indexed(len(screen_pts), pyglet.gl.GL_LINES,
                index,
                ('v2i',tuple(chain(*screen_pts))),
            )
            #point = (self.m_xmin_field,self.m_ymin_field)
            #radius = self.rescale_num2out(DEF_RADIUS)
            #shape = Circle(self,point,radius,DEF_LINECOLOR,solid=False)
            #shape.render()
            #shape.draw()
            #print "Field:drawGuides"

    # Cells

    def createCell(self, id):
        """Create a cell.  """
        # create cell - note we pass self since we want a back reference to
        # field instance
        # If it already exists, don't create it
        if not id in self.m_cell_dict:
            cell = Cell(self, id)
            # add to the cell list
            self.m_cell_dict[id] = cell
            self.m_our_cell_count += 1
            print "Field:createCell:count:",self.m_our_cell_count
        # but if it already exists
        else:
            # let's make sure it is no longer suspect
            if id in self.m_suspect_cells:
                print "Field:createCell:Cell",id,"was suspected lost but is now above suspicion"
                del self.m_suspect_cells[id]

    def updateCell(self, id, p=None, r=None, orient=None, effects=None, color=None):
        """ Update a cells information.

        Possibilities:
            * Cell does not exist:
                create it, remove from suspect list, update it, increment count
            * Cell exists, but is on the suspect list
                remove from suspect list, increment count
            * Cell exists in master list and is not suspect:
                update its info; count unchanged
        """ 
        if effects is None:
            effects = []
        # if cell does not exist:
        if not id in self.m_cell_dict:
            # create it and increment count
            self.createCell(id)
            # remove from suspect list
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            print "Field:updateCell:Cell",id,"was lost and has been recreated"
        # if cell exists, but is on suspect list
        elif id in self.m_suspect_cells:
            # remove from suspect list
            del self.m_suspect_cells[id]
            # increment count
            self.m_our_cell_count += 1
            print "Field:updateCell:Cell",id,"was suspected lost but is now above suspicion"
        # update cell's info
        self.m_cell_dict[id].update(p, r, orient, effects, color)

    def isCellGoodToGo(self, id):
        """Test if cell is good to be rendered.
        Returns True if cell is on master list and not suspect.
        """
        if not id in self.m_cell_dict:
            return False
        if id in self.m_suspect_cells:
            return False
        if self.m_cell_dict[id].m_location is None:
            return False
        return True

    def delCell(self, id):
        """Delete a cell.
        We used to delete all of it's connections, now we just delete it and
        let the connector sort it out. This allows us to defer connector
        deletion -- instead we keep a cound of suspicious connectors. That way, 
        if the cells reappear, we can reconnect them without losing their
        connectors.
        """
        #cell = self.m_cell_dict[id]
        # delete all cell's connectors from master list of connectors
        #for conxid in cell.m_connector_dict:
        #    if conxid in self.m_connector_dict:
        #        del self.m_connector_dict[conxid]
        # have cell disconnect all of its connections and refs
        # Note: connector checks if cell still exists before rendering
        if id in self.m_cell_dict:
            #cell.cellDisconnect()
            # delete from the cell master list of cells
            print "Field:delCell:deleting",id
            del self.m_cell_dict[id]
            if id in self.m_suspect_cells:
                del self.m_suspect_cells[id]
            else:
                self.m_our_cell_count -= 1
            print "Field:delCell:count:",self.m_our_cell_count

    def checkPeopleCount(self,reported_count):
        self.m_reported_cell_count = reported_count
        our_count = self.m_our_cell_count
        print "Field:checkPeopleCount:count:",our_count,"- Reported:",self.m_reported_cell_count
        if reported_count != our_count:
            print "Field:checkPeopleCount:Count mismatch"
            self.hideAllCells()
            self.m_out_cell_count = 0

    def hideCell(self, id):
        """Hide a cell.
        We don't delete cells unless we have to.
        Instead we add them to a suspect list (actually a count of how
        suspicous they are)
        """
        self.m_suspect_cells[id] = 1
        self.m_our_cell_count -= 1
        print "Field:hideCell:count:",self.m_our_cell_count

    def hideAllCells(self):
        print "Field:hideAllCells"
        for id in self.m_cell_dict:
            self.hideCell(id)

    def renderCell(self,cell):
        """Render a cell.

        We first check if the cell is good.
        If not, we increment its suspect count
        If yes, render it.
        """
        if self.isCellGoodToGo(cell.m_id):
            cell.render()
            #del self.m_suspect_cells[cell.m_id]
        else:
            print "Field:renderCell:Cell",cell.m_id,"is suspected lost for",\
                  self.m_suspect_cells[cell.m_id],"frames"
            if self.m_suspect_cells[cell.m_id] > MAX_LOST_PATIENCE:
                self.delCell(cell.m_id)
            else:
                self.m_suspect_cells[cell.m_id] += 1

    def renderAllCells(self):
        # we don't call the Cell's render-er directly because we have some
        # logic here at this level
        for cell in self.m_cell_dict.values():
            self.renderCell(cell)

    def drawCell(self,cell):
        cell.draw()

    def drawAllCells(self):
        # we don't call the Cell's draw-er directly because we may want
        # to introduce logic at this level
        for cell in self.m_cell_dict.values():
            self.drawCell(cell)

    # Connectors

    def createConnector(self, id, cell0, cell1):
        # create connector - note we pass self since we want a back reference
        # to field instance
        # NOTE: Connector class takes care of storing the cells as well as
        # telling each of the two cells that they now have a connector
        connector = Connector(self, id, cell0, cell1)
        # add to the connector list
        self.m_connector_dict[id] = connector

    def delConnector(self,conxid):
        if conxid in self.m_connector_dict:
            # make sure the cells that this connector is attached to, delete
            # refs to it
            self.m_connector_dict[id].conxDisconnectThyself()
            # delete from the connector list
            del self.m_connector_dict[conxid]

    def renderConnector(self,connector):
        """Render a connector.

        We first check if the connector's two cells are both good.
        If not, we increment its suspect count
        If yes, render it.
        """
        if self.isCellGoodToGo(connector.m_cell0.m_id) and \
           self.isCellGoodToGo(connector.m_cell1.m_id):
            connector.render()
            if connector.m_id in self.m_suspect_conxs:
                del self.m_suspect_conxs[connector.m_id]
        else:
            print "Field:renderConnector:Conx",connector.m_id,"between",\
                connector.m_cell0.m_id,"and",connector.m_cell1.m_id,"is suspected lost"
            if self.m_suspect_conxs[connector.m_id] > MAX_LOST_PATIENCE:
                self.delConnector(connector.m_id)
            else:
                self.m_suspect_conxs[connector.m_id] += 1

    def renderAllConnectors(self):
        # we don't call the Connector's render-er directly because we have some
        # logic here at this level
        for connector in self.m_connector_dict.values():
            self.renderConnector(connector)

    def drawConnector(self,connector):
        connector.draw()

    def drawAllConnectors(self):
        # we don't call the Connector's draw-er directly because we may want
        # to introduce logic at this level
        for connector in self.m_connector_dict.values():
            self.drawConnector(connector)

    # Distances - TODO: temporary -- this info will come from the conduction subsys

    def dist_sqd(self,cell0,cell1):
        return ((cell0.m_location[0]-cell1.m_location[0])**2 + 
                (cell0.m_location[1]-cell1.m_location[1])**2)

    def calcDistances(self):
        self.distance = {}
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

    # Paths

    # should the next two functions be in the gridmap module? No, because the GridMap
    # and Pathfinder classes have to be instantiated from somewhere. And if not
    # here they have to be called from the main loop. Better here.
    def makePathGrid(self):
        # for our pathfinding, we're going to overlay a grid over the field with
        # squares that are sized by a constant in the config file
        self.path_grid = GridMap(self.scale2path(self.m_xmax_field),
                                 self.scale2path(self.m_ymax_field))
        self.pathfinder = PathFinder(self.path_grid.successors, self.path_grid.move_cost, 
                                     self.path_grid.estimate)

    def resetPathGrid(self):
        self.path_grid.reset_grid()
        # we store the results of all the paths, why? Not sure we need to anymore
        #self.allpaths = []

    def pathScoreCells(self):
        #print "***Before path: ",self.m_cell_dict
        for cell in self.m_cell_dict.values():
            self.path_grid.set_blocked(self.scale2path(cell.m_location),\
                                    self.scale2path(cell.m_radius),BLOCK_FUZZ)

    def pathfindConnectors(self):
        """ Find path for all the connectors.

        We sort the connectors by distance and do easy paths for the closest 
        ones first.
        """
        #connector_dict_rekeyed = self.m_connector_dict
        #for i in connector_dict_rekeyed.iterkeys():
        connector_dict_rekeyed = {}
        for connector in self.m_connector_dict.values():
            p0 = connector.m_cell0.m_location
            p1 = connector.m_cell1.m_location
            # normally we'd take the sqrt to get the distance, but here this is 
            # just used as a sort comparison, so we'll not take the hit for sqrt
            score = ((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) 
            # here we save time by sorting as we go through it
            connector_dict_rekeyed[score] = connector
        for i in sorted(connector_dict_rekeyed.iterkeys()):
            connector = connector_dict_rekeyed[i]
            print "findpath--id:",connector.m_id,"dist:",i**0.5
            connector.addPath(self.findPath(connector))

    def findPath(self, connector):
        """ Find path in path_grid and then scale it appropriately."""
        start = self.scale2path(connector.m_cell0.m_location)
        goal = self.scale2path(connector.m_cell1.m_location)
        # TODO: Either here or in compute_path we first try several simple/dumb
        # paths, reserving A* for the ones that are blocked and need more
        # smarts. We sort the connectors by distance and do easy paths for the
        # closest ones first.
        #path = list(self.path_grid.easy_path(start, goal))
        #print "connector:id",connector.m_id,"path:",path
        #if not path:
        path = list(self.pathfinder.compute_path(start, goal))
        # take results of found paths and block them on the map
        self.path_grid.set_block_line(path)
        #self.allpaths = self.allpaths + path
        return self.path2scale(path)
        
    def printGrid(self):
        self.path_grid.printme()
    # Scaling conversions

    def _convert(self,obj,scale,min1,min2):
        """Recursively converts numbers in an object.

        This function accepts single integers, tuples, lists, or combinations.

        """
        if isinstance(obj, (int, float)):
            #return(int(obj*scale) + min)
            return(int((obj-min1)*scale) + min2)
        elif isinstance(obj, list):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min1,min2))
            return mylist
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min1,min2))
            return tuple(mylist)

    def scale2out(self,n):
        """Convert internal unit (cm) to units usable for the vector or screen. """
        if self.m_output_mode == MODE_SCREEN:
            return self._convert(n,self.m_screen_scale,self.m_xmin_field,self.m_xmin_screen)
        return self._convert(n,self.m_vector_scale,self.m_xmin_field,self.m_xmin_vector)

    def scale2path(self,n):
        """Convert internal unit (cm) to units usable for pathfinding. """
        return self._convert(n,self.m_path_scale,self.m_xmin_field,0)

    def path2scale(self,n):
        """Convert pathfinding units to internal unit (cm). """
        #print "m_path_scale",self.m_path_scale
        return self._convert(n,1/self.m_path_scale,0,self.m_xmin_field)

    def _rescale_pts(self,obj,scale,orig_pmin,new_pmin):
        """Recursively rescales points or lists of points.

        This function accepts single integers, tuples, lists, or combinations.

        """
        # if this is a point, rescale it
        if isinstance(obj, tuple) and len(obj) == 2 and \
           isinstance(obj[0], (int,float)) and isinstance(obj[1], (int,float)):
            x = int((obj[0]-orig_pmin[0])*scale) + new_pmin[0]
            y = int((obj[1]-orig_pmin[1])*scale) + new_pmin[1]
            return (x,y)
        # if this is a list, examine each element, return list
        elif isinstance(obj, (list,tuple)):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i,scale,orig_pmin,new_pmin))
            return mylist
        # if this is a tuple, examine each element, return tuple
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i,scale,orig_pmin,new_pmin))
            return tuple(mylist)
        # otherwise, we don't know what to do with it, return it
        # TODO: Consider throwing an exception
        else:
            print "ERROR: Can only rescale a point, not",obj
            return obj

    def rescale_pt2out(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (self.m_xmin_field,self.m_ymin_field)
        if self.m_output_mode == MODE_SCREEN:
            scale = self.m_screen_scale
            new_pmin = (self.m_xmin_screen+self.m_xmargin,self.m_ymin_screen+self.m_ymargin)
        else:
            scale = self.m_screen_vector
            new_pmin = (self.m_xmin_vector,self.m_ymin_vector)
        return self._rescale_pts(p,scale,orig_pmin,new_pmin)

    def rescale_num2out(self,n):
        """Convert num in internal units (cm) to units usable for the vector or screen. """
        if self.m_output_mode == MODE_SCREEN:
            scale = self.m_screen_scale
        else:
            scale = self.m_screen_vector
        return n*scale


# basic data elements

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

    def __init__(self,field,effects=None, color=DEF_LINECOLOR):
        if effects is None:
            effects = []
        self.m_field=field
        self.m_leffects=effects
        self.m_color=color
        self.m_shape = object
        # TODO: init points, index, color

    def addEffects(self, effects):
        self.m_leffects += effects
        
    def applyEffects(self):
        pass

    def draw(self):
        self.m_shape.draw()


class Cell(GraphElement):

    """Represents one person/object on the floor.

    Create a cell as a subclass of the basic data element.
    
    Stores the following values:
        m_location: center of cell
        m_orient: orientation from the default (DEF_ORIENT)

    setLocation: set the location value for this cell as an XY tuple
    setOrient: set the orientation for this cell from 12:00 in degrees
    makeBasicShape: create the set of arcs that will define the shape

    """

    def __init__(self, field, id, p=(), r=DEF_RADIUS, orient=DEF_ORIENT,
            effects=None, color=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
        if effects is None:
            effects = []
        self.m_id = id
        self.m_location = p
        self.m_blob_radius = r
        self.m_blob_color = DEF_BLOBCOLOR
        self.m_radius = r*RAD_PAD
        self.m_oriend = orient
        self.m_visible = True
        self.m_connector_dict = {}
        GraphElement.__init__(self,field,effects,color)

    def update(self, p=None, r=None, orient=None, effects=None, color=None):
        """Store basic info and create a GraphElement object"""
        if p is not None:
            self.m_location = p
        if r is not None:
            self.m_blob_radius = r
            self.m_radius = r*RAD_PAD
        if orient is not None:
            self.m_oriend = orient
        if effects is not None:
            self.m_leffects = effects
        if color is not None:
            self.m_color = color

    def setLocation(self, p):
        self.m_location=p

    def setOrient(self, orient):
        self.m_orient=orient

    def addConnector(self, connector):
        self.m_connector_dict[connector.m_id] = connector

    def delConnector(self, connector):
        if connector.m_id in self.m_connector_dict:
            del self.m_connector_dict[connector.m_id]

    def render(self):
        self.m_shape = Circle(self.m_field,self.m_location,self.m_radius,
                              self.m_color,solid=False)
        self.m_shape.render()
        if DRAW_BLOBS:
            self.m_blobshape = Circle(self.m_field,self.m_location,self.m_blob_radius,
                                  self.m_blob_color,solid=True)
            self.m_blobshape.render()

    def draw(self):
        self.m_shape.draw()
        if DRAW_BLOBS:
            self.m_blobshape.draw()

    def cellDisconnect(self):
        """Disconnects all the connectors and refs it can reach.
        
        To actually delete it, remove it from the list of cells in the Field
        class.
        """
        print "Disconnecting cell",self.m_id
        # we make a copy because we can't iterate over the dict if we are
        # deleting stuff from it!
        new_connector_dict = self.m_connector_dict.copy()
        # for each connector attached to this cell...
        for connector in new_connector_dict.values():
            # OPTION: for simplicity's sake, we do the work rather than passing to
            # the object to do the work
            # delete the connector from its two cells
            if connector.m_id in connector.m_cell0.m_connector_dict:
                del connector.m_cell0.m_connector_dict[connector.m_id]
            if connector.m_id in connector.m_cell1.m_connector_dict:
                del connector.m_cell1.m_connector_dict[connector.m_id]
            # delete cells ref'd from this connector
            connector.m_cell0 = None
            connector.m_cell1 = None
            # now delete from this cell's list
            if connector.m_id in self.m_connector_dict:
                del self.m_connector_dict[connector.m_id]

            # OPTION: Let the objects do the work
            #connector.conxDisconnectThyself()
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

    def __init__(self, field, id, cell0, cell1, effect=None, color=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
        if effect is None:
            effect = []
        self.m_id = id
        # store the cells we are connected to
        self.m_cell0 = cell0
        self.m_cell1 = cell1
        # tell the cells themselves that they now own a connector
        cell0.addConnector(self)
        cell1.addConnector(self)
        self.m_path = []
        self.m_score = 0
        GraphElement.__init__(self,field,effect,color)

    def addPath(self,path):
        """Record the path of this connector."""
        self.m_path = path

    def render(self):
        loc0 = self.m_cell0.m_location
        loc1 = self.m_cell1.m_location
        rad0 = self.m_cell0.m_radius
        rad1 = self.m_cell1.m_radius
        self.m_shape = Line(self.m_field,loc0,loc1,rad0,rad1,self.m_color,self.m_path)
        #print ("Render Connector(%s):%s to %s" % (self.m_id,cell0.m_location,cell1.m_location))
        self.m_shape.render()

    def conxDisconnectThyself(self):
        """Disconnect cells this connector refs & this connector ref'd by them.
        
        To actually delete it, remove it from the list of connectors in the Field
        class.
        """
        print "Disconnecting connector",self.m_id,"between",\
                self.m_cell0.m_id,"and",self.m_cell1.m_id
        # for simplicity's sake, we do the work rather than passing to
        # the object to do the work
        # delete the connector from its two cells
        if self.m_id in self.m_cell0.m_connector_dict:
            del self.m_cell0.m_connector_dict[self.m_id]
        if self.m_id in self.m_cell1.m_connector_dict:
            del self.m_cell1.m_connector_dict[self.m_id]
        # delete the refs to those two cells
        self.m_cell0 = None
        self.m_cell1 = None

# graphic primatives

class GraphicObject(object):

    """Basic graphic object primative"""

    def __init__(self, field, points, index, color):
        """Graphic object constructor.

            Args:
                arcpoints - list of points that define the graphic object
                arcindex - list of indicies to arcpoints
                color - list of colors of each arc
        """
        self.m_field = field
        self.m_arcpoints = points
        self.m_arcindex = index
        self.m_color = color
        # each arc is broken down into a list of points and indecies
        # these are gathered into lists of lists
        # TODO: possibly these could be melded into single dim lists
        self.m_points = []
        self.m_index = []

    def render(self):
        # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
        # e.g., self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
        #print "self.m_arcpoints = ",self.m_arcpoints
        #print "self.m_arcindex = ",self.m_arcindex

        for i in range(len(self.m_arcindex)):
            # e.g., self.m_arcindex[i] = (0,1,2,3)
            p0 = self.m_arcpoints[self.m_arcindex[i][0]]
            p1 = self.m_arcpoints[self.m_arcindex[i][1]]
            p2 = self.m_arcpoints[self.m_arcindex[i][2]]
            p3 = self.m_arcpoints[self.m_arcindex[i][3]]
            # if this is a straight line, don't chop into cubicSplines
            if p0[0] == p1[0] == p2[0] == p3[0] or \
                    p0[1] == p1[1] == p2[1] == p3[1]:
                points = [p0,p1,p2,p3]
                index = [0,1,1,2,2,3]
                # TODO: convert CURVE_SEGS into a passable parameter, so in the
                # case of a straight line, we pass t=1 so it makes ONE slice
            else:
                (points,index) = cubicSpline(p0,p1,p2,p3,CURVE_SEGS)
            self.m_points.append(points)
            self.m_index.append(index)

    def draw(self):
        #print "points:",self.m_points
        #print "index:",self.m_index
        for i in range(len(self.m_index)):
            points = self.m_points[i]
            #print "Points:",points
            scaled_pts = self.m_field.rescale_pt2out(points)
            #print "Scaled_pts:",scaled_pts
            index = self.m_index[i]
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            pyglet.graphics.draw_indexed(len(scaled_pts), pyglet.gl.GL_LINES,
                index,
                ('v2i',tuple(chain(*scaled_pts))),
            )
        

class Circle(GraphicObject):

    """Define circle object."""

    def __init__(self, field, p, r, color,solid=False):
        """Circle constructor.

        Args:
            p - center point
            r - radius of circle
            c - color
        """
        self.m_center = p
        self.m_radius = r
        self.m_solid = solid
        k = 0.5522847498307935  # 4/3 (sqrt(2)-1)
        kr = int(r*k)
        (x,y)=p
        arcpoints=[(x+r,y),(x+r,y+kr), (x+kr,y+r), (x,y+r),
                           (x-kr,y+r), (x-r,y+kr), (x-r,y),
                           (x-r,y-kr), (x-kr,y-r), (x,y-r),
                            (x+kr,y-r), (x+r,y-kr)]
        arcindex=[(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, 9), (9, 10, 11, 0)]
        GraphicObject.__init__(self,field,arcpoints,arcindex,color)

    def render(self):
        # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
        # e.g., self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
        #print "self.m_arcpoints = ",self.m_arcpoints
        #print "self.m_arcindex = ",self.m_arcindex
        for i in range(len(self.m_arcindex)):
            # e.g., self.m_arcindex[i] = (0,1,2)
            p0 = self.m_arcpoints[self.m_arcindex[i][0]]
            p1 = self.m_arcpoints[self.m_arcindex[i][1]]
            p2 = self.m_arcpoints[self.m_arcindex[i][2]]
            p3 = self.m_arcpoints[self.m_arcindex[i][3]]
            (points,index) = cubicSpline(p0,p1,p2,p3,CURVE_SEGS)
            if self.m_solid:
                points.append(self.m_center)
                nxlast_pt = len(points)-2
                last_pt = len(points)-1
                xtra_index = [nxlast_pt,last_pt,last_pt,0]
                index = index + xtra_index
            self.m_points.append(points)
            self.m_index.append(index)

    def draw(self):
        for i in range(len(self.m_index)):
            points = self.m_points[i]
            #print "Points:",points
            scaled_pts = self.m_field.rescale_pt2out(points)
            #print "Scaled_pts:",scaled_pts
            index = self.m_index[i]
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            if not self.m_solid:
                pyglet.graphics.draw_indexed(len(scaled_pts), pyglet.gl.GL_LINES,
                    index,
                    ('v2i',tuple(chain(*scaled_pts))),
                )
            else:
                pyglet.graphics.draw_indexed(len(scaled_pts), pyglet.gl.GL_POLYGON,
                    index,
                    ('v2i',tuple(chain(*scaled_pts))),
                )

class Line(GraphicObject):

    """Define line object."""

    def __init__(self, field, p0, p1, r0, r1, color, path=[]):
        """Line constructor.

        Args:
            p0 - srating point
            p1 - ending point
            color - color of line
        """

        def midpoint(p1, p2):
            return (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))

        def makeArc(p1,p2):
            midpt = midpoint(p1,p2)
            return (p1,midpt,midpt,p2)

        def inCircle(center, radius, p):
            square_dist = (center[0] - p[0]) ** 2 + (center[1] - p[1]) ** 2
            return square_dist < radius ** 2

        def findIntersect(outpt, inpt, center, radius):
            # Here instead of checking whether the point is on the circle, 
            # we just see if the points have converged on each other.
            sum_dist = abs(inpt[0] - outpt[0]) + abs(inpt[1] - outpt[1])
            #print "sum dist:",sum_dist
            if sum_dist < 2:
                return inpt
            midpt = midpoint(outpt, inpt)
            if inCircle(center, radius, midpt):
                return findIntersect(outpt, midpt, center, radius)
            else:
                return findIntersect(midpt, inpt, center, radius)

        (x0,y0)=p0
        (x1,y1)=p1
        """
        straight lines between cells
        lp = [(x0,y0),(x1,y1)]
        i = [(0,1)]
        c = [c]
        """
        # if we were given a path, we will use it
        n = len(path) - 1
        index = [0] + [int(x * 0.5) for x in range(2, n*2)] + [n]
        lastpt = []
        npath = []
        arcpoints = []
        arcindex = []
        for i in range(0, len(path)-1):
            thispt = path[i]
            nextpt = path[i+1]
            # Remove parts of path within the radius of cell
            # TODO: Ensure that the logic here works in every case
            # if both ends of this line segment are inside a circle fugetaboutit
            if (inCircle(p0, r0, thispt) and inCircle(p0, r0, nextpt)) or\
                (inCircle(p1, r1, thispt) and inCircle(p1, r1, nextpt)):
                continue
            # if near end of this line segment is inside a circle
            if inCircle(p0, r0, thispt):
                # find the point intersecting the circle
                thispt = findIntersect(nextpt, thispt, p0, r0)
            # if far end of this line segment is inside the other circle
            elif inCircle(p1, r1, nextpt):
                # find the point intersecting the circle
                nextpt = findIntersect(thispt, nextpt, p1, r1)
            """
            # if one end of this line segment is inside a circle
            if inCircle(p1, r1, thispt) and not inCircle(p1, r1, nextpt):
                # find the point intersecting the circle
                thispt = findIntersect(thispt, nextpt, p1, r1)
            # if one end of this line segment is inside the other circle
            if inCircle(p0, r0, nextpt) and not inCircle(p0, r0, thispt):
                # find the point intersecting the circle
                nextpt = findIntersect(nextpt, thispt, p0, r0)
            """
            # if neither point is inside one of our circles, use it
            #print path[i],"inside cell"
            # take segment of two points, and transform to three point arc
            arc = makeArc(thispt,nextpt)
            npath.append(arc[0])
            npath.append(arc[1])
            lastpt = arc[2]
            npath.append(lastpt)
            #print "npath:", npath
            arcpoints = npath
            arcindex = [(x-3,x-2,x-1,x) for x in range(3,len(npath),3)]
            #print "arcpoints:", arcpoints
            #print "arcindex:", arcindex
        GraphicObject.__init__(self,field,arcpoints,arcindex,color)


# spline code

def quadX(t, p0, p1, p2):
    #print "points:",p0[0],p1[0],p2[0]," t:",t
    return  int((1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0])

def quadY(t, p0, p1, p2):
    #print "points:",p0[1],p1[1],p2[1]," t:",t
    return int((1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

def quadSpline(p0, p1, p2, nSteps):
    """Returns a list of line segments and an index to make the full curve.

    Cubics are defined as a start point (p0) and end point (p2) and
    a control point (p1) and a parameter t that goes from 0.0 to 1.0.
    The parameter is sample nSteps times.

    NOTE: Technically, these are called Quadratic Bezier splines
    """
    lineSegments = []
    for i in range(nSteps+1):
        # the definition of the spline means the parameter t goes
        # from 0.0 to 1.0
        t = i / float(nSteps)
        x = quadX(t, p0, p1, p2)
        y = quadY(t, p0, p1, p2)
        lineSegments.append((x,y))
    #lineSegments.append(p2)
    quadIndex = [0] + [int(x * 0.5) for x in range(2, (nSteps)*2)] + [nSteps]
    return (lineSegments,quadIndex)

def cubicSpline(p0, p1, p2, p3, nSteps):
    """Returns a list of line segments and an index to make the full curve.

    Cubics are defined as a start point (p0) and end point (p3) and
    control points (p1 & p2) and a parameter t that goes from 0.0 to 1.0.
    """
    points = numpy.array([p0, p1, p2, p3])
    bez = bezier.Bezier_Curve( points )
    lineSegments = []
    for val in numpy.linspace( 0, 1, nSteps ):
        #print '%s: %s' % (val, bez( val ))
        # the definition of the spline means the parameter t goes
        # from 0.0 to 1.0
        (x,y) = bez(val)
        lineSegments.append((int(x),int(y)))
    #lineSegments.append(p2)
    cubicIndex = [0] + [int(x * 0.5) for x in range(2, (nSteps-1)*2)] + [nSteps-1]
    #print "lineSegments = ",lineSegments
    #print "cubicIndex = ",cubicIndex
    return (lineSegments,cubicIndex)

# effect elements

class Effect(object):

    """An effect to the quality of a line."""

    # self.m_

    def evaluate(self, prim):
        pass


class EffectDouble(Effect):

    def __init__(self, stuff):
        #work out init values that will effect this
        pass

    def evaluate(self, prim):
        # do double
        return prim



if __name__ == "__main__":


    # initialize field
    field = Field()
    # initialize pyglet 
    field.initScreen()

    # generate test data
    rmin = 20
    rmax = 70
    xmin_field = rmax
    xmax_field = XMAX_FIELD-rmax
    ymin_field = rmax
    ymax_field = YMAX_FIELD-rmax
    people = 6
    connections = 6

    # make cells
    #cell_list=[]
    for i in range(people):
        cell = field.createCell(i)
        p = (randint(xmin_field,xmax_field), randint(ymin_field,ymax_field))
        r = randint(rmin,rmax)
        field.updateCell(i,p,r)

    # make connectors
    connector_list=[]
    for i in range(connections):
        cell0 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        #print "cell0:",cell0.m_id," loc:",cell0.m_location
        cell1 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        while cell0 == cell1:
            cell1 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        #print "cell1:",cell1.m_id," loc:",cell1.m_location
        field.createConnector(i,cell0,cell1)

    playcell = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]

    #for connector in field.m_connector_dict.values():
        #connector.addPath(field.findPath(connector))
    #field.printGrid()

    pyglet.app.run()


    """
    realizing I can't create the classes until I know how I'm going to use them,
    I'll pseudocode the control loop here at the highest level

    while True:
        for each tracking msg on OSC stack
            record the position,radius of cells
        for each conductor msg on OSC stack
            record new connectors
            record style,intensity for cells
            record style,intensity for connectors
            record the rollcall
        for each of the cells in the rollcall
            draw them
        for each of the connectors with two cells in the rollcall
            draw them
    """
