#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Co-related space shared config file """

# system configuration
framerate = 25.0
max_lost_patience = 2   # (sec)

# OSC configuration

osc_ips_local = {
    'default': "UNSPECIFIED",
    'localhost': "127.0.0.1",
    'conductor': "127.0.0.1",
    'tracking': "127.0.0.1",
    'sound': "127.0.0.1",
    'laser': "127.0.0.1",
    'recorder': "127.0.0.1",
    'touchosc':"127.0.01",
}

osc_ips_prod = {
    'default': "UNSPECIFIED",
    'localhost': "192.168.0.31",
    'conductor': "localhost",
    'tracking': "localhost",
    'sound': "192.168.0.29",
    'laser': "localhost",
    'recorder': "localhost",
    'touchosc':"127.0.01",
}

osc_ports_local = {
    'default': -1,
    'localhost': 7010,
    'conductor': 7011,
    'tracking': 7770,
    'sound': 7010,
    'laser': 7780,
    'recorder': 7790, 
    'touchosc': 9998, 
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

cell_avg_triggers = {
    # what avg value triggers the connection
    # You can think of this as how much of the time do you expect them to be
    # doing this?
    # 0 = no avg triggers
    'default': 0.8,
    # cell values
    'dance': 0.8,
    'interactive': 0.24,    # implemented
    'static': 0.2,  # implemented
    'kinetic': 0.4, # implemented
    'fast': 0.8,    # implemented; tested
    'timein': 0.3,  # implemented
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
    'dance': 5,
    'interactive': 30,
    'static': 20,
    'kinetic': 10,
    'fast': 1,
    'timein': 30,
    'spin': 5,
    'quantum': 5,
    'jacks': 5,
    'chosen': 5,
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
    # cell values
    'interactive': 3,
    'static': 0.2,  # m/s
    'kinetic': 0.5,  # m/s
    'timein': 60,   # sec
    'fast':2,
}

connector_avg_triggers = {
    # what avg value triggers the connection
    # 0 = no avg triggers
    'default': 0.8,
    # connector values
    'grouped': 0.3,    # implemented; tested
    'contact': 0.3,    # implemented; tested
    'friends': 0.6,    # implemented; tested
    'coord': 0.1,      # implemented
    'mirror': 0,
    'fof': 0,
    'irlbuds': 0.33,    # implemented
    'leastconx': 0,
    'nearby': 0.4,
    'strangers': 0.4,  # implemented
    'chosen': 0,
    'facing': 0.25,
    # happening values
    'fusion': 0.01,   # implemented; tested
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
    'contact': 3,
    'friends': 10,
    'coord': 2,
    'fof': 0,
    'irlbuds': 30,
    'leastconx': 5,
    'nearby': 5,
    'strangers': 60,
    'chosen': 5,
    'facing': 5,
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
    # connector values
    'friends': 3,
    'coord-min': 1,   # m/s
    'contact': 5/8,    # m
    'facing': 180,   # degrees
    'fusion-max': 1.5, # m
    'irlbuds': 3,
    'nearby-min': 1.5,   # m
    'nearby-max': 4, # m
    'strangers-min': 5, # sec
    # happening values
    'fusion-min': .5, # m
    # event values
    'touch': .33,    # m
    'tag': .33,   # m
}

# Internal config
#
report_frequency = {
    # report every n frames
    'debug': 100,
    'rollcall': 25,
    'attrs': 5,
    'conxs': 5,
    'gattrs': 5,
    'uisettings':50,
    'health':25,
}
osctimeout = 0
