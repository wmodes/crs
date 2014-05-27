#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pathfinding classes.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "pathelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
import sys
from math import copysign
#from collections import defaultdict
import numpy

# installed modules

# local modules
from shared import config
from shared import debug

# local classes

# constants
PATH_COST_ZIG = 2
PATH_COST_MID = 1
PATH_COST_LINE = 3
PATH_COST_PROX = [6,5,4]

DRAW_GRID = '.'
#DRAW_COST_PROX = "#$@%&0*"
DRAW_COST_PROX = 'Oo,'
DRAW_PATH = '+'
DRAW_PATH_COLIDE = '*'
DRAW_PATH_BLOCK = '0'

MAX_CIRCLE_RADIUS = 20


# init debugging
dbug = debug.Debug()

class GridMap(object):
    """ Represents a rectangular grid map. The map consists of 
        xmax X ymax coordinates (squares). Some of the squares
        can be blocked (by obstacles).
    """

    def __init__(self, xmax, ymax):
        """ Create a new GridMap with the given amount of x and y squares.  """
        self.max_r = 0
        self.opencircle = []
        self.solidcircle = []
        self.xmax = xmax
        self.ymax = ymax

        #self.map = [[0] * self.ymax+1 for i in range(self.xmax+1)]
        self.map = numpy.zeros((self.xmax+1,self.ymax+1))
        #self.blocked = defaultdict(lambda: False)
        self.gen_circles(MAX_CIRCLE_RADIUS)

    def reset_grid(self):
        """ Resets the grid between frames. """
        #self.map = [[0] * self.ymax for i in range(self.xmax)]
        self.map = numpy.zeros((self.xmax,self.ymax))

    def gen_circles (self, max_r):
        """ Pre-generate circles to some maximum radius. """
        self.max_r = max_r
        for k_r in range(max_r + 1):
            k_r_sq = k_r ** 2
            newlist = []
            for x in range(-max_r, max_r + 1):
                x_sq = x ** 2
                for y in range(-max_r, max_r + 1):
                    y_sq = y ** 2
                    #if x_sq + y_sq <= k_r_sq and x_sq + y_sq >= (k_r_sq - 8):
                    if x_sq + y_sq <= k_r_sq:
                        newlist.append((x,y))
            self.solidcircle.append(newlist)
            if k_r > 1:
                #print "k_r:",k_r
                #print "opencircle(",k_r,"):",newlist," minus ",self.solidcircle[k_r -2]
                newlist = [x for x in newlist if x not in self.solidcircle[k_r - 1]]
            self.opencircle.append(newlist)

    def set_blocked(self, p, r, f):
        """Set the blocked state of a coordinate. 

        Takes an integer value that represents the fuzzy cost around the circle.

        """

        # the number of circles we've pregenerated
        n = len(self.solidcircle) - 1
        # if r is higher than the number we've pregen'd, trim it
        r = int(min(r,n))
        # if r + f is higher than the number we've pregen'd, trim it
        if r + f > n:
            f = int(max(0, n - r))

        (cx,cy) = p
        for i in range(f + 1):
            if i == 0:
                for j in range(len(self.solidcircle[r])):
                    (relx,rely) = self.solidcircle[r][j]
                    x = cx + relx
                    y = cy + rely
                    if 0 <= x < self.xmax and \
                       0 <= y < self.ymax:
                        self.map[x][y] = PATH_COST_PROX[i]
            else:
                for j in range(len(self.opencircle[r+i])):
                    (relx,rely) = self.opencircle[r+i][j]
                    x = cx + relx
                    y = cy + rely
                    if 0 <= x < self.xmax and \
                       0 <= y < self.ymax:
                        self.map[x][y] = PATH_COST_PROX[i]

    def set_block_line(self, pathlist):
        """Sets the blocked state of an entire path."""
        for p in pathlist:
            (x,y) = p
            if not self.map[x][y]:
                self.map[x][y] = PATH_COST_LINE

    def midpoint(self, p1, p2):
        return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)

    def move_cost(self, c1, c2, pred=None, start=None, goal=None):
        """ Compute the cost of movement from one coordinate to another. 
        """

        #The cost is:
        # the Euclidean distance PLUS
        # TODO: There has got to be a faster way to weigh distance
        #score = sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
        score = ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5
        # PLUS a penalty for getting near blocked spaces
        score += self.map[c2[0]][c2[1]]
        # PLUS a penalty for changing direction (except near the center point?)
        if pred and c2[0] != pred[0] and c2[1] != pred[1]:
            #print "zig: ",pred,c1,c2
            score += PATH_COST_ZIG
        # MINUS a penalty if we are at the midpoint of a line
        if start and goal:
            midpt = self.midpoint(start, goal)
            if c2[0] == midpt[0] or c2[1] == midpt[1]:
                score -= PATH_COST_MID
        score += self.map[c2[0]][c2[1]]
        return score

    def estimate(self, c1, c2):
        """ Compute the cost of movement from one coordinate to
            another. 

            The cost is the Euclidean distance.
        """
        # TODO: There has got to be a faster routine for this
        #return sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5

    def successors(self, c):
        """ Compute the successors of coordinate 'c': all the 
            coordinates that can be reached by one step from 'c'.

            In the source algorithm, blocking was done in the successors
            function. I wanted a bit more shades of gray, and so added it as
            additional cost in the move_cost function. This allows it to
            "overcome" obstacles if necessary.
            
        """
        slist = []

        for (dx,dy) in [(0,-1),(-1,0),(0,1),(1,0)]:
            newx = c[0] + dx
            newy = c[1] + dy
            if (    0 <= newx <= self.xmax - 1 and
                    0 <= newy <= self.ymax - 1):
                slist.append((newx, newy))

        return slist

    def easy_path(self,start,goal):
        """ First we try to create an easy path if we can.

        First we try several simple/dumb paths, reserving A* for the ones that
        are blocked and need more smarts. We sort the connectors by distance
        and do easy paths for the closest ones first. Otherwise, we return nothing.

        args:
            start = path-scaled start point
            goal = path-scaled goal point
        returns:
            path-scaled list of points that make up the path
        """

        def enumXpath(p0,p1):
            xpath = []
            y = p0[1]
            x0 = p0[0]
            x1 = p1[0]
            if x0 < x1:
                for x in range(x0,x1+1,1):
                    xpath.append((x,y))
            else:
                for x in range(x0,x1-1,-1):
                    xpath.append((x,y))
            return xpath

        def enumYpath(p0,p1):
            ypath = []
            x = p0[0]
            y0 = p0[1]
            y1 = p1[1]
            if y0 < y1:
                for y in range(y0,y1,1):
                    ypath.append((x,y))
            else:
                for y in range(y0,y1-1,-1):
                    ypath.append((x,y))
            return ypath

        (x0,y0)=start
        (x1,y1)=goal
        path = []
        # get position of p1 relative to p0 
        vx = int(copysign(1,x1-x0))  # rel x pos vector as 1 or -1
        vy = int(copysign(1,y1-y0))  # rel y pos vector as 1 or -1
        xdif = abs(x0 - x1)
        ydif = abs(y0 - y1)
        if not xdif:
            #print "straight x line: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif
            path = enumYpath((x0,y0),(x1,y1))
        elif not ydif:
            #print "straight y line: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif
            path = enumXpath((x0,y0),(x1,y1))
        elif (xdif > ydif):
            xmid = x0 + vx*xdif/2
            #print "longer on x: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"xmidpt:",xmid
            path += enumXpath((x0,y0),(xmid,y0))
            path += enumYpath((xmid,y0),(xmid,y1))
            path += enumXpath((xmid,y1),(x1,y1))
        else:
            ymid = y0 + vy*ydif/2
            #print "longer on y: p0:",start,"p1:",goal,"xdif:",xdif,"ydif:",ydif,"ymidpt:",ymid
            path += enumYpath((x0,y0),(x0,ymid))
            path += enumXpath((x0,ymid),(x1,ymid))
            path += enumYpath((x1,ymid),(x1,y1))
        return path

    def printme(self):
        """ Print the map to stdout in ASCII. """
        for y in reversed(range(self.ymax)):
            for x in range(self.xmax):
                if self.map[x][y] > PATH_COST_LINE:
                    #print self.map[x][y],
                    for c in range(len(PATH_COST_PROX)):
                        if self.map[x][y] == PATH_COST_PROX[c]:
                            sys.stdout.write(DRAW_COST_PROX[c])
                elif self.map[x][y] == PATH_COST_LINE:
                    sys.stdout.write(DRAW_PATH)
                else:
                    sys.stdout.write(DRAW_GRID)
            print ''

