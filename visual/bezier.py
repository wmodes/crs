## n := len( P ) - 1
## n is the degree.  If n == 3, the bezier is cubic.
## t is the parameter along the curve.  t is in [0,1].

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

def test1():
    print '====== test1() ======'
    
    from numpy import meshgrid, linspace
    P = meshgrid([0,0],range(3+1))[1]
    
    print 'P:'
    print P
    
    V = 5
    bez = Bezier_Curve( P )
    for val in linspace( 0, 1, V ):
        print '%s: %s' % (val, bez( val ))

def test2():
    print '====== test2() ======'
    
    from numpy import meshgrid, linspace
    P = meshgrid([0,0],range(3+1))[1]
    
    print 'P:'
    print P
    
    n = 2
    print 'n:', n
    
    V = 5
    bez = Bezier_Curve_n( P, n )
    for val in linspace( 0, 1, V ):
        print '%s: %s' % (val, bez( val ))

def main():
    test1()
    test2()

if __name__ == '__main__': main()
