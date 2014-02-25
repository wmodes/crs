
max_radius = 20    
xmax = max_radius*2 + 5
ymax = max_radius*2 + 5

PATH_COST_PROX0 = 5
PATH_COST_PROX1 = 4
PATH_COST_PROX2 = 3
PATH_COST_PROX3 = 2
PATH_COST_PROX4 = 1
PATH_COST_PROX = [5,4,3]
DRAW_COST_PROX = "#$@%&0*"
DRAW_COST_PROX = "@0*"

class DiscTemplate:

    def __init__(self, max_r):
        self.map = [[0] * ymax for i in range(xmax)]

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

    def get_disc(self, r):
        return self.solidcircle[r - 1]

    def set_blocked(self, p, r, f):
        """
        Set the blocked state of a coordinate. Takes an integer value that
        represents the fuzzy cost around the circle.
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
                print "core!"
                for j in range(len(self.solidcircle[r])):
                    (relx,rely) = self.solidcircle[r][j]
                    self.map[cx+relx][cy+rely] = PATH_COST_PROX[i]
            else:
                print "fuzzy!"
                for j in range(len(self.opencircle[r+i])):
                    (relx,rely) = self.opencircle[r+i][j]
                    self.map[cx+relx][cy+rely] = PATH_COST_PROX[i]

    def printme(self):
        """ Print the map to stdout in ASCII."""
        for y in reversed(range(ymax)):
            for x in range(xmax):
                if self.map[x][y] >= 1:
                    #print self.map[x][y],
                    for c in range(len(PATH_COST_PROX)):
                        if self.map[x][y] == PATH_COST_PROX[c]:
                            print DRAW_COST_PROX[c],
                            pass
                else:
                    print '.',
            print ''

test = DiscTemplate(20)
test.set_blocked((xmax/2,ymax/2),3,6)
#print "solid:",test.solidcircle[10]
#print "open:",test.opencircle[10]
#disc = test.get_disc(20)

test.printme()
