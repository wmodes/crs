
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

osc_default_host = "UNSPECIFIED"
osc_default_port = -1

osc_visual_host = "localhost"
osc_visual_port = 7012

osc_conductor_host = "localhost"
osc_conductor_port = 7011

osc_tracking_host = "localhost"
osc_tracking_port = 7770

osc_sound_host = "192.168.0.29"
osc_sound_port = 7010

osc_laser_host = "localhost"
osc_laser_port = 7780

osc_recorder_host = "localhost"
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

