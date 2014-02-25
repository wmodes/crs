import sys
r = int(sys.argv[1])

#pen = '#$@%&0*;:,. '
pen = '###.'
 
for y in xrange(int(-r*1.3),int(r*1.3),2):
    for x in xrange(int(-r*1.3),int(r*1.3)):
        sys.stdout.write(pen[min(abs(r*r - (x*x+y*y))/(r/2), len(pen)-1)])
    print
