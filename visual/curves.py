#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bezier, Cubic, and QuadSpline functions.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "curves.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules
import numpy

# local modules
from shared import debug

# local classes


# constants


# init debugging
dbug = debug.Debug()


## n := len( P ) - 1
## n is the degree.  If n == 3, the bezier is cubic.
## t is the parameter along the curve.  t is in [0,1].

# spline code

def quadx(t, p0, p1, p2):
    #print "points:",p0[0],p1[0],p2[0]," t:",t
    return  (1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]

def quady(t, p0, p1, p2):
    #print "points:",p0[1],p1[1],p2[1]," t:",t
    return (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]

def quad_spline(p0, p1, p2, nsteps):
    """Returns a list of line segments and an index to make the full curve.

    Cubics are defined as a start point (p0) and end point (p2) and
    a control point (p1) and a parameter t that goes from 0.0 to 1.0.
    The parameter is sample nSteps times.

    NOTE: Technically, these are called Quadratic Bezier splines
    """
    linesegments = []
    for i in range(nsteps+1):
        # the definition of the spline means the parameter t goes
        # from 0.0 to 1.0
        t = i / float(nsteps)
        x = quadx(t, p0, p1, p2)
        y = quady(t, p0, p1, p2)
        linesegments.append((x,y))
    #lineSegments.append(p2)
    quadindex = [0] + [int(x * 0.5) for x in range(2, (nsteps)*2)] + [nsteps]
    return (linesegments,quadindex)

def cubic_spline(p0, p1, p2, p3, nsteps):
    """Returns a list of line segments and an index to make the full curve.

    Cubics are defined as a start point (p0) and end point (p3) and
    control points (p1 & p2) and a parameter t that goes from 0.0 to 1.0.
    """
    points = numpy.array([p0, p1, p2, p3])
    bez = bezier_curve( points )
    linesegments = []
    for val in numpy.linspace( 0, 1, nsteps ):
        #print '%s: %s' % (val, bez( val ))
        # the definition of the spline means the parameter t goes
        # from 0.0 to 1.0
        (x,y) = bez(val)
        linesegments.append((x,y))
    #lineSegments.append(p2)
    cubicindex = [0] + [int(x * 0.5) for x in range(2, (nsteps-1)*2)] + [nsteps-1]
    #print "lineSegments = ",lineSegments
    #print "cubicIndex = ",cubicIndex
    return (linesegments,cubicindex)


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

def b( p, t ):
    '''
    Evaluates the bezier curve of degree len(P) - 1, using control points 'P',
    at parameter value 't' in [0,1].
    '''
    n = len( p ) - 1
    assert n > 0
    
    from numpy import zeros
    result = zeros( len( p[0] ) )
    for i in xrange( n + 1 ):
        result += binom( n, i ) * p[i] * (1 - t)**(n-i) * t**i
    
    return result

def b_n( p, n, t ):
    '''
    Evaluates the bezier curve of degree 'n', using control points 'P',
    at parameter value 't' in [0,1].
    '''
    
    ## clamp t to the range [0,1]
    t = min( 1., max( 0., t ) )
    
    num_segments = 1 + (len( p ) - (n+1) + n-1) // n
    assert num_segments > 0
    from math import floor
    segment_offset = min( int( floor( t * num_segments ) ), num_segments-1 )
    
    p_offset = segment_offset * n
    
    return b( p[ p_offset : p_offset + n+1 ], ( t - segment_offset/float(num_segments) ) * num_segments )

def bezier_curve( p ):
    '''
    Returns a function object that can be called with parameters between 0 and 1
    to evaluate the Bezier Curve with control points 'P' and degree len(P)-1.
    '''
    return lambda t: b( p, t )

def bezier_curve_n( p, n ):
    '''
    Returns a function object that can be called with parameters between 0 and 1
    to evaluate the Bezier Curve strip with control points 'P' and degree n.
    '''
    return lambda t: b_n( p, n, t )

def test1():
    print '====== test1() ======'
    
    from numpy import meshgrid, linspace
    p = meshgrid([0,0],range(3+1))[1]
    
    print 'P:'
    print p
    
    v = 5
    bez = bezier_curve( p )
    for val in linspace( 0, 1, v ):
        print '%s: %s' % (val, bez( val ))

def test2():
    print '====== test2() ======'
    
    from numpy import meshgrid, linspace
    p = meshgrid([0,0],range(3+1))[1]
    
    print 'P:'
    print p
    
    n = 2
    print 'n:', n
    
    v = 5
    bez = bezier_curve_n( p, n )
    for val in linspace( 0, 1, v ):
        print '%s: %s' % (val, bez( val ))

def main():
    test1()
    test2()

if __name__ == '__main__': main()
