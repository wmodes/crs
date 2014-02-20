#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related Space is an interactive multimedia installation that engages the themes of presence, interaction, and place. Using motion tracking, laser light and a generative soundscape, it encourages interactions between participants, visually and sonically transforming a regularly trafficked space. Co-related Space highlights participants' active engagement and experimentation with sound and light, including complex direct and indirect behavior and relationships."""
 
__appname__ = "crs-visual.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"
 

# imports
import logging
import warnings 
import time
import daemon
import pprint
import copysign from math

import config


# constants
LOGFILE = config.logfile
DEF_RADIUS = config.default_radius
DEF_ORIENT = config.default_orient
DEF_COLOR = config.default_color


# create logger
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=LOGFILE,level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')

 
# basic data elements

class GraphElement(object):

    """Basic data element represented by cells and connectors.

    Stores the following values
        m_color: color of this element (DEF_COLOR)
        m_leffects: list of effects

    addEffect: add an effect to the list of effects that will act on this
        object
    applyEffects: apply all the effects in the list to the arcs that make
        up this object

    """

    def __init__(self,effect=[],c=DEF_COLOR):
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

    def __init__(self, id, p, r=DEF_RADIUS, orient=DEF_ORIENT, effect=[], c=DEF_COLOR):
        """Store basic info and create a GraphElement object"""
        self.m_id=id
        self.m_location=p
        self.m_radius=r
        self.m_oriend=orient
        # does Cell have to call GraphElement to get teh defaults set?
        GraphElement.__init__(self,effect,c)

    def setLocation(self, p):
        self.m_location=p

    def setOrient(self, orient):
        self.m_orient=orient

    # Do I want these here as functions that draw stuff, or do I want to do it
    # outside of this class?

    def makeBasicShape(self):
        self.shape = Circle(self.m_location,self.m_radius,self.m_color)
        return(self.shape)

    def draw(shape):
        pass
        

class Connector(GraphElement):

    """Represents a connector between two cells.

    Create a connector as a subclass of the basic data element.
    
    Stores the following values:
        m_cells: the two cells connected by this connector

    makeBasicShape: create the set of arcs that will define the shape

    """

    def __init__(self, cell0, cell1):
        """Store basic info and create a GraphElement object"""
        self.m_cells=(cell0,cell1)

    def makeBasicShape(self):
        loc0 = self.m_cells[0].m_location
        loc1 = self.m_cells[1].m_location
        rad0 = self.m_cells[0].m_radius
        rad1 = self.m_cells[1].m_radius
        self.shape = Line(loc0,loc1,rad0,rad1,self.m_color)
        return(self.shape)

    def draw(shape):
        pass
        


# graphic primatives

class GraphicObject(object):

    """Basic graphic object primative"""

    def __init__(self, lp, i, c):
        """Graphic object constructor.

            Args:
                lp - list of points that define the graphic object
        """
        self.m_points = lp
        self.m_arcindex = i
        self.m_color = c

class Circle(GraphicObject):

    """Define circle object."""

    def __init__(self, p, r, c):
        """Circle constructor.

        Args:
            p - center point
            r - radius of circle
            c - color
        """
        (x,y)=p
        lp=[(x,y-r),(x+r,y-r),(x+r,y),(x+r,y+r),(x,y+r),(x-r,y+r),(x-r,y),(x-r,y-r)]
        i=[(0,1,2),(2,3,4),(4,5,6),(6,7,0)]
        c=[c,c,c,c]
        GraphicObject.__init__(self,lp,i,c)

class Line(GraphicObject):

    """Define line object."""

    def __init__(self, p0, p1, r0, r1, c):
        """Line constructor.

        Args:
            p0 - srating point
            p1 - ending point
            c - color
        """
        (x0,y0)=p0
        (x1,y1)=p1
        # get position of p1 relative to p0 
        vx = copysign(1,x1-x0)  # rel x pos vector as 1 or -1
        vy = copysign(1,y1-y0)  # rel y pos vector as 1 or -1
        xdif = abs(x0 - x1)
        ydif = abs(y0 - y1)
        if (xdif > ydif) {
            xmid = x0 + vx*xdif/2
            arc0 = makeArc((x0 + vx*r0,y0),(xmid,y0))
            arc1 = makeArc((xmid,y0),(xmid,y1))
            arc2 = makeArc((xmid,y1),(x1 - vx*r1,y1))
        }
        else {
            ymid = y0 + vy*ydif/2
            arc0 = makeArc((x0,y0 + vy*r0),(x0,ymid))
            arc1 = makeArc((x0,ymid),(x1,ymid))
            arc2 = makeArc((x1,ymid),(x1,y1 - vy*r1))
        }
        lp = [arc0[0],arc0[1],arc0[2],arc1[1],arc2[0],arc2[1],arc2[2])
        i=[(0,1,2),(2,3,4),(4,5,6)]
        c=[c,c,c]

        GraphicObject.__init__(self,lp,i,c)

        def makeArc(p1,p2):
            return (p1,midpoint(p1,p2),p2)

        def midpoint(p1, p2):
            return Point((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)


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


# test stuff

circle=Circle((0,0),10,"ffffff")
pprint.pprint(circle.m_points)
print "\n"
cell=Cell(1,(0,0))
pprint.pprint(cell)
print "\n"
new_circle=cell.getBasicArcs()
pprint.pprint(new_circle)

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
