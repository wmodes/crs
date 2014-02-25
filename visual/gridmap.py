from collections import defaultdict
from math import sqrt


COVER_MAP = [
    [(0,0)],
    [(0,1),(1,0),(0,-1),(-1,0)],
    [(1,1),(1,-1),(-1,-1),(-1,1)],
    [(0,2),(2,0),(0,-2),(-2,0)],
    [(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)],
    [(0,3),(2,2),(3,0),(2,-2),(0,-3),(-2,-2),(-3,0),(-2,2)],
    [(1,3),(3,1),(3,-1),(1,-3),(-1,-3),(-3,-1),(-3,1),(-1,3)]
]

PATH_COST_ZIG = 2
PATH_COST_MID = 1
PATH_COST_LINE = 2
PATH_COST_PROX = [5,4,3]

DRAW_GRID = '.'
DRAW_COST_PROX = "#$@%&0*"
DRAW_COST_PROX = 'Oo,'
DRAW_PATH = '+'
DRAW_PATH_COLIDE = '*'
DRAW_PATH_BLOCK = '0'

MAX_CIRCLE_RADIUS = 20

class GridMap(object):
    """ Represents a rectangular grid map. The map consists of 
        xmax X ymax coordinates (squares). Some of the squares
        can be blocked (by obstacles).
    """

    def __init__(self, xmax, ymax):
        """ Create a new GridMap with the given amount of x and y squares.  """
        self.xmax = xmax
        self.ymax = ymax

        self.map = [[0] * self.ymax for i in range(self.xmax)]
        #self.blocked = defaultdict(lambda: False)
        self.gen_circles(MAX_CIRCLE_RADIUS)

    def gen_circles (self, max_r):
        """ Pre-generate circles to some maximum radius. """
        self.solidcircle = []
        self.opencircle = []
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
        self.max_r = max_r


    def set_blocked(self, p, r, f):
        """Set the blocked state of a coordinate. 

        Takes an integer value that represents the fuzzy cost around the circle.

        """

        # the number of circles we've pregenerated
        n = len(self.solidcircle) - 1
        # if r is higher than the number we've pregen'd, trim it
        r = min(r,n)
        f = min(f,len(PATH_COST_PROX)-1)
        # if r + f is higher than the number we've pregen'd, trim it
        if r + f > n:
            f = max(0, n - r)

        (cx,cy) = p
        for i in range(f + 1):
            if i == 0:
                for j in range(len(self.solidcircle[r])):
                    (relx,rely) = self.solidcircle[r][j]
                    x = cx + relx
                    y = cy + rely
                    if x >= 0 and x < self.xmax and\
                        y >= 0 and y < self.ymax:
                        self.map[x][y] = PATH_COST_PROX[i]
            else:
                for j in range(len(self.opencircle[r+i])):
                    (relx,rely) = self.opencircle[r+i][j]
                    x = cx + relx
                    y = cy + rely
                    if x >= 0 and x < self.xmax and\
                        y >= 0 and y < self.ymax:
                        self.map[x][y] = PATH_COST_PROX[i]

    def set_block_line(self, pathlist):
        """Sets the blocked state of an entire path."""
        for p in pathlist:
            (x,y) = p
            if not self.map[x][y]:
                self.map[x][y] = PATH_COST_LINE

    def move_cost(self, c1, c2, pred=None, start=None, goal=None):
        """ Compute the cost of movement from one coordinate to another. 
        """

        def midpoint(p1, p2):
            return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)

        #The cost is:
        # the Euclidean distance PLUS
        score = sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
        # PLUS a penalty for getting near blocked spaces
        score += self.map[c2[0]][c2[1]]
        # PLUS a penalty for changing direction (except near the center point?)
        if pred and c2[0] != pred[0] and c2[1] != pred[1]:
            #print "zig: ",pred,c1,c2
            score += PATH_COST_ZIG
        # MINUS a penalty if we are at the midpoint of a line
        if start and goal:
            midpt = midpoint(start, goal)
            if c2[0] == midpt[0] or c2[1] == midpt[1]:
                score -= PATH_COST_MID
        score += self.map[c2[0]][c2[1]]
        return score

    def estimate(self, c1, c2):
        """ Compute the cost of movement from one coordinate to
            another. 

            The cost is the Euclidean distance.
        """
        return sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

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

    def printme(self,path=[]):
        """ Print the map to stdout in ASCII. """
        for y in reversed(range(self.ymax)):
            for x in range(self.xmax):
                if self.map[x][y] > PATH_COST_LINE and (x,y) in path:
                    print DRAW_PATH_BLOCK, 
                elif self.map[x][y] > PATH_COST_LINE:
                    #print self.map[x][y],
                    for c in range(len(PATH_COST_PROX)):
                        if self.map[x][y] == PATH_COST_PROX[c]:
                            print DRAW_COST_PROX[c],
                            pass
                elif (x, y) in path:
                    print DRAW_PATH,
                else:
                    print DRAW_GRID,
            print ''

