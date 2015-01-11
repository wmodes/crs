


import main
import Conductor
import config
import itertools
import re

conductor = Conductor(None)

re_tests = {
    "Implemented & Successfully Tested": "Success",
    "Implemented & Not Tested": "Not Tested",
    "Not Implemented": "Not .* Implemented",
}

cell_results = {}
conx_results = {}

print "#\n# Cell tests\n#\n"

for status,regex in re_tests.iteritems():
    cell_results[status] = []
    for type,test in conductor.cell_tests.iteritems():
        docstring = test.__doc__
        #print "KILME:",regex
        if re.search(regex, docstring, flags=re.I):
            cell_results[status].append(type)

for status in re_tests:
    print status
    if len(cell_results[status]):
        for test in cell_results[status]:
            print "    %s"%test
            print "        trigger=%.2f memory=%.2f max_age=%.2f"%\
                (config.cell_avg_triggers[test], 
                config.cell_memory_time[test],
                config.cell_max_age[test])
    else:
        print "    No tests"

#import pdb;pdb.set_trace()
print ""
    
print "#\n# Conductor tests\n#\n"

for status,regex in re_tests.iteritems():
    conx_results[status] = []
    for type,test in conductor.conx_tests.iteritems():
        docstring = test.__doc__
        if re.search(regex, docstring, flags=re.I):
            conx_results[status].append(type)

for status in re_tests:
    print status
    if len(conx_results[status]):
        for test in conx_results[status]:
            print "    %s"%test
            print "        trigger=%.2f memory=%.2f max_age=%.2f"%\
                (config.connector_avg_triggers[test], 
                config.connector_memory_time[test],
                config.connector_max_age[test])
    else:
        print "    No tests"
    
print ""

print "#\n# Cell tests (More Info)\n#\n"

for type,test in conductor.cell_tests.iteritems():
    print "def Conductor.%s(self, uid, type):"%type
    print "    \"\"\"%s"%test.__doc__
    print "    \"\"\"\n"

print "#\n# Conductor tests (More Info)\n#\n"

for type,test in conductor.conx_tests.iteritems():
    print "def Conductor.%s(self, cid, type, cell0, cell1):"%type
    print "    \"\"\"%s"%test.__doc__
    print "    \"\"\"\n"
