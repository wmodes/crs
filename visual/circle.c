import sys
r = int(sys.argv[1])
 
 for y in xrange(-r*1.3,r*1.3,2):
     for x in xrange(-r*1.3,r*1.3):
	 sys.stdout.write('#$@%&0*;:,. '[min(abs(r*r - (x*x+y*y))/(r/2), 11)])
     print
