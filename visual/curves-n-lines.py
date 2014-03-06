    #!/usr/bin/env python

    # core modules
    from itertools import chain

    # installed modules
    import pyglet
    import numpy

    # local modules
    import config

    # constants
    CURVE_SEGS = config.curve_segments  # number of line segs in a curve

    # bezier curves courtesy of NYU

    def fac( k ):
        '''
        Returns k!.
        '''
        
        if k == 0: return 1
        else: return reduce(lambda i,j : i*j, range(1,k+1))

    def binom( n, k ):
        '''
        Returns n choose k.
        '''
        
        if k < 0 or k > n: return 0
        
        return fac( n ) / ( fac( k ) * fac( n - k ) )

    def B( P, t ):
        '''
        Evaluates the bezier curve of degree len(P) - 1, using control points 'P',
        at parameter value 't' in [0,1].
        '''
        n = len( P ) - 1
        assert n > 0
        
        from numpy import zeros
        result = zeros( len( P[0] ) )
        for i in xrange( n + 1 ):
            result += binom( n, i ) * P[i] * (1 - t)**(n-i) * t**i
        
        return result

    def B_n( P, n, t ):
        '''
        Evaluates the bezier curve of degree 'n', using control points 'P',
        at parameter value 't' in [0,1].
        '''
        
        ## clamp t to the range [0,1]
        t = min( 1., max( 0., t ) )
        
        num_segments = 1 + (len( P ) - (n+1) + n-1) // n
        assert num_segments > 0
        from math import floor
        segment_offset = min( int( floor( t * num_segments ) ), num_segments-1 )
        
        P_offset = segment_offset * n
        
        return B( P[ P_offset : P_offset + n+1 ], ( t - segment_offset/float(num_segments) ) * num_segments )

    def Bezier_Curve( P ):
        '''
        Returns a function object that can be called with parameters between 0 and 1
        to evaluate the Bezier Curve with control points 'P' and degree len(P)-1.
        '''
        return lambda t: B( P, t )

    def Bezier_Curve_n( P, n ):
        '''
        Returns a function object that can be called with parameters between 0 and 1
        to evaluate the Bezier Curve strip with control points 'P' and degree n.
        '''
        return lambda t: B_n( P, n, t )

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
