
# graphics configuration

draw_blobs = True
default_radius = 0.75
default_orient = 0
default_linecolor = (1,1,1)     # white
default_blobcolor = (.1,.1,.1)  # dark dark gray
default_bkgdcolor = (.25, .25, .25, 1)    # dark gray

radius_padding = 1.5      # increased radius of circle around blobs
curve_segments = 12     # number of line segs in a curve
fuzzy_area_for_cells = 1

xmin = 0
ymin = 0
xmax = 1219 # 40ft = 12.19m = 1219cm
ymax = 1219

min_laser = -32768
max_laser = 32768
min_screen = 0
max_screen = 800

#path_unit = 20   # 20cm = about 8in
#path_unit = 40   # 20cm = about 8in
path_unit = 30   # 20cm = about 8in

logfile="crs-visual.log"

# OSC configuration

oscport = 7010
oschost = ""
osctimeout = 0

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
