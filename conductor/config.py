
radius_padding = 1.5      # increased radius of circle around blobs
fuzzy_area_for_cells = 1

xmin = 0
ymin = 0
xmax = 1219 # 40ft = 12.19m = 1219cm
ymax = 1219

#path_unit = 20   # 20cm = about 8in
#path_unit = 40   # 20cm = about 8in
path_unit = 30   # 20cm = about 8in

logfile="crs-conductor.log"

# Data config

avg_time_short = 15 * 1     # 15 fps * 1 sec
avg_time_med = 15 * 5     # 15 fps * 5 sec
avg_time_long = 15 * 15     # 15 fps * 15 sec

# OSC configuration

oscport = 7010
oschost = ""
osctimeout = 0

"""
oscpath_ping = "/ping"
oscpath_start = "/pf/started"
oscpath_entry = "/pf/entry"
oscpath_exit = "/pf/exit"
oscpath_update = "/pf/update"
oscpath_frame = "/pf/frame"
oscpath_stop = "/pf/stopped"
oscpath_set = "/pf/set/"
oscpath_set_dict = {
    "minx": "minx",
    "maxx": "maxx",
    "miny": "miny",
    "maxy": "maxy",
    "npeople": "npeople",
}
"""

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
