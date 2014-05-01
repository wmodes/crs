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

__appname__ = "graphelement_class.py"
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

CURVE_SEGS = config.curve_segments  # number of line segs in a curve

# init debugging
dbug = debug.Debug()


class Circle(object):
    """Define circle object."""
    def __init__(self):
        """Circle constructor."""
        self.m_field = None
        self.m_center = None
        self.m_radius = None
        self.m_color = None
        self.m_solid = None
        self.m_arcpoints = None
        self.m_arcindex = None
        # each arc is broken down into a list of points and indecies
        # these are gathered into lists of lists
        # TODO: possibly these could be melded into single dim lists
        self.m_points = []
        self.m_index = []

    def update(self, field, p, r, color, solid=False):
        """Circle constructor.

        Args:
            p - center point
            r - radius of circle
            c - color
        """

        self.m_field = field
        self.m_center = p
        self.m_radius = r
        self.m_color = color
        self.m_solid = solid
        self.m_points = []
        self.m_index = []
        k = 0.5522847498307935  # 4/3 (sqrt(2)-1)
        kr = int(r*k)
        (x,y)=p
        self.m_arcpoints = [(x+r,y),(x+r,y+kr), (x+kr,y+r), (x,y+r),
                           (x-kr,y+r), (x-r,y+kr), (x-r,y),
                           (x-r,y-kr), (x-kr,y-r), (x,y-r),
                            (x+kr,y-r), (x+r,y-kr)]
        self.m_arcindex = [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, 9), (9, 10, 11, 0)]

    def render(self):
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
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
                (points,index) = curves.cubic_spline(p0,p1,p2,p3,CURVE_SEGS)
                if self.m_solid:
                    points.append(self.m_center)
                    nxlast_pt = len(points)-2
                    last_pt = len(points)-1
                    xtra_index = [nxlast_pt,last_pt,last_pt,0]
                    index = index + xtra_index
                self.m_points.append(points)
                self.m_index.append(index)

    def draw(self):
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
            for i in range(len(self.m_index)):
                points = self.m_points[i]
                if dbug.LEV & dbug.GRAPH: print "Cirlce:draw:Points =",points
                scaled_pts = self.m_field.rescale_pt2out(points)
                if dbug.LEV & dbug.GRAPH: print "Cirlce:draw:Scaled_pts =",scaled_pts
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


class Line(object):
    """Define line object."""
    def __init__(self):
        """Line constructor."""
        self.m_field = None
        self.m_p0 = None
        self.m_p1 = None
        self.m_r0 = None
        self.m_r1 = None
        self.m_color = None
        self.m_path = None
        self.m_arcpoints = None
        self.m_arcindex = None
        # each arc is broken down into a list of points and indecies
        # these are gathered into lists of lists
        # TODO: possibly these could be melded into single dim lists
        self.m_points = []
        self.m_index = []

    def update(self, field, p0, p1, r0, r1, color, path=None):
        self.m_field = field
        self.m_color = color
        # if we were given a path, we will use it
        if path is None:
            path = []
        n = len(path) - 1
        #index = [0] + [int(x * 0.5) for x in range(2, n*2)] + [n]
        lastpt = []
        npath = []
            
        for i in range(0, len(path)-1):
            thispt = path[i]
            nextpt = path[i+1]
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

            # if one end of this line segment is inside a circle
            #if in_circle(p1, r1, thispt) and not in_circle(p1, r1, nextpt):
                # find the point intersecting the circle
                #thispt = find_intersect(thispt, nextpt, p1, r1)
            # if one end of this line segment is inside the other circle
            #if in_circle(p0, r0, nextpt) and not in_circle(p0, r0, thispt):
                # find the point intersecting the circle
                #nextpt = find_intersect(nextpt, thispt, p0, r0)

            # if neither point is inside one of our circles, use it
            #print path[i],"inside cell"
            # take segment of two points, and transform to three point arc
            arc = self.make_arc(thispt,nextpt)
            npath.append(arc[0])
            npath.append(arc[1])
            lastpt = arc[2]
            npath.append(lastpt)
            #print "npath:", npath
        self.m_arcpoints = npath
        self.m_arcindex = [(x-3,x-2,x-1,x) for x in range(3,len(npath),3)]

    def midpoint(self, p1, p2):
        return (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))

    def make_arc(self,p1,p2):
        midpt = self.midpoint(p1,p2)
        return p1,midpt,midpt,p2

    def in_circle(self,center, radius, p):
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
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
            # e.g., self.m_arcpoints = [(10,5),(15,5),(15,10),(15,15),(10,15),(5,15),(5,10)]
            # e.g., self.m_arcindex = [(0,1,2,3),(3,4,5,6)]
            if dbug.LEV & dbug.GRAPH: print "Graph:render:self.m_arcpoints = ",self.m_arcpoints
            if dbug.LEV & dbug.GRAPH: print "Graph:render:self.m_arcindex = ",self.m_arcindex

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
                    (points,index) = curves.cubic_spline(p0,p1,p2,p3,CURVE_SEGS)
                self.m_points.append(points)
                self.m_index.append(index)

    def draw(self):
        if self.m_field and self.m_arcpoints and self.m_arcindex and self.m_color:
            if dbug.LEV & dbug.GRAPH: print "Graph:draw:self.m_points =",self.m_points
            if dbug.LEV & dbug.GRAPH: print "Graph:draw:index:",self.m_index
            for i in range(len(self.m_index)):
                points = self.m_points[i]
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:points =",points
                scaled_pts = self.m_field.rescale_pt2out(points)
                if dbug.LEV & dbug.GRAPH: print "Graph:draw:scaled_points =",scaled_pts
                index = self.m_index[i]
                pyglet.gl.glColor3f(self.m_color[0],self.m_color[1],self.m_color[2])
                pyglet.graphics.draw_indexed(len(scaled_pts), pyglet.gl.GL_LINES,
                    index,
                    ('v2i',tuple(chain(*scaled_pts))),
                )
