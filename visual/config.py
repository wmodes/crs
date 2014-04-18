
# graphics configuration

draw_blobs = True
default_radius = 75
default_orient = 0
inverse=False
if inverse:
    default_bkgdcolor = (.25, .25, .25, 1)    # dark gray
    default_guidecolor = (0,0,0)  # dark dark gray
    default_linecolor = (1,1,1)     # white
    default_blobcolor = (0,0,0)  # gray
else:
    default_bkgdcolor = (1, 1, 1, 1)    # white
    default_guidecolor = (.1,.1,.1)  # dark dark gray
    default_linecolor = (0,0,0)     # black
    default_blobcolor = (.1,.1,.1)  # gray

radius_padding = 1.5      # increased radius of circle around blobs
curve_segments = 12     # number of line segs in a curve
fuzzy_area_for_cells = 1

minimum_connection_distance = 12000   # this is cm sq

xmin_field = -1600
ymin_field = 0
xmax_field = 1600 # 40ft = 12.19m = 1219cm
ymax_field = 1600

xmin_vector = -32768
ymin_vector = -32768
xmax_vector = 32768
ymax_vector = 32768
xmin_screen = 0
ymin_screen = 0
xmax_screen = 1440
ymax_screen = 795

default_margin=.05

#path_unit = 20   # 20cm = about 8in
#path_unit = 40   # 20cm = about 8in
path_unit = 30   # 20cm = about 8in

logfile="crs-visual.log"
freq_regular_reports = 100

max_lost_patience = 10

# OSC configuration

oscport = 7010
#oschost = "169.254.31.214"
oschost = ""
osctimeout = 0

oscpath = {
    # Incoming OSC from the tracking subsys, pf=pulsefield
    'ping': "/ping",
    'start': "/pf/started",
    'entry': "/pf/entry",
    'exit': "/pf/exit",
    'update': "/pf/update",
    'frame': "/pf/frame",
    'stop': "/pf/stopped",
    'set': "/pf/set/",
    'minx': "/pf/set/minx",
    'maxx': "/pf/set/maxx",
    'miny': "/pf/set/miny",
    'maxy': "/pf/set/maxy",
    'npeople': "/pf/set/npeople",
    # Outgoing OSC updates from the conductor
    'attribute': "/conducter/attribute",
    'rollcall': "/conducter/rollcall",
    'event': "/conducter/event",
    'conx': "/conducter/conx",
}
