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


# constants
LOGFILE = config.logfile
DEF_RADIUS = config.default_radius
DEF_ORIENT = config.default_orient
DEF_LINECOLOR = config.default_linecolor
DEF_BLOBCOLOR = config.default_blobcolor
DEF_BKGDCOLOR = config.default_bkgdcolor
DRAW_BLOBS = config.draw_blobs

RAD_PAD = config.radius_padding     # increased radius of circle around blobs
CURVE_SEGS = config.curve_segments  # number of line segs in a curve

XMIN = config.xmin
YMIN = config.ymin
XMAX = config.xmax
YMAX = config.ymax
MIN_LASER = config.min_laser
MAX_LASER = config.max_laser
MIN_SCREEN = config.min_screen
MAX_SCREEN = config.max_screen
MODE_SCREEN = 0
MODE_LASER = 1
PATH_UNIT = config.path_unit
BLOCK_FUZZ = config.fuzzy_area_for_cells

MIN_CONX_DIST = config.minimum_connection_distance

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
        self.m_cell_dict = {}
        self.m_connector_dict = {}
        #self.allpaths = []
        self.initScaling((XMIN,YMIN), (XMAX,YMAX), 
                         (MIN_LASER,MIN_LASER), (MAX_LASER,MAX_LASER), 
                         (MIN_SCREEN,MIN_SCREEN), (MAX_SCREEN,MAX_SCREEN), 
                         PATH_UNIT, MODE_SCREEN)
        self.makePathGrid()

    def initScreen(self):
        # initialize pyglet 
        (xmax,ymax) = self.screenMax()
        self.m_screen = pyglet.window.Window(width=xmax,height=ymax)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        pyglet.gl.glClearColor(*DEF_BKGDCOLOR)

    def updateScreen(self):
        # initialize pyglet 
        (xmax,ymax) = self.screenMax()
        self.m_screen.set_size(xmax, ymax)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        pyglet.gl.glClearColor(*DEF_BKGDCOLOR)

    # Cells

    def createCell(self, id):
        # create cell - note we pass self since we want a back reference to
        # feild instance
        cell = Cell(self, id)
        # add to the cell list
        self.m_cell_dict[id] = cell

    def updateCell(self, id, p=(), r=0, orient=0, effects=[], color=0):
        cell = self.m_cell_dict[id]
        cell.update(p, r, orient, effects, color)

    def delCell(self, id):
        # delete all connectors from master list of connectors
        #for connector in cell.m_connector_dict.values():
            #del self.m_connector_dict[connector.m_id]
        # have cell disconnect all of its connections and refs
        self.m_cell_dict[id].cellDisconnect()
        # delete the cell master list of cells
        del self.m_cell_dict[id]

    def renderCell(self,cell):
        cell.render()

    def drawCell(self,cell):
        cell.draw()

    def renderAllCells(self):
        for cell in self.m_cell_dict.values():
            cell.render()

    def drawAllCells(self):
        for cell in self.m_cell_dict.values():
            cell.draw()

    # Connectors

    def createConnector(self, id, cell0, cell1):
        # create connector - note we pass self since we want a back reference
        # to field instance
        # NOTE: Connector class takes care of storing the cells as well as
        # telling each of the two cells that they now have a connector
        connector = Connector(self, id, cell0, cell1)
        # add to the connector list
        self.m_connector_dict[id] = connector

    def delConnector(self,id):
        connector = self.m_connector_dict[id]
        # delete the connector in the cells attached to the connector
        connector.conxDisconnect()
        # delete from the connector list
        del self.m_connector_dict[id]

    def renderConnector(self,connector):
        connector.render()

    def drawConnector(self,cell):
        connector.draw()

    def renderAllConnectors(self):
        for connector in self.m_connector_dict.values():
            connector.render()

    def drawAllConnectors(self):
        for connector in self.m_connector_dict.values():
            connector.draw()

    # Everything

    def renderAll(self):
        """Render all the cells and connectors."""
        self.renderAllCells()
        self.renderAllConnectors()

    def drawAll(self):
        """Draw all the cells and connectors."""
        self.drawAllCells()
        self.drawAllConnectors()

    # Distances - TODO: temporary -- this info will come from the conduction subsys

    def dist_sqd(self,cell0,cell1):
        return ((cell0.m_location[0]-cell1.m_location[0])**2 + 
                (cell0.m_location[1]-cell1.m_location[1])**2)

    def resetDistances(self):
        self.distance = {}

    def calcDistances(self):
        for cell0 in self.m_cell_dict.values():
            for cell1 in self.m_cell_dict.values():
                conxid = str(cell0.m_id)+'.'+str(cell1.m_id)
                conxid_ = str(cell1.m_id)+'.'+str(cell0.m_id)
                #if self.distance[conxid] == 0:
                if cell0 != cell1:
                    dist = self.dist_sqd(cell0,cell1)
                    #print "Calculating distance",conxid,"dist:",dist
                    self.distance[conxid] = dist
                    self.distance[conxid_] = dist
                    #self.distance[str(cell1.m_id)+'.'+str(cell0.m_id)] = dist
                    if dist < MIN_CONX_DIST:
                        self.createConnector(conxid,cell0,cell1)

    # Paths

    # should the next two functions be in the gridmap module? No, because the GridMap
    # and Pathfinder classes have to be instantiated from somewhere. And if not
    # here they have to be called from the main loop. Better here.
    def makePathGrid(self):
        # for our pathfinding, we're going to overlay a grid over the field with
        # squares that are sized by a constant in the config file
        self.path_grid = GridMap(self.scale2path(self.m_xmax),
                                 self.scale2path(self.m_ymax))
        self.pathfinder = PathFinder(self.path_grid.successors, self.path_grid.move_cost, 
                                     self.path_grid.estimate)

    def resetPathGrid(self):
        self.path_grid.reset_grid()
        # we store the results of all the paths, why? Not sure we need to anymore
        #self.allpaths = []

    def pathScoreCells(self):
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
        path = list(self.path_grid.easy_path(start, goal))
        #print "connector:id",connector.m_id,"path:",path
        if not path:
            path = list(self.pathfinder.compute_path(start, goal))
        # take results of found paths and block them on the map
        self.path_grid.set_block_line(path)
        #self.allpaths = self.allpaths + path
        return self.path2scale(path)
        
    def printGrid(self):
        self.path_grid.printme()

    # Scaling

    def initScaling(self,pmin,pmax,pmin_laser,pmax_laser,
                    pmin_screen,pmax_screen,path_unit,mode):
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
        self.m_xmin = xmin = pmin[0]
        self.m_ymin = ymin = pmin[1]
        self.m_xmax = xmax = pmax[0]
        self.m_ymax = ymax = pmax[1]
        self.m_min_laser = min_laser = pmin_laser[0]
        self.m_max_laser  = max_laser = pmax_laser[0]
        self.m_min_screen = min_screen = pmin_screen[0]
        self.m_max_screen = max_screen = pmax_screen[0]
        self.m_mode = mode
        self.m_path_unit = path_unit
        if xmax > ymax:
            self.m_laser_scale = float(max_laser-min_laser)/(xmax-xmin)
            self.m_screen_scale = float(max_screen-min_screen)/(xmax-xmin)
        else:
            self.m_laser_scale = float(max_laser-min_laser)/(ymax-ymin)
            self.m_screen_scale = float(max_screen-min_screen)/(ymax-ymin)
        #print "path unit:",path_unit," path_scale:",float(1)/path_unit
        self.m_path_scale = float(1)/path_unit
        #print "SCREEN SCALE:",self.m_screen_scale
        #print "REAL SCALING:",(xmin,ymin),(xmax,ymax)
        #print "SCREEN SCALING:",self.scale2out((xmin,ymin)),self.scale2out((xmax,ymax))
        #print "SCREEN SCALING(alt):",self.screenMax()

    def updateScaling(self,pmin=0,pmax=0,pmin_laser=0,pmax_laser=0,
                      pmin_screen=0,pmax_screen=0):
        """Update scaling in the field. """
        if pmin:
            self.m_xmin = pmin[0]
            self.m_ymin = pmin[1]
        if pmax:
            self.m_xmax = pmax[0]
            self.m_ymax = pmax[1]
        if pmin_laser:
            self.m_min_laser = pmin_laser[0]
        if pmax_laser:
            self.m_max_laser  = pmax_laser[0]
        if pmin_screen:
            self.m_min_screen = pmin_screen[0]
        if pmax_screen:
            self.m_max_screen = pmax_screen[0]
        xmin = self.m_xmin
        ymin = self.m_ymin
        xmax = self.m_xmax
        ymax = self.m_ymax
        min_laser = self.m_min_laser
        max_laser = self.m_max_laser
        min_screen = self.m_min_screen
        max_screen = self.m_max_screen
        if xmax > ymax:
            self.m_laser_scale = float(max_laser-min_laser)/(xmax-xmin)
            self.m_screen_scale = float(max_screen-min_screen)/(xmax-xmin)
        else:
            self.m_laser_scale = float(max_laser-min_laser)/(ymax-ymin)
            self.m_screen_scale = float(max_screen-min_screen)/(ymax-ymin)
        #print "SCREEN SCALE:",self.m_screen_scale
        #print "REAL SCALING:",(xmin,ymin),(xmax,ymax)
        #print "SCREEN SCALING:",self.scale2out((xmin,ymin)),self.scale2out((xmax,ymax))
        #print "SCREEN SCALING(alt):",self.screenMax()

    def laserMax(self):
        return (int((self.m_xmax-self.m_xmin)*self.m_laser_scale) + self.m_min_laser,
            int((self.m_ymax-self.m_ymin)*self.m_laser_scale) + self.m_min_laser)

    def screenMax(self):
        return (int((self.m_xmax-self.m_xmin)*self.m_screen_scale) + self.m_min_screen,
            int((self.m_ymax-self.m_ymin)*self.m_screen_scale) + self.m_min_screen)

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
        """Convert internal unit (cm) to units usable for the laser or screen. """
        if self.m_mode == MODE_SCREEN:
            return self._convert(n,self.m_screen_scale,self.m_xmin,self.m_min_screen)
        return self._convert(n,self.m_laser_scale,self.m_xmin,self.m_min_laser)

    def scale2path(self,n):
        """Convert internal unit (cm) to units usable for pathfinding. """
        return self._convert(n,self.m_path_scale,self.m_xmin,0)

    def path2scale(self,n):
        """Convert pathfinding units to internal unit (cm). """
        #print "m_path_scale",self.m_path_scale
        return self._convert(n,1/self.m_path_scale,0,self.m_xmin)


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

    def __init__(self,field,effects=[], color=DEF_LINECOLOR):
        self.m_field=field
        self.m_leffects=effects
        self.m_color=color
        # TODO: init points, index, color

    def addEffects(self, effects):
        self.m_leffect += effects
        
    def applyEffects():
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
            effects=[], color=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
        self.m_id = id
        self.m_location = p
        self.m_blob_radius = r
        self.m_blob_color = DEF_BLOBCOLOR
        self.m_radius = r*RAD_PAD
        self.m_oriend = orient
        self.m_visible = True
        self.m_connector_dict = {}
        GraphElement.__init__(self,field,effects,color)

    def update(self, p=(), r=0, orient=0, effects=[], color=0):
        """Store basic info and create a GraphElement object"""
        if p:
            self.m_location = p
        if r:
            self.m_blob_radius = r
            self.m_radius = r*RAD_PAD
        if orient:
            self.m_oriend = orient
        if effects:
            self.m_leffects = effects
        if color:
            self.m_color = color

    def setLocation(self, p):
        self.m_location=p

    def setOrient(self, orient):
        self.m_orient=orient

    def addConnector(self, connector):
        self.m_connector_dict[connector.m_id] = connector

    def delConnector(self, connector):
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
        new_connector_dict = self.m_connector_dict.copy()
        # for each connector attached to this cell...
        for connector in new_connector_dict.values():
            # OPTION: for simplicity's sake, we do the work rather than passing to
            # the object to do the work
            # delete the connector from its two cells
            del connector.m_cell0.m_connector_dict[connector.m_id]
            del connector.m_cell1.m_connector_dict[connector.m_id]
            # delete cells ref'd from this connector
            connector.m_cell0 = None
            connector.m_cell1 = None
            # now delete from this cell's list
            del self.m_connector_dict[connector.m_id]

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

    def __init__(self, field, id, cell0, cell1, effect=[], color=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
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

    def conxDisconnect(self):
        """Disconnect cells this connector refs & this connector ref'd by them.
        
        To actually delete it, remove it from the list of connectors in the Field
        class.
        """
        print "Disconnecting connector",self.m_id,"between",\
                self.m_cell0.m_id,"and",self.m_cell1.m_id
        # OPTION: for simplicity's sake, we do the work rather than passing to
        # the object to do the work
        # delete the connector from its two cells
        del self.m_cell0.m_connector_dict[self.m_cell0.m_id]
        del self.m_cell1.m_connector_dict[self.m_cell1.m_id]
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
            index = self.m_index[i]
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            pyglet.graphics.draw_indexed(len(points), pyglet.gl.GL_LINES,
                index,
                ('v2i',self.m_field.scale2out(tuple(chain(*points)))),
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
            index = self.m_index[i]
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            if not self.m_solid:
                pyglet.graphics.draw_indexed(len(points), pyglet.gl.GL_LINES,
                    index,
                    ('v2i',self.m_field.scale2out(tuple(chain(*points)))),
                )
            else:
                pyglet.graphics.draw_indexed(len(points), pyglet.gl.GL_POLYGON,
                    index,
                    ('v2i',self.m_field.scale2out(tuple(chain(*points)))),
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

        def findIntersect(inpt, outpt, center, radius):
            # Here instead of checking whether the point is on the circle, 
            # we just see if the points have converged on each other.
            sum_dist = abs(inpt[0] - outpt[0]) + abs(inpt[1] - outpt[1])
            #print "sum dist:",sum_dist
            if sum_dist <= 2:
                return inpt
            midpt = midpoint(inpt, outpt)
            if inCircle(center, radius, midpt):
                return findIntersect(midpt, outpt, center, radius)
            else:
                return findIntersect(inpt,midpt, center, radius)

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
            # if both ends of this line segment are inside a circle fugetaboutit
            if (inCircle(p0, r0, thispt) and inCircle(p0, r0, nextpt)) or\
                (inCircle(p1, r1, thispt) and inCircle(p1, r1, nextpt)):
                continue
            # if one end of this line segment is inside a circle
            if inCircle(p0, r0, thispt) and not inCircle(p0, r0, nextpt):
                # find the point intersecting the circle
                thispt = findIntersect(thispt, nextpt, p0, r0)
            # if one end of this line segment is inside the other circle
            if inCircle(p1, r1, nextpt) and not inCircle(p1, r1, thispt):
                # find the point intersecting the circle
                nextpt = findIntersect(nextpt, thispt, p1, r1)
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
    xmin = rmax
    xmax = XMAX-rmax
    ymin = rmax
    ymax = YMAX-rmax
    people = 10
    connections = 7

    # make cells
    #cell_list=[]
    for i in range(people):
        cell = field.createCell(i)
        p = (randint(xmin,xmax), randint(ymin,ymax))
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

    def on_draw():
        start = time.clock()
        field.resetDistances()
        field.calcDistances()
        field.resetPathGrid()
        field.pathScoreCells()
        field.pathfindConnectors()
        field.m_screen.clear()
        field.renderAll()
        field.drawAll()
        #print "draw loop in",(time.clock() - start)*1000,"ms"

    field.m_screen.on_draw = on_draw
    #visualsys.pyglet.app.run()

    def on_key_press(symbol, modifiers):
        MOVEME = 25
        print "key press.",
        if symbol == pyglet.window.key.SPACE:
            print "SPACE"
            field.m_screen.clear()
            field.renderAll()
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
        playcell.m_location = (playcell.m_location[0]+rx, playcell.m_location[1]+ry)

    field.m_screen.on_key_press = on_key_press
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
