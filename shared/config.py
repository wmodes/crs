#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related space shared config file """

# system configuration
framerate = 25.0

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
    'cell-dance': 0.8,
    'cell-interactive': 0.25,
    'cell-static': 0.6,
    'cell-kinetic': 0.6,
    'cell-fast': 0.8,
    'cell-timein': 0.5,
    'cell-spin': 0.8,
    'cell-quantum': 0.8,
    'cell-jacks': 0.8,
    'cell-chosen': 0.8,
}

cell_memory_time = {
    # Haw far back do we consider (in sec)
    # 0 = no timed triggers
    'default': 10,
    # cell values
    'cell-dance': 10,
    'cell-interactive': 5*60,
    'cell-static': 10,
    'cell-kinetic': 10,
    'cell-fast': 2,
    'cell-timein': 120,
    'cell-spin': 10,
    'cell-quantum': 10,
    'cell-jacks': 10,
    'cell-chosen': 10,
}

cell_max_age = {
    # as max age in secs
    # 0 = immortal
    'default': 10,
    # cell values
    'cell-dance': 10,
    'cell-interactive': 10,
    'cell-static': 10,
    'cell-kinetic': 10,
    'cell-fast': 10,
    'cell-timein': 10,
    'cell-spin': 10,
    'cell-quantum': 10,
    'cell-jacks': 10,
    'cell-chosen': 10,
}

cell_physical_triggers = {
    # in meters unless otherwise specified
    'default': 2, # totally arbitrary since default dist is meaningless
    # cell values
    'cell-interactive': 3,
    'cell-static': 4,  # m/s
    'cell-kinetic': 4,  # m/s
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
    'conx-conx-grouped': 0.3,
    'conx-contact': 0.3,
    'conx-friends': 0.8,
    'conx-coord': 0.9,
    'conx-fof': 0,
    'conx-irlbuds': 0.8,
    'conx-leastconx': 0,
    'conx-nearby': 0,
    'conx-tag': 0,
    'conx-chosen': 0,
    'conx-fusion': 0,
    'conx-transfer': 0,
}

connector_memory_time = {
    # Haw far back do we consider (in sec)
    # 0 = no timed triggers
    'default': 10,
    # connector values
    'conx-grouped': 3,
    'conx-contact': 20,
    'conx-friends': 30,
    'conx-coord': 5,
    'conx-fof': 0,
    'conx-irlbuds': 5*60,
    'conx-leastconx': 0,
    'conx-nearby': 0,
    'conx-tag': 0,
    'conx-chosen': 0,
    'conx-facing': 20,
    'conx-fusion': 0,
    'conx-transfer': 0,
}

connector_max_age = {
    # as max age in secs
    # 0 = immortal
    'default': 10,
    # connector values
    'conx-grouped': 10,
    'conx-contact': 10,
    'conx-friends': 10,
    'conx-coord': 10,
    'conx-fof': 10,
    'conx-irlbuds': 30,
    'conx-leastconx': 20,
    'conx-mirror': 10,
    'conx-nearby': 5,
    'conx-strangers': 10,
    'conx-tag': 10,
    'conx-chosen': 20,
    'conx-facing': 20,
    'conx-fusion': 0,
    'conx-transfer': 0,
}

connector_physical_triggers = {
    # in meters, unless otherwise specified
    'default': 2, # totally arbitrary since default dist is meaningless
    # connector values
    'conx-friends': 10,
    'conx-coord': 20,   # m/s
    'conx-contact': .33,
    'conx-facing': 30,   # degrees
    'conx-fusion_max': 1.5,
    'conx-fusion_min': .75,
    'conx-nearby_min': 3,
    'conx-nearby_max': 1.5,
}

connector_latitude = {
    # all as percentage variance
    'conx-heading': 10,
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

max_lost_patience = 25 * 5

# OSC configuration

osc_default_host = "UNSPECIFIED"
osc_default_port = -1

osc_visual_host = "192.168.0.100"
osc_visual_port = 7012

osc_conductor_host = "192.168.0.100"
osc_conductor_port = 7011

osc_tracking_host = "192.168.0.162"
osc_tracking_port = 7770

osc_sound_host = "192.168.0.101"
osc_sound_port = 7010

osc_laser_host = "192.168.0.162"
osc_laser_port = 7780

osc_recorder_host = "192.168.0.162"
osc_recorder_port = 7790

osc_local_only=True

if osc_local_only:
    #localhost="127.0.0.1"
    localhost="localhost"
    osc_visual_host = localhost
    osc_conductor_host = localhost
    osc_tracking_host = localhost
    osc_sound_host = localhost
    osc_laser_host =localhost
    osc_recorder_host =localhost

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
