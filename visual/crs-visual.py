#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related Space is an interactive multimedia installation that engages the themes of presence, interaction, and place. Using motion tracking, laser light and a generative soundscape, it encourages interactions between participants, visually and sonically transforming a regularly trafficked space. Co-related Space highlights participants' active engagement and experimentation with sound and light, including complex direct and indirect behavior and relationships."""
 
__appname__ = "crs-visual.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"
 

# core modules
import logging
import warnings 
import time
import daemon
import pprint
from math import copysign
from random import randint
from itertools import chain
import random

# installed modules
import pyglet

# local modules
import config
import pathfinder
from gridmap import GridMap
from pathfinder import PathFinder


# constants
LOGFILE = config.logfile
DEF_RADIUS = config.default_radius
DEF_ORIENT = config.default_orient
DEF_LINECOLOR = config.default_linecolor
DEF_BLOBCOLOR = config.default_blobcolor
DEF_BKGDCOLOR = config.default_bkgdcolor

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

    def addCell(self,cell):
        self.m_cell_dict[cell.m_id] = cell

    def delCell(self,cell):
        del self.m_cell_list[cell.m_id]

    def addConnector(self,connector):
        self.m_connector_dict[connector.m_id] = connector
        connector.m_cells[0].addConnector(connector)
        connector.m_cells[1].addConnector(connector)

    def delConnector(self,connector):
        del self.m_connector_list[connector.m_id]

    # should this shit be in the pathfinding module? If so, I'd have to pass
    # all the info it has access to here in Field
    def makePathGrid(self):
        # for our pathfinding, we're going to overlay a grid over the field with
        # squares that are sized by a constant in the config file
        self.path_grid = GridMap(self.scale2path(self.m_xmax),
                            self.scale2path(self.m_ymax))
        self.pathfinder = PathFinder(self.path_grid.successors, self.path_grid.move_cost, 
                                self.path_grid.estimate)

    def pathScoreCells(self):
        for key, cell in self.m_cell_dict.iteritems():
            #print "cell:",cell.m_id," radius:",cell.m_radius,"cm pathscaled:",\
                #self.scale2path(cell.m_radius)
            self.path_grid.set_blocked(self.scale2path(cell.m_location),\
                                    self.scale2path(cell.m_radius*RAD_PAD),BLOCK_FUZZ)

    def initScaling(self,xmin,ymin,xmax,ymax,min_laser,max_laser,
            min_screen,max_screen,path_unit,mode):
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
        self.m_xmin = xmin
        self.m_ymin = ymin
        self.m_xmax = xmax
        self.m_ymax = ymax
        self.m_min_laser = min_laser
        self.m_max_laser  = max_laser 
        self.m_min_screen = min_screen
        self.m_max_screen = max_screen
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

    def laserMax(self):
        return (int(self.m_xmax*self.m_laser_scale) + self.m_min_laser,
            int(self.m_ymax*self.m_laser_scale) + self.m_min_laser)

    def screenMax(self):
        return (int(self.m_xmax*self.m_screen_scale) + self.m_min_screen,
            int(self.m_ymax*self.m_screen_scale) + self.m_min_screen)

    def _convert(self,obj,scale,min):
        """Recursively converts numbers in an object.

        This function accepts single integers, tuples, lists, or combinations.

        """
        if isinstance(obj, (int, float)):
            return(int(obj*scale) + min)
        elif isinstance(obj, list):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min))
            return mylist
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min))
            return tuple(mylist)

    def scale2out(self,n):
        """Convert internal unit (cm) to units usable for the laser or screen. """
        if self.m_mode == MODE_SCREEN:
            return self._convert(n,self.m_screen_scale,self.m_min_screen)
        return self._convert(n,self.m_laser_scale,self.m_min_laser)

    def scale2path(self,n):
        """Convert internal unit (cm) to units usable for pathfinding. """
        return self._convert(n,self.m_path_scale,0)

    def path2scale(self,n):
        """Convert internal unit (cm) to units usable for pathfinding. """
        print "m_path_scale",self.m_path_scale
        return self._convert(n,1/self.m_path_scale,0)


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

    def __init__(self,field,effect=[],c=DEF_LINECOLOR):
        self.m_field=field
        self.m_leffects=effect
        self.m_color=c

    def addEffect(self, effect):
        self.m_leffect.append=effect
        
    def applyEffects():
        pass


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

    def __init__(self, field, id, p, r=DEF_RADIUS, orient=DEF_ORIENT,
            effect=[], c=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
        self.m_id=id
        self.m_location=p
        self.m_radius=r
        self.m_oriend=orient
        self.m_connector_dict = {}
        # does Cell have to call GraphElement to get teh defaults set?
        GraphElement.__init__(self,field,effect,c)

    def setLocation(self, p):
        self.m_location=p

    def setOrient(self, orient):
        self.m_orient=orient

    def addConnector(self, connector):
        self.m_connector_dict[connector.m_id] = connector

    def delConnector(self, connector):
        del self.m_connector_list[connector.m_id]

    """def makeBasicShape(self):
        self.shape = Circle(self.m_location,self.m_radius,self.m_color)
        return(self.shape)
        """

    def drawCell(self,color=0):
        if not color:
            color = DEF_LINECOLOR 
        shape = Circle(self.m_field,self.m_location,self.m_radius*RAD_PAD,color)
        shape.draw()
        return(shape)

    def drawBlob(self,color=0):
        if not color:
            color = DEF_LINECOLOR 
        shape = Circle(self.m_field,self.m_location,self.m_radius,color)
        shape.drawSolid()
        return(shape)


class Connector(GraphElement):

    """Represents a connector between two cells.

    Create a connector as a subclass of the basic data element.
    
    Stores the following values:
        m_cells: the two cells connected by this connector

    makeBasicShape: create the set of arcs that will define the shape

    """

    def __init__(self, field, id, cell0, cell1, effect=[], c=DEF_LINECOLOR):
        """Store basic info and create a GraphElement object"""
        self.m_id=id
        self.m_cells=(cell0,cell1)
        GraphElement.__init__(self,field,effect,c)

    """def makeBasicShape(self):
        loc0 = self.m_cells[0].m_location
        loc1 = self.m_cells[1].m_location
        rad0 = self.m_cells[0].m_radius
        rad1 = self.m_cells[1].m_radius
        self.shape = Line(loc0,loc1,rad0,rad1,self.m_color)
        return(self.shape)
        """

    def draw(self,color=0):
        # TODO: Here we know how many connectors we have, and we can tell 
        # in what direction they go, we need to pass that info on to use it.
        # specifically, we want to jog the origin line in the direction 
        # it is going.
        if not color:
            color = self.m_color
        loc0 = self.m_cells[0].m_location
        loc1 = self.m_cells[1].m_location
        rad0 = self.m_cells[0].m_radius
        rad1 = self.m_cells[1].m_radius
        shape = Line(self.m_field,loc0,loc1,rad0,rad1,color)
        shape.draw()
        return(shape)


# graphic primatives

class Point(object):
    """Basic cartisian coordinate point object"""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Arc(object):
    """Basic arc object"""

    def __init__(self,p1,p2,p3,c):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.c = c


class Arc(object):

    """Basic arc object"""

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

    def draw(self):
        # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10),(5,5)]
        # e.g., self.m_arcindex = [(0,1,2),(2,3,4),(4,5,6),(6,7,0)]
        #print "self.m_arcpoints = ",self.m_arcpoints
        #print "self.m_arcindex = ",self.m_arcindex

        for i in range(len(self.m_arcindex)):
            # e.g., self.m_arcindex[i] = (0,1,2)
            p0 = self.m_arcpoints[self.m_arcindex[i][0]]
            p1 = self.m_arcpoints[self.m_arcindex[i][1]]
            p2 = self.m_arcpoints[self.m_arcindex[i][2]]
            (lp,index) = cubicSpline(p0,p1,p2,CURVE_SEGS)
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            #print "list:",tuple(chain(*lp))
            #print "convert:",self.m_field.scale2out(tuple(chain(*lp)))
            pyglet.graphics.draw_indexed(CURVE_SEGS, pyglet.gl.GL_LINES,
                index,
                ('v2i',self.m_field.scale2out(tuple(chain(*lp)))),
            )
        

class Circle(GraphicObject):

    """Define circle object."""

    def __init__(self, field, p, r, color):
        """Circle constructor.

        Args:
            p - center point
            r - radius of circle
            c - color
        """
        self.m_center = p
        self.m_radius = r
        (x,y)=p
        arcpoints=[(x,y-r),(x+r,y-r),(x+r,y),(x+r,y+r),(x,y+r),(x-r,y+r),(x-r,y),(x-r,y-r)]
        arcindex=[(0,1,2),(2,3,4),(4,5,6),(6,7,0)]
        GraphicObject.__init__(self,field,arcpoints,arcindex,color)

    def drawSolid(self):
        # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10),(5,5)]
        # e.g., self.m_arcindex = [(0,1,2),(2,3,4),(4,5,6),(6,7,0)]
        #print "self.m_arcpoints = ",self.m_arcpoints
        #print "self.m_arcindex = ",self.m_arcindex
        for i in range(len(self.m_arcindex)):
            # e.g., self.m_arcindex[i] = (0,1,2)
            p0 = self.m_arcpoints[self.m_arcindex[i][0]]
            p1 = self.m_arcpoints[self.m_arcindex[i][1]]
            p2 = self.m_arcpoints[self.m_arcindex[i][2]]
            (points,index) = cubicSpline(p0,p1,p2,CURVE_SEGS)
            points.append(self.m_center)
            nxlast_pt = len(points)-2
            last_pt = len(points)-1
            xtra_index = [nxlast_pt,last_pt,last_pt,0]
            index = index + xtra_index
            pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
            pyglet.graphics.draw_indexed(len(points), pyglet.gl.GL_POLYGON,
                index,
                ('v2i',self.m_field.scale2out(tuple(chain(*points)))),
                #('c3b',self.m_color*2)
            )
        

class Line(GraphicObject):

    """Define line object."""

    def __init__(self, field, p0, p1, r0, r1, color):
        """Line constructor.

        Args:
            p0 - srating point
            p1 - ending point
            color - color of line
        """

        def midpoint(p1, p2):
            return (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))

        def makeArc(p1,p2):
            return (p1,midpoint(p1,p2),p2)

        (x0,y0)=p0
        (x1,y1)=p1
        """
        straight lines between cells
        lp = [(x0,y0),(x1,y1)]
        i = [(0,1)]
        c = [c]
        """
        nr0 = r0*RAD_PAD
        nr1 = r1*RAD_PAD
        # get position of p1 relative to p0 
        vx = int(copysign(1,x1-x0))  # rel x pos vector as 1 or -1
        vy = int(copysign(1,y1-y0))  # rel y pos vector as 1 or -1
        xdif = abs(x0 - x1)
        ydif = abs(y0 - y1)
        if (xdif > ydif):
            xmid = x0 + vx*xdif/2
            arc0 = makeArc((x0 + vx*nr0,y0),(xmid,y0))
            arc1 = makeArc((xmid,y0),(xmid,y1))
            arc2 = makeArc((xmid,y1),(x1 - vx*nr1,y1))
        else:
            ymid = y0 + vy*ydif/2
            arc0 = makeArc((x0,y0 + vy*nr0),(x0,ymid))
            arc1 = makeArc((x0,ymid),(x1,ymid))
            arc2 = makeArc((x1,ymid),(x1,y1 - vy*nr1))
        arcpoints = [arc0[0],arc0[1],arc0[2],arc1[1],arc2[0],arc2[1],arc2[2]]
        arcindex=[(0,1,2),(2,3,4),(4,5,6)]

        GraphicObject.__init__(self,field,arcpoints,arcindex,color)

# spline code

def cubicX(t, p0, p1, p2):
    #print "points:",p0[0],p1[0],p2[0]," t:",t
    return  int((1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0])

def cubicY(t, p0, p1, p2):
    #print "points:",p0[1],p1[1],p2[1]," t:",t
    return int((1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

def cubicIndex(t):
    """Create point index for a contiguous series of t line segments. """
    index = []
    for i in range(t):
        index.append(i)
        if i != 0 and i != t-1:
            index.append(i)
    return index

def cubicSpline(p0, p1, p2, nSteps):
    """cubics are defined as a start point (p0) and end point (p2) and
    a control point (p1) and a parameter t that goes from 0.0 to 1.0.
    The parameter is sample nSteps times.

    Returns a list of line segments and an index to make the full curve
    """
    lineSegments = []
    for i in range(0, nSteps-1):
        # the definition of the spline means the parameter t goes
        # from 0.0 to 1.0
        t = i / float(nSteps)
        x = cubicX(t, p0, p1, p2)
        y = cubicY(t, p0, p1, p2)
        lineSegments.append((x,y))
    lineSegments.append(p2)
    return (lineSegments,cubicIndex(nSteps))

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

# pathfinder graph

"""
Creating a graph for A* pathfinding algorithm
* Divide space into points one standard diameter apart
* edges are at cardinal directions
* nodes are blocked when a cell diameter touches its center
* use modified A* for traversing nodes
"""

class PathNote(object):

    """A node object of the pathfinding graph

    Stores the following values:
        m_p: the location of the node as an (x,y) tuple
        m_block: a tag to indicate blocking

    """

    def __init__(self, p, block=False):
        self.m_p = p
        self.m_block = block

    def clearBlock(self):
        self.m_block = False

    def makeBlock(self):
        self.m_block = True

    def isBlocked(self):
        return(self.m_block)


class PathEdge(object):

    """An edge object of the pathfinding graph

    Stores the following values:
        m_cells: a tuple of two cells that form the ends of the edge
        m_block: a tag to indicate blocking

    """

    def __init__(self, nodes, block=False):
        self.m_nodes = nodes
        self.m_block = block

    def clearBlock(self):
        self.m_block = False

    def makeBlock(self):
        self.m_block = True

    def isBlocked(self):
        return(self.m_block)



class PathGraph(object):

    """Creates a graph of the entire field

    Creates all the nodes and edges of the graph
    
    Stores the following values:

    """

    def __init__(self, xmax, ymax):
        self.m_xmax = xmax
        self.m_ymax = ymax

    def evaluate(self, prim):
        # do double
        return prim


if __name__ == "__main__":

    # initialize field
    field = Field()
    field.initScaling(XMIN, YMIN, XMAX, YMAX, MIN_LASER, MAX_LASER, 
        MIN_SCREEN, MAX_SCREEN, PATH_UNIT, MODE_SCREEN)
    field.makePathGrid()

    # initialize pyglet 
    (xmax,ymax) = field.screenMax()
    window = pyglet.window.Window(width=xmax,height=ymax)
    # set window background color = r, g, b, alpha
    # each value goes from 0.0 to 1.0
    pyglet.gl.glClearColor(*DEF_BKGDCOLOR)

    # generate test data
    rmin = 35
    rmax = 70
    xmin = rmax
    xmax = XMAX-rmax
    ymin = rmax
    ymax = YMAX-rmax
    people = 6
    connections = 4

    # make cells
    #cell_list=[]
    for i in range(people):
        cell = Cell(field,i,(randint(xmin,xmax),randint(ymin,ymax)),randint(rmin,rmax))
        field.addCell(cell)

    # add cells to path 
    field.pathScoreCells()

    # make connectors
    connector_list=[]
    for i in range(connections):
        cell0 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        #print "cell0:",cell0.m_id," loc:",cell0.m_location
        cell1 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        while cell0 == cell1:
            cell1 = field.m_cell_dict[random.choice(field.m_cell_dict.keys())]
        print "cell1:",cell1.m_id," loc:",cell1.m_location
        connector = Connector(field,i,cell0,cell1)
        field.addConnector(connector)

    allpaths = []
    for key, connector in field.m_connector_dict.iteritems():
        start = field.scale2path(connector.m_cells[0].m_location)
        goal = field.scale2path(connector.m_cells[1].m_location)
        path = list(field.pathfinder.compute_path(start, goal))
        field.path_grid.set_block_line(path)
        allpaths = allpaths + path
        
    field.path_grid.printme(allpaths)

    @window.event
    def on_draw():
        window.clear()

        for key, cell in field.m_cell_dict.iteritems():
            cell.drawBlob(DEF_BLOBCOLOR)
            cell.drawCell()
        for key, connector in field.m_connector_dict.iteritems():
            connector.draw()

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
