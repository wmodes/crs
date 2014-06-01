#/usr/bin/env python
# -*- coding: utf-8 -*-
"""Graphic Element classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "circle.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from itertools import chain

# installed modules
import pyglet

# local modules
from shared import config
from shared import debug
import curves

# local classes

# constants
LOGFILE = config.logfile

LINEMODE = config.linemode
CURVE_SEGS = config.curve_segments  # number of line segs in a curve

GRAPHMODES = config.graphic_modes
GRAPHOPTS = {'screen': 1, 'osc': 2, 'etherdream':3}

OSCPATH = config.oscpath

# init debugging
dbug = debug.Debug()



class Circle(object):
    """Define circle object.

        Stores the following values:
            m_field: Stores the field for back referencing
            m_center: center point of circle ((float,float) in m)
            m_radius: radius of circle (float in m)
            m_color: color of circle
            m_solid: is this a solid (boolean)
            m_arcpoints: the points that make up the arcs
            m_arcindex: the index to connect the above arcpoints
            m_points: a list of points that make up the circle
            m_index: the index to connect the above points

        """

    def __init__(self):
        """Circle constructor."""
        self.m_field = None
        self.m_center = None
        self.m_radius = None
        self.m_color = None
        self.m_solid = False
        self.m_visible = True
        self.m_arcpoints = None
        self.m_arcindex = None
        # each arc is broken down into a list of points and indices
        # these are gathered into lists of lists
        # TODO: possibly these could be melded into single dim lists
        self.m_points = []
        self.m_index = []

    def update(self, field, p, r, color=None, solid=None, visible=None):
        """Circle constructor."""

        self.m_field = field
        self.m_center = p
        self.m_radius = r
        if color is not None:
            self.m_color = color
        if solid is not None:
            self.m_solid = solid
        if visible is not None:
            self.m_visible = visible

    def render(self):
        (x,y) = self.m_center
        r = self.m_radius
        k = 0.5522847498307935  # 4/3 (sqrt(2)-1)
        kr = r * k
        self.m_arcpoints = [(x+r,y), (x+r,y+kr), (x+kr,y+r), (x,y+r),
                           (x-kr,y+r), (x-r,y+kr), (x-r,y),
                           (x-r,y-kr), (x-kr,y-r), (x,y-r),
                            (x+kr,y-r), (x+r,y-kr)]
        self.m_arcindex = [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, 9), (9, 10, 11, 0)]
        self.m_points = []
        self.m_index = []

    # Render functions moved into draw routine for simplicity
    #def render(self):
    #    if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
    #        # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
    #        # e.g., self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
    #        #print "self.m_arcpoints = ",self.m_arcpoints
    #        #print "self.m_arcindex = ",self.m_arcindex
    #        for i in range(len(self.m_arcindex)):
    #            # e.g., self.m_arcindex[i] = (0,1,2)
    #            p0 = self.m_arcpoints[self.m_arcindex[i][0]]
    #            p1 = self.m_arcpoints[self.m_arcindex[i][1]]
    #            p2 = self.m_arcpoints[self.m_arcindex[i][2]]
    #            p3 = self.m_arcpoints[self.m_arcindex[i][3]]
    #            (points,index) = curves.cubic_spline(p0,p1,p2,p3,CURVE_SEGS)
    #            if self.m_solid:
    #                points.append(self.m_center)
    #                nxlast_pt = len(points)-2
    #                last_pt = len(points)-1
    #                xtra_index = [nxlast_pt,last_pt,last_pt,0]
    #                index = index + xtra_index
    #            self.m_points.append(points)
    #            self.m_index.append(index)

    def draw(self):
        """Draw a circle.

        We come into this routine with the shape already calculated, and the
        data in the following form:
            a list of points:
                self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
            an index of fourples that describe an arc (cubicspline)
                self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
        The screen engine wants these arcs divded up into line segments
        The laser engine wants these arcs divied up into OSC messages
        """
        if self.m_center and self.m_radius:
            self.render()
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
            if GRAPHMODES & GRAPHOPTS['screen']:
                # The screen engine, pyglet, wants output in this form
                #   a list of points
                #       points = [(10.0,10.0), (20.0,0), (-10.0,10.0), etc]
                #   an index into points describing contiguous line segments
                #       index = [(1,2), (2, 3), (3,4), etc]
                # for each arc in the circle, convert to line segments
                for i in range(len(self.m_arcindex)):
                    # e.g., self.m_arcindex[i] = (0,1,2)
                    p0 = self.m_arcpoints[self.m_arcindex[i][0]]
                    p1 = self.m_arcpoints[self.m_arcindex[i][1]]
                    p2 = self.m_arcpoints[self.m_arcindex[i][2]]
                    p3 = self.m_arcpoints[self.m_arcindex[i][3]]
                    (points,index) = curves.cubic_spline(p0,p1,p2,p3,CURVE_SEGS)
                    if self.m_solid:
                        points.append(self.m_center)
                        nxlast_pt = len(points)-2
                        last_pt = len(points)-1
                        xtra_index = [nxlast_pt,last_pt,last_pt,0]
                        index = index + xtra_index
                    self.m_points.append(points)
                    self.m_index.append(index)
                # now, for each segment, output a line to pyglet
                for i in range(len(self.m_index)):
                    points = self.m_points[i]
                    if dbug.LEV & dbug.GRAPH: print "Circle:draw:Points =",points
                    scaled_pts = self.m_field.rescale_pt2screen(points)
                    if dbug.LEV & dbug.GRAPH: print "Circle:draw:screen:scaled_pts =",scaled_pts
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
            if GRAPHMODES & GRAPHOPTS['osc']:
                # the laser engine wants output of this form:
                #   /laser/bezier/cubic ffffffff
                # we send an OSC message like this:
                #   self.m_field.m_osc_laser.send( OSCMessage("/user/1", [1.0, 2.0, 3.0 ] ) )
                #scaled_pts = self.m_field.rescale_pt2vector(points)
                #if dbug.LEV & dbug.GRAPH: print "Circle:draw:vector:scaled_pts =",scaled_pts
                if dbug.LEV & dbug.GRAPH: 
                    print "Circle:OSC to laser:", OSCPATH['graph_color'], \
                       [self.m_color[0],self.m_color[1],self.m_color[2]]
                self.m_field.m_osc.send_laser(OSCPATH['graph_color'], 
                            [self.m_color[0],self.m_color[1],self.m_color[2]])
                for i in range(len(self.m_arcindex)):
                    # e.g., self.m_arcindex[i] = (0,1,2)
                    p0 = self.m_arcpoints[self.m_arcindex[i][0]]
                    p1 = self.m_arcpoints[self.m_arcindex[i][1]]
                    p2 = self.m_arcpoints[self.m_arcindex[i][2]]
                    p3 = self.m_arcpoints[self.m_arcindex[i][3]]
                    if dbug.LEV & dbug.GRAPH: 
                        print "Circle:OSC to laser:", OSCPATH['graph_cubic'], \
                                [p0[0], p0[1], p1[0], p1[1],
                                 p2[0], p2[1], p3[0], p3[1]]
                    self.m_field.m_osc.send_laser(OSCPATH['graph_cubic'], 
                                    [p0[0], p0[1], p1[0], p1[1], 
                                     p2[0], p2[1], p3[0], p3[1]])


