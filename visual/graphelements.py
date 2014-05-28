#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Graphic Element classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "graphelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from itertools import chain
from math import copysign

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
        # each arc is broken down into a list of points and indecies
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


class Line(object):
    """Define line object.

        Stores the following values:
            m_field: Stores the field for back referencing
            m_p0,m_p1: endpoints of line
            m_r0,m_l1: radius of connected cells
            m_color: color of circle
            m_path: path from one cell0 to cell1
            m_arcpoints: the points that make up the arcs
            m_arcindex: the index to connect the above arcpoints
            m_points: a list of points that make up the circle
            m_index: the index to connect the above points

        """

    def __init__(self):
        """Line constructor."""
        self.m_field = None
        self.m_p0 = None
        self.m_p1 = None
        self.m_r0 = None
        self.m_r1 = None
        self.m_color = None
        self.m_arcpoints = None
        self.m_arcindex = None
        # each arc is broken down into a list of points and indecies
        # these are gathered into lists of lists
        # TODO: possibly these could be melded into single dim lists
        self.m_points = []
        self.m_index = []

    def update(self, field, p0, p1, r0, r1, color, path=None):
        """Update line information."""
        self.m_field = field
        self.m_p0 = p0
        self.m_p1 = p1
        self.m_r0 = r0
        self.m_r1 = r1
        self.m_color = color
        # if we were given a path, we will use it
        if path is None:
            self.m_path = [p0, p1]
        else:
            self.m_path = path

    def fracpoint(self, p1, p2, fract):
        return (p1[0]+(p2[0]-p1[0])*fract, p1[1]+(p2[1]-p1[1])*fract)

    def midpoint(self, p1, p2):
        return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)

    def make_arc(self, p1, p2):
         m1 = self.fracpoint(p1, p2, 0.333)
         m2 = self.fracpoint(p1, p2, 0.666)
         return (p1, m1, m2, p2)

    def in_circle(self,center, radius, p):
        """Is point, p, inside circle of given center and radius."""
        square_dist = (center[0] - p[0]) ** 2 + (center[1] - p[1]) ** 2
        return square_dist < radius ** 2

    def find_intersect(self,outpt, inpt, center, radius):
        # Here instead of checking whether the point is on the circle, 
        # we just see if the points have converged on each other.
        sum_dist = abs(inpt[0] - outpt[0]) + abs(inpt[1] - outpt[1])
        #print "sum dist:",sum_dist
        if sum_dist < 2:
            return inpt
        midpt = self.midpoint(outpt, inpt)
        if self.in_circle(center, radius, midpt):
            return self.find_intersect(outpt, midpt, center, radius)
        else:
            return self.find_intersect(midpt, inpt, center, radius)

    def render(self):
        """Render the line.

        Going into this function, we know the end points of the cells we are
        connecting, and their radius.

        Exiting, we have a list of points that make up the line, and a list of
        indecies that tell us how the points are organized into cubic arcs.
        """
        p0 = self.m_p0
        p1 = self.m_p1
        r0 = self.m_r0
        r1 = self.m_r1
        #import pdb;pdb.set_trace()
        self.m_arcpoints = None
        self.m_arcindex = None
        self.m_points = []
        self.m_index = []
        # locals
        #index = [0] + [int(x * 0.5) for x in range(2, n*2)] + [n]
        lastpt = []
        npath = []

        if LINEMODE == 'direct':
            self.m_arcpoints = [ 
                (p0[0], p0[1]),
                self.midpoint(p0,p1),
                self.midpoint(p0,p1),
                (p1[0], p1[1]),
            ]
            self.m_arcindex = [(0, 1, 2, 3)]

        elif LINEMODE == 'curve':
            (x0,y0)=p0
            (x1,y1)=p1
            # get position of p1 relative to p0
            xdif = abs(x0 - x1)
            ydif = abs(y0 - y1)
            if not xdif or not ydif:
                #print "straight x line: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif
                midpt = self.midpoint(p0,p1)
                self.m_arcpoints = [p0, midpt, midpt, p1]
            elif (xdif > ydif):
                xmid = (x0 + x1)/2
                #print "longer on x: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"xmidpt:",xmid
                self.m_arcpoints = [p0, (xmid,y0), (xmid,y1), p1]
            else:
                ymid = (y0 + y1)/2
                #print "longer on y: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"ymidpt:",ymid
                self.m_arcpoints = [p0, (x0,ymid), (x0,ymid), p1]
            self.m_arcindex = [(0, 1, 2, 3)]

        elif LINEMODE == 'simple':
            (x0,y0)=p0
            (x1,y1)=p1
            self.m_arcpoints = []
            xdif = abs(x0 - x1)
            ydif = abs(y0 - y1)
            if not xdif or not ydif:
                #print "straight x line: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif
                midpt = self.midpoint(p0,p1)
                self.m_arcpoints = [p0, midpt, midpt, p1]
                self.m_arcindex = [(0, 1, 2, 3)]
            elif (xdif > ydif):
                xmid = (x0 + x1)/2
                #print "longer on x: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"xmidpt:",xmid
                self.m_arcpoints += self.make_arc(p0, (xmid, y0))
                self.m_arcpoints += self.make_arc((xmid, y0), (xmid, y1))
                self.m_arcpoints += self.make_arc((xmid, y1), p1)
                self.m_arcindex = [(0, 1, 2, 3),(3, 5, 6, 7),(7, 9, 10, 11)]
            else:
                ymid = (y0 + y1)/2
                #print "longer on y: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"ymidpt:",ymid
                self.m_arcpoints += self.make_arc(p0, (x0, ymid))
                self.m_arcpoints += self.make_arc((x0, ymid), (x1, ymid))
                self.m_arcpoints += self.make_arc((x1, ymid), p1)
                self.m_arcindex = [(0, 1, 2, 3),(3, 5, 6, 7),(7, 9, 10, 11)]
            #break pt
            #import pdb;pdb.set_trace()

        elif LINEMODE == 'improved_simple':
            pass

        elif LINEMODE == 'pathfinding':
            #n = len(path) - 1
            for i in range(0, len(self.m_path)-1):
                thispt = self.m_path[i]
                nextpt = self.m_path[i+1]
                # Remove parts of path within the radius of cell
                # TODO: Ensure that the logic here works in every case
                # if both ends of this line segment are inside a circle fugetaboutit
                if (self.in_circle(p0, r0, thispt) and self.in_circle(p0, r0, nextpt)) or\
                    (self.in_circle(p1, r1, thispt) and self.in_circle(p1, r1, nextpt)):
                    continue
                # if near end of this line segment is inside a circle
                if self.in_circle(p0, r0, thispt):
                    # find the point intersecting the circle
                    thispt = self.find_intersect(nextpt, thispt, p0, r0)
                # if far end of this line segment is inside the other circle
                elif self.in_circle(p1, r1, nextpt):
                    # find the point intersecting the circle
                    nextpt = self.find_intersect(thispt, nextpt, p1, r1)

                # if neither point is inside one of our circles, use it
                #print path[i],"inside cell"
                # take segment of two points, and transform to three point arc
                arc = self.make_arc(thispt,nextpt)
                npath.append(arc[0])
                npath.append(arc[1])
                npath.append(arc[2])
                lastpt = arc[3]
            npath.append(lastpt)
            #print "npath:", npath
            self.m_arcpoints = npath
            self.m_arcindex = [(x-3,x-2,x-1,x) for x in range(3,len(npath),3)]
            #import pdb;pdb.set_trace()
        elif LINEMODE == 'improved_pathfinding':
            pass

    def draw(self):
        """Draw a line, which is actually a path made up of cubicsplines.

        We come into this routine with the shape already calculated, and the
        data in the following form:
            a list of points:
                self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
            an index of fourples that describe an arc (cubicspline)
                self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
        The screen engine wants these arcs divded up into line segments
        The laser engine wants these arcs divied up into OSC messages
        """
        if self.m_p0 and self.m_p1:
            self.render()
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
            if GRAPHMODES & GRAPHOPTS['screen']:
                # The screen engine, pyglet, wants output in this form
                #   a list of points
                #       points = [(10.0,10.0), (20.0,0), (-10.0,10.0), etc]
                #   an index into points describing contiguous line segments
                #       index = [(1,2), (2, 3), (3,4), etc]
                # for each arc in the circle, convert to line segments
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:self.m_arcpoints = ",self.m_arcpoints
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:self.m_arcindex = ",self.m_arcindex
                for i in range(len(self.m_arcindex)):
                    # e.g., self.m_arcindex[i] = (0,1,2,3)
                    p0 = self.m_arcpoints[self.m_arcindex[i][0]]
                    p1 = self.m_arcpoints[self.m_arcindex[i][1]]
                    p2 = self.m_arcpoints[self.m_arcindex[i][2]]
                    p3 = self.m_arcpoints[self.m_arcindex[i][3]]
                    # if this is a straight line, don't chop into cubicSplines
                    #TODO: Replace with colinear test
                    if p0[0] == p1[0] == p2[0] == p3[0] or \
                            p0[1] == p1[1] == p2[1] == p3[1]:
                        points = [p0,p1,p2,p3]
                        index = [0,1,1,2,2,3]
                        # TODO: convert CURVE_SEGS into a passable parameter, so in the
                        # case of a straight line, we pass t=1 so it makes ONE slice
                    else:
                        (points,index) = curves.cubic_spline(p0,p1,p2,p3,CURVE_SEGS)
                    self.m_points.append(points)
                    self.m_index.append(index)
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:self.m_points =",self.m_points
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:index:",self.m_index
                # now, for each segment, output a line to pyglet
                for i in range(len(self.m_index)):
                    points = self.m_points[i]
                    if dbug.LEV & dbug.GRAPH: print "Graph:draw:points =",points
                    scaled_pts = self.m_field.rescale_pt2screen(points)
                    if dbug.LEV & dbug.GRAPH: print "Graph:draw:screen:scaled_points =",scaled_pts
                    index = self.m_index[i]
                    pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
                    pyglet.graphics.draw_indexed(len(scaled_pts), pyglet.gl.GL_LINES,
                        index,
                        ('v2i',tuple(chain(*scaled_pts))),
                    )
            if GRAPHMODES & GRAPHOPTS['osc']:
                # the laser engine wants output of this form:
                #   /laser/bezier/cubic ffffffff
                # we send an OSC message like this:
                #   self.m_field.m_osc_laser.send( OSCMessage("/user/1", [1.0, 2.0, 3.0 ] ) )
                #scaled_pts = self.m_field.rescale_pt2vector(points)
                if dbug.LEV & dbug.GRAPH: 
                    print "Line:OSC to laser:", OSCPATH['graph_color'], \
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
                        print "Line:OSC to laser:", OSCPATH['graph_cubic'], \
                                [p0[0], p0[1], p1[0], p1[1],
                                 p2[0], p2[1], p3[0], p3[1]]
                    self.m_field.m_osc.send_laser(OSCPATH['graph_cubic'], 
                                    [p0[0], p0[1], p1[0], p1[1], 
                                     p2[0], p2[1], p3[0], p3[1]])

