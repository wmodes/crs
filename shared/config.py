#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related space shared config file """

# system configuration
framerate = 25.0

# Debugging codes get and'ed together
# MORE  = 1
# FIELD = 2
# DATA  = 4
# GRAPH = 8
# MSGS  = 16
# PYG   = 32
# COND  = 32
debug_level = 2 + 4 + 64    # data (2), field (4), osc(16), conduct(64)
#debug_level = 2 + 4    # data (2), field (4)
#debug_level = 2 + 4 + 8    # data (2), field (4), graph (8)
#debug_level = 255    # everything

max_lost_patience = 2   # (sec)

# OSC configuration

osc_ips_local = {
    'default': "UNSPECIFIED",
    'localhost': "192.168.70.66",
    'visual': "192.168.70.66",
    'conductor': "192.168.70.66",
    'tracking': "localhost",
    'sound': "localhost",
    'laser': "localhost",
    'recorder': "localhost",
}

osc_ips_prod = {
    'default': "UNSPECIFIED",
    'localhost': "192.168.0.31",
    'visual': "localhost",
    'conductor': "localhost",
    'tracking': "localhost",
    'sound': "192.168.0.29",
    'laser': "localhost",
    'recorder': "localhost",
}

osc_ports_local = {
    'default': -1,
    'localhost': "7010",
    'visual': 7012,
    'conductor': 7011,
    'tracking': 7770,
    'sound': 7010,
    'laser': 7780,
    'recorder': 7790, 
} 

osc_ports_prod = osc_ports_local

# modeling configuration
#
max_legs = 4
default_diam = .75    # 3/4 of a meter
default_orient = 0
diam_padding = .25      # 1/4 meter
group_distance = 100
ungroup_distance = 150

cell_avg_min = 0.01    # below this and we consider it zero
cell_avg_triggers = {
    # what avg value triggers the connection
    # You can think of this as how much of the time do you expect them to be
    # doing this?
    # 0 = no avg triggers
    'default': 0.8,
    # cell values
    'dance': 0.8,
    'interactive': 0.25,    # implemented
    'static': 0.8,  # implemented
    'kinetic': 0.8, # implemented
    'fast': 0.8,    # implemented; tested
    'timein': 0.5,  # implemented
    'spin': 0.8,
    'quantum': 0.8,
    'jacks': 0.8,
    'chosen': 0.8,
}

cell_memory_time = {
    # Haw far back do we consider (in sec)
    # 0 = no timed triggers
    'default': 10,
    # cell values
    'dance': 10,
    'interactive': 5*60,
    'static': 20,
    'kinetic': 20,
    'fast': 2,
    'timein': 20,
    #'timein': 120,
    'spin': 10,
    'quantum': 10,
    'jacks': 10,
    'chosen': 10,
}

cell_max_age = {
    # as max age in secs
    # 0 = immortal
    'default': 10,
    # cell values
    'dance': 10,
    'interactive': 10,
    'static': 10,
    'kinetic': 10,
    'fast': 10,
    'timein': 10,
    'spin': 10,
    'quantum': 10,
    'jacks': 10,
    'chosen': 10,
}

cell_qualifying_triggers = {
    # in meters unless otherwise specified
    'default': 2, # totally arbitrary since default dist is meaningless
    # cell values
    'interactive': 3,
    'static': 4,  # m/s
    'kinetic': 4,  # m/s
    'timein': 60,   # sec
}

cell_latitude = {
    # all as percentage variance
}


connector_avg_min = 0.01    # below this and we consider it zero
connector_avg_triggers = {
    # what avg value triggers the connection
    # 0 = no avg triggers
    'default': 0.8,
    # connector values
    'grouped': 0.3,    # implemented; tested
    'contact': 0.3,    # implemented; tested
    'friends': 0.8,    # implemented; tested
    'coord': 0.9,      # implemented
    'mirror': 0,
    'fof': 0,
    'irlbuds': 0.66,    # implemented
    'leastconx': 0,
    'nearby': 0.8,
    'strangers': 0.8,  # implemented
    'chosen': 0,
    'facing': 0.5,
    # happening values
    'fusion': 0,   # implemented; tested
    'transfer': 0,
    # event values
    'touch': 0.3,    # implemented; tested
    'tag': 0.3,    # implemented; tested
}

connector_memory_time = {
    # Haw far back do we consider (in sec)
    # 0 = no timed triggers
    'default': 10,
    # connector values
    'grouped': 3,
    'contact': 20,
    'friends': 10,
    'coord': 5,
    'fof': 0,
    'irlbuds': 2*60,
    'leastconx': 10,
    'nearby': 5,
    'strangers': 2*60,
    'chosen': 10,
    'facing': 10,
    # happening values
    'fusion': 0,
    'transfer': 0,
    # event values
    'touch': 0,
    'tag': 0,
}

connector_max_age = {
    # as max age in secs
    # 0 = immortal
    'default': 10,
    # connector values
    'grouped': 10,
    'contact': 10,
    'friends': 10,
    'coord': 10,
    'fof': 10,
    'irlbuds': 30,
    'leastconx': 20,
    'mirror': 10,
    'nearby': 5,
    'strangers': 30,
    'chosen': 20,
    'facing': 20,
    # happening values
    'fusion': 0,
    'transfer': 0,
    # event values
    'touch': 0,
    'tag': 0,
}

connector_qualifying_triggers = {
    # in meters, unless otherwise specified
    'default-min': 1, # totally arbitrary since default dist is meaningless
    'default-max': 3, # totally arbitrary since default dist is meaningless
    # connector values
    'friends': 10,
    'coord-min-vel': 4,   # m/s
    'coord-max-vdiff': 4,   # m/s
    'contact': .33,    # m
    'facing': 90,   # degrees
    'fusion-max': 1.5, # m
    'nearby-min': 4,   # m
    'nearby-max': 1.5, # m
    'strangers-min': 5, # sec
    # happening values
    'fusion-min': .5, # m
    # event values
    'touch': .33,    # m
    'tag': .33,   # m
}

connector_latitude = {
    # all as percentage variance
    'heading': 10,
}


# visual configuration
#
graphic_modes = 3   # 1=screen; 2=osc; 3=etherdream
#graphic_modes = 1 | 2   # 1=screen; 2=osc; 3=etherdream
#draw_bodies = True
draw_bodies = False

# Line mode, one of 
#   'direct', 'curve', 'simple', 'improved-simple', 'pathfinding', 'improved_pathfinding'
linemode = 'curves'

inverse=True
if inverse:
    default_bkgdcolor = (0, 0, 0, 1)    # black
    default_guidecolor = (1,1,1)  # white
    default_linecolor = (0,1,0)     # white
    default_groupcolor = (0,0,0)     # differt
    default_bodycolor = (.2,.2,.2)  # dk gray
else:
    default_bkgdcolor = (1, 1, 1, 1)    # white
    default_guidecolor = (.1,.1,.1)  # dark dark gray
    default_linecolor = (0,0,0)     # black
    default_bodycolor = (.1,.1,.1)  # gray

curve_segments = 12     # number of line segs in a curve
fuzzy_area_for_cells = 1

#minimum_connection_distance = 12000   # this is cm sq

xmin_field = -16  # (m)
ymin_field = 0  # (m)
xmax_field = 16   # (m)
ymax_field = 16  # (m)

# etherdream
#xmin_vector = -32768 #
#ymin_vector = -32768
#xmax_vector = 32768
#ymax_vector = 32768
# Brent's graphic system
xmin_vector = -32768
ymin_vector = -32768
xmax_vector = 32768
ymax_vector = 32768
xmin_screen = 0
ymin_screen = 0
xmax_screen = 640
ymax_screen = 480
#xmax_screen = 1440
#ymax_screen = 795

default_margin=.03

#path_unit = 20   # 20cm = about 8in
#path_unit = 40   # 20cm = about 8in
path_unit = .2    # 0.2m = 20 cm

# Internal config
#

logfile="crs-visual.log"

report_frequency = {
    # report every n frames
    'debug': 100,
    'rollcall': 25,
    'attrs': 5,
    'conxs': 5,
    'gattrs': 5,
    'events': 1,
}
osctimeout = 0

oscpath = {
    # Common
    'ping': "/ping",
    'ack': "/ack",

    # Tracker subsystem
    #
    # Output to tracker
    'track_dump': "/pf/dump",
    'track_adddest': "/pf/adddest",
    'track_rmdest': "/pf/rmdest",
    # Incoming OSC: field state
    'track_start': "/pf/started",
    'track_stop': "/pf/stopped",
    'track_entry': "/pf/entry",
    'track_exit': "/pf/exit",
    'track_frame': "/pf/frame",
    # Incoming OSC: set params
    'track_set': "/pf/set/",
    'track_minx': "/pf/set/minx",
    'track_maxx': "/pf/set/maxx",
    'track_miny': "/pf/set/miny",
    'track_maxy': "/pf/set/maxy",
    'track_npeople': "/pf/set/npeople",
    'track_groupdist': "/pf/set/groupdist",
    'track_ungroupdist': "/pf/set/ungroupdist",
    'track_fps': "/pf/set/fps",
    # Incoming OSC: updates
    'track_update': "/pf/update",
    'track_leg': "/pf/leg",
    'track_body': "/pf/body",
    'track_group': "/pf/group",
    'track_geo': "/pf/geo",

    # Visual subsystem
    #
    # Outgoing from the visual subsys
    'visual_start': "/visual/start",
    'visual_stop': "/visual/stop",

    # Laser subsystem
    #
    # Outgoing to the laser engine
    'graph_start': "/laser/start",
    'graph_stop': "/laser/stop",
    'graph_line': "/laser/line",
    'graph_cubic': "/laser/bezier/cubic",
    'graph_arc': "/laser/arc",
    'graph_color': "/laser/set/color",
    'graph_density': "/laser/set/density",
    'graph_attr': "/laser/set/attribute",
    'graph_pps': "/laser/set/pps",
    'graph_update': "/laser/update",
    'graph_begin_conx':"/laser/conx/begin",
    'graph_end_conx':"/laser/conx/end",
    'graph_begin_cell':"/laser/cell/begin",
    'graph_end_cell':"/laser/cell/end",
    
    # Conductor subsystem
    #
    # Incoming to the conductor
    'conduct_dump': "/conductor/dump",
    # Outgoing from the conductor
    'conduct_start': "/conductor/start",
    'conduct_stop': "/conductor/stop",
    'conduct_scene': "/conductor/scene",
    'conduct_rollcall': "/conductor/rollcall",
    'conduct_attr': "/conductor/attr",
    'conduct_conx': "/conductor/conx",
    'conduct_conxbreak': "/conductor/conxbreak",
    'conduct_gattr': "/conductor/gattr",
    'conduct_event': "/conductor/event",

}
