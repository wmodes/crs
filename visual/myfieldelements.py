#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Subclassed field class.

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "myfieldelements.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules
from itertools import chain

# installed modules
import pyglet

# local modules
from shared import config
from shared import debug

# local classes
from window_class import Window
from gridmap import GridMap
from pathfinder import PathFinder
from shared.fieldelements import Field
from mydataelements import MyCell,MyConnector

# constants
LOGFILE = config.logfile

DEF_RADIUS = config.default_radius
DEF_LINECOLOR = config.default_linecolor
DEF_BODYCOLOR = config.default_bodycolor
DEF_GUIDECOLOR = config.default_guidecolor
DEF_BKGDCOLOR = config.default_bkgdcolor

RAD_PAD = config.radius_padding     # increased radius of circle around bodies
CURVE_SEGS = config.curve_segments  # number of line segs in a curve

XMIN_FIELD = config.xmin_field
YMIN_FIELD = config.ymin_field
XMAX_FIELD = config.xmax_field
YMAX_FIELD = config.ymax_field
XMIN_VECTOR = config.xmin_vector
YMIN_VECTOR = config.ymin_vector
XMAX_VECTOR = config.xmax_vector
YMAX_VECTOR = config.ymax_vector
XMIN_SCREEN = config.xmin_screen
YMIN_SCREEN = config.ymin_screen
XMAX_SCREEN = config.xmax_screen
YMAX_SCREEN = config.ymax_screen
DEF_MARGIN = config.default_margin
MODE_SCREEN = 1
MODE_VECTOR = 2
MODE_DEFAULT = MODE_SCREEN
PATH_UNIT = config.path_unit
BLOCK_FUZZ = config.fuzzy_area_for_cells

MIN_CONX_DIST = config.minimum_connection_distance

MAX_LOST_PATIENCE = config.max_lost_patience

# init debugging
dbug = debug.Debug()


class MyField(Field):
    """An object representing the field.  """

    cellClass = MyCell
    connectorClass = MyConnector

    def __init__(self):

        self.m_xmin_field = XMIN_FIELD
        self.m_ymin_field = YMIN_FIELD
        self.m_xmax_field = XMAX_FIELD
        self.m_ymax_field = YMAX_FIELD
        self.m_xmin_vector = XMIN_VECTOR
        self.m_ymin_vector = YMIN_VECTOR
        self.m_xmax_vector = XMAX_VECTOR
        self.m_ymax_vector = YMAX_VECTOR
        self.m_xmin_screen = XMIN_SCREEN
        self.m_ymin_screen = YMIN_SCREEN
        self.m_xmax_screen = XMAX_SCREEN
        self.m_ymax_screen = YMAX_SCREEN
        self.m_path_unit = PATH_UNIT
        self.m_output_mode = MODE_DEFAULT
        self.m_path_scale = 1
        self.m_screen_scale = 1
        self.m_vector_scale = 1
        # our default margins, one will be overwriten below
        self.m_xmargin = int(self.m_xmax_screen*DEF_MARGIN)
        self.m_ymargin = int(self.m_ymax_screen*DEF_MARGIN)
        self.set_scaling()
        self.m_screen = object
        self.path_grid = object
        self.pathfinder = object
        super(MyField, self).__init__()

        self.make_path_grid()

    # Screen Stuff

    def init_screen(self):
        # initialize window
        #(xmax_screen,ymax_screen) = self.screenMax()
        #self.m_screen = pyglet.window.Window(width=xmax_screen,height=ymax_screen)
        width = self.m_xmax_screen - self.m_xmin_screen
        height = self.m_ymax_screen - self.m_ymin_screen
        if dbug.LEV & dbug.FIELD: print "field:init_screen"
        self.m_screen = Window(self,width=width,height=height)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        # ... perform some additional initialisation
        pyglet.gl.glClearColor(*DEF_BKGDCOLOR)
        self.m_screen.clear()
        # register draw routing with pyglet
        # TESTED: These functions are being called correctly, and params are
        # being passed correctly
        self.m_screen.set_minimum_size(XMAX_SCREEN/4, YMAX_SCREEN/4)
        self.m_screen.set_visible()

    # Scaling

    def set_scaling(self,pmin_field=None,pmax_field=None,pmin_vector=None,pmax_vector=None,
                      pmin_screen=None,pmax_screen=None,path_unit=None,output_mode=None):
        """Set up scaling in the field.

        A word about graphics scaling:
         * The vision tracking system (our input data) measures in meters.
         * The laser DAC measures in uh, int16? -32,768 to 32,768
         * Pyglet measures in pixels at the screen resolution of the window you create
         * The pathfinding units are each some ratio of the smallest expected radius

         So we will keep eveything internally in centemeters (so we can use ints
         instead of floats), and then convert it to the appropriate units before 
         display depending on the output mode

         """

        if pmin_field is not None:
            self.m_xmin_field = pmin_field[0]
            self.m_ymin_field = pmin_field[1]
        if pmax_field is not None:
            self.m_xmax_field = pmax_field[0]
            self.m_ymax_field = pmax_field[1]
        if pmin_vector is not None:
            self.m_xmin_vector = pmin_vector[0]
            self.m_ymin_vector = pmin_vector[1]
        if pmax_vector is not None:
            self.m_xmax_vector  = pmax_vector[0]
            self.m_ymax_vector  = pmax_vector[1]
        if pmin_screen is not None:
            self.m_xmin_screen = pmin_screen[0]
            self.m_ymin_screen = pmin_screen[1]
        if pmax_screen is not None:
            self.m_xmax_screen = pmax_screen[0]
            self.m_ymax_screen = pmax_screen[1]
        if path_unit is not None:
            self.m_path_unit = path_unit
            self.m_path_scale = float(1)/path_unit
        if output_mode is not None:
            self.m_output_mode = output_mode
        xmin_field = self.m_xmin_field
        ymin_field = self.m_ymin_field
        xmax_field = self.m_xmax_field
        ymax_field = self.m_ymax_field
        xmin_vector = self.m_xmin_vector
        ymin_vector = self.m_ymin_vector
        xmax_vector = self.m_xmax_vector
        ymax_vector = self.m_ymax_vector
        xmin_screen = self.m_xmin_screen
        ymin_screen = self.m_ymin_screen
        xmax_screen = self.m_xmax_screen
        ymax_screen = self.m_ymax_screen

        # in order to find out how to display this,
        #   1) we find the aspect ratio (x/y) of the screen or vector (depending on the
        #      mode). 
        #   2) Then if the aspect ratio (x/y) of the reported field is greater, we
        #      set the x axis to stretch to the edges of screen (or vector) and then use
        #      that value to determine the scaling.
        #   3) But if the aspect ratio (x/y) of the reported field is less than,
        #      we set the y axis to stretch to the top and bottom of screen (or
        #      vector) and use that value to determine the scaling.

        # aspect ratios used only for comparison
        field_aspect = float(xmax_field-xmin_field)/(ymax_field-ymin_field)
        if self.m_output_mode == MODE_SCREEN:
            display_aspect = float(xmax_screen-xmin_screen)/(ymax_screen-ymin_screen)
        else:
            display_aspect = float(xmax_vector-xmin_vector)/(ymax_vector-ymin_vector)
        if field_aspect > display_aspect:
            if dbug.LEV & dbug.FIELD: print "Field:SetScaling:Longer in the x dimension"
            field_xlen=xmax_field-xmin_field
            if field_xlen:
                self.m_xmargin = int(xmax_screen*DEF_MARGIN)
                # scale = vector_width / field_width
                self.m_vector_scale = \
                    float(xmax_vector-xmin_vector)/field_xlen
                # scale = (screen_width - margin) / field_width
                self.m_screen_scale = \
                    float(xmax_screen-xmin_screen-(self.m_xmargin*2))/field_xlen
                self.m_ymargin = \
                    int(((ymax_screen-ymin_screen)-((ymax_field-ymin_field)*self.m_screen_scale)) / 2)
        else:
            if dbug.LEV & dbug.FIELD: print "Field:SetScaling:Longer in the y dimension"
            field_ylen=ymax_field-ymin_field
            if field_ylen:
                self.m_ymargin = int(ymax_screen*DEF_MARGIN)
                self.m_vector_scale = \
                    float(ymax_vector-ymin_vector)/field_ylen
                self.m_screen_scale = \
                    float(ymax_screen-ymin_screen-(self.m_ymargin*2))/field_ylen
                self.m_xmargin = \
                    int(((xmax_screen-xmin_screen)-((xmax_field-xmin_field)*self.m_screen_scale)) / 2)
        if dbug.LEV & dbug.MORE: print "Field dims:",(xmin_field,ymin_field),(xmax_field,ymax_field)
        if dbug.LEV & dbug.MORE: print "Screen dims:",(xmin_screen,ymin_screen),(xmax_screen,ymax_screen)
        #print "Screen scale:",self.m_screen_scale
        #print "Screen margins:",(self.m_xmargin,self.m_ymargin)
        if dbug.LEV & dbug.MORE: print "Used screen space:",self.rescale_pt2out((xmin_field,ymin_field)),self.rescale_pt2out((xmax_field,ymax_field))

    # Everything

    def render_all(self):
        """Render all the cells and connectors."""
        self.render_all_cells()
        self.render_all_connectors()

    def draw_all(self):
        """Draw all the cells and connectors."""
        self.draw_guides()
        self.draw_all_cells()
        self.draw_all_connectors()

    # Guides

    def draw_guides(self):
        # draw boundaries of field (if in screen mode)
        if self.m_output_mode == MODE_SCREEN:
            pyglet.gl.glColor3f(DEF_GUIDECOLOR[0],DEF_GUIDECOLOR[1],DEF_GUIDECOLOR[2])
            points = [(self.m_xmin_field,self.m_ymin_field),
                      (self.m_xmin_field,self.m_ymax_field),
                      (self.m_xmax_field,self.m_ymax_field),
                      (self.m_xmax_field,self.m_ymin_field)]
            if dbug.LEV & dbug.GRAPH: print "boundary points (field):",points
            index = [0,1,1,2,2,3,3,0]
            screen_pts = self.rescale_pt2out(points)
            if dbug.LEV & dbug.GRAPH: print "boundary points (screen):",screen_pts
            # boundary points (screen): [(72, 73), (72, 721), (1368, 721), (1368, 73)]
            if dbug.LEV & dbug.GRAPH: print "proc screen_pts:",tuple(chain(*screen_pts))
            # proc screen_pts: (72, 73, 72, 721, 1368, 721, 1368, 73)
            if dbug.LEV & dbug.GRAPH: print "PYGLET:pyglet.graphics.draw_indexed(",len(screen_pts),", pyglet.gl.GL_LINES,"
            if dbug.LEV & dbug.GRAPH: print "           ",index
            if dbug.LEV & dbug.GRAPH: print "           ('v2i',",tuple(chain(*screen_pts)),"),"
            if dbug.LEV & dbug.GRAPH: print "       )"
            pyglet.graphics.draw_indexed(len(screen_pts), pyglet.gl.GL_LINES,
                index,
                ('v2i',tuple(chain(*screen_pts))),
            )
            #point = (self.m_xmin_field,self.m_ymin_field)
            #radius = self.rescale_num2out(DEF_RADIUS)
            #shape = Circle(self,point,radius,DEF_LINECOLOR,solid=False)
            #shape.render()
            #shape.draw()
            if dbug.LEV & dbug.MORE: print "Field:drawGuides"

    # Cells
    #def create_cell(self, id):
    # moved to superclass
    #def update_cell(self, id, p=None, r=None, effects=None, color=None):
    # moved to superclass
    #def is_cell_good_to_go(self, id):
    # moved to superclass
    #def del_cell(self, id):
    # moved to superclass
    #def check_people_count(self,reported_count):
    # moved to superclass
    #def hide_cell(self, id):
    # moved to superclass
    #def hide_all_cells(self):
    # moved to superclass

    def render_cell(self,cell):
        """Render a cell.

        We first check if the cell is good.
        If not, we increment its suspect count
        If yes, render it.
        """
        if self.is_cell_good_to_go(cell.m_id):
            cell.render()
            #del self.m_suspect_cells[cell.m_id]
        else:
            if dbug.LEV & dbug.FIELD: print "Field:renderCell:Cell",cell.m_id,"is suspected lost for",\
                  self.m_suspect_cells[cell.m_id],"frames"
            if self.m_suspect_cells[cell.m_id] > MAX_LOST_PATIENCE:
                self.del_cell(cell.m_id)
            else:
                self.m_suspect_cells[cell.m_id] += 1

    def render_all_cells(self):
        # we don't call the Cell's render-er directly because we have some
        # logic here at this level
        for cell in self.m_cell_dict.values():
            self.render_cell(cell)

    def draw_cell(self,cell):
        cell.draw()

    def draw_all_cells(self):
        # we don't call the Cell's draw-er directly because we may want
        # to introduce logic at this level
        for cell in self.m_cell_dict.values():
            self.draw_cell(cell)

    # Connectors

    #def create_connector(self, id, cell0, cell1):
    # moved to superclass

    #def del_connector(self,conxid):
    # moved to superclass

    def render_connector(self,connector):
        """Render a connector.

        We first check if the connector's two cells are both good.
        If not, we increment its suspect count
        If yes, render it.
        """
        if self.is_cell_good_to_go(connector.m_cell0.m_id) and \
           self.is_cell_good_to_go(connector.m_cell1.m_id):
            connector.render()
            if connector.m_id in self.m_suspect_conxs:
                del self.m_suspect_conxs[connector.m_id]
        else:
            if dbug.LEV & dbug.FIELD: print "Field:renderConnector:Conx",connector.m_id,"between",\
                connector.m_cell0.m_id,"and",connector.m_cell1.m_id,"is suspected lost"
            if self.m_suspect_conxs[connector.m_id] > MAX_LOST_PATIENCE:
                self.del_connector(connector.m_id)
            else:
                self.m_suspect_conxs[connector.m_id] += 1

    def render_all_connectors(self):
        # we don't call the Connector's render-er directly because we have some
        # logic here at this level
        for connector in self.m_connector_dict.values():
            self.render_connector(connector)

    def draw_connector(self,connector):
        connector.draw()

    def draw_all_connectors(self):
        # we don't call the Connector's draw-er directly because we may want
        # to introduce logic at this level
        for connector in self.m_connector_dict.values():
            self.draw_connector(connector)

    # Distances - TODO: temporary -- this info will come from the conduction subsys

    #def dist_sqd(self,cell0,cell1):
    # moved to superclass
    #def calc_distances(self):
    # moved to superclass

    # Paths

    # should the next two functions be in the gridmap module? No, because the GridMap
    # and Pathfinder classes have to be instantiated from somewhere. And if not
    # here they have to be called from the main loop. Better here.
    def make_path_grid(self):
        # for our pathfinding, we're going to overlay a grid over the field with
        # squares that are sized by a constant in the config file
        self.path_grid = GridMap(self.scale2path(self.m_xmax_field),
                                 self.scale2path(self.m_ymax_field))
        self.pathfinder = PathFinder(self.path_grid.successors, self.path_grid.move_cost, 
                                     self.path_grid.estimate)

    def reset_path_grid(self):
        self.path_grid.reset_grid()
        # we store the results of all the paths, why? Not sure we need to anymore
        #self.allpaths = []

    def path_score_cells(self):
        #print "***Before path: ",self.m_cell_dict
        for cell in self.m_cell_dict.values():
            self.path_grid.set_blocked(self.scale2path(cell.m_location),
                                       self.scale2path(cell.m_radius),BLOCK_FUZZ)

    def path_find_connectors(self):
        """ Find path for all the connectors.

        We sort the connectors by distance and do easy paths for the closest 
        ones first.
        """
        #connector_dict_rekeyed = self.m_connector_dict
        #for i in connector_dict_rekeyed.iterkeys():
        connector_dict_rekeyed = {}
        for connector in self.m_connector_dict.values():
            p0 = connector.m_cell0.m_location
            p1 = connector.m_cell1.m_location
            # normally we'd take the sqrt to get the distance, but here this is 
            # just used as a sort comparison, so we'll not take the hit for sqrt
            score = ((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) 
            # here we save time by sorting as we go through it
            connector_dict_rekeyed[score] = connector
        for i in sorted(connector_dict_rekeyed.iterkeys()):
            connector = connector_dict_rekeyed[i]
            print "findpath--id:",connector.m_id,"dist:",i**0.5
            connector.add_path(self.find_path(connector))

    def find_path(self, connector):
        """ Find path in path_grid and then scale it appropriately."""
        start = self.scale2path(connector.m_cell0.m_location)
        goal = self.scale2path(connector.m_cell1.m_location)
        # TODO: Either here or in compute_path we first try several simple/dumb
        # paths, reserving A* for the ones that are blocked and need more
        # smarts. We sort the connectors by distance and do easy paths for the
        # closest ones first.
        #path = list(self.path_grid.easy_path(start, goal))
        #print "connector:id",connector.m_id,"path:",path
        #if not path:
        path = list(self.pathfinder.compute_path(start, goal))
        # take results of found paths and block them on the map
        self.path_grid.set_block_line(path)
        #self.allpaths = self.allpaths + path
        return self.path2scale(path)
        
    def print_grid(self):
        self.path_grid.printme()
    # Scaling conversions

    def _convert(self,obj,scale,min1,min2):
        """Recursively converts numbers in an object.

        This function accepts single integers, tuples, lists, or combinations.

        """
        if isinstance(obj, (int, float)):
            #return(int(obj*scale) + min)
            return int((obj-min1)*scale) + min2
        elif isinstance(obj, list):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min1,min2))
            return mylist
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._convert(i,scale,min1,min2))
            return tuple(mylist)

    def scale2out(self,n):
        """Convert internal unit (cm) to units usable for the vector or screen. """
        if self.m_output_mode == MODE_SCREEN:
            return self._convert(n,self.m_screen_scale,self.m_xmin_field,self.m_xmin_screen)
        return self._convert(n,self.m_vector_scale,self.m_xmin_field,self.m_xmin_vector)

    def scale2path(self,n):
        """Convert internal unit (cm) to units usable for pathfinding. """
        return self._convert(n,self.m_path_scale,self.m_xmin_field,0)

    def path2scale(self,n):
        """Convert pathfinding units to internal unit (cm). """
        #print "m_path_scale",self.m_path_scale
        return self._convert(n,1/self.m_path_scale,0,self.m_xmin_field)

    def _rescale_pts(self,obj,scale,orig_pmin,new_pmin):
        """Recursively rescales points or lists of points.

        This function accepts single integers, tuples, lists, or combinations.

        """
        # if this is a point, rescale it
        if isinstance(obj, tuple) and len(obj) == 2 and \
           isinstance(obj[0], (int,float)) and isinstance(obj[1], (int,float)):
            x = int((obj[0]-orig_pmin[0])*scale) + new_pmin[0]
            y = int((obj[1]-orig_pmin[1])*scale) + new_pmin[1]
            return x,y
        # if this is a list, examine each element, return list
        elif isinstance(obj, (list,tuple)):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i,scale,orig_pmin,new_pmin))
            return mylist
        # if this is a tuple, examine each element, return tuple
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i,scale,orig_pmin,new_pmin))
            return tuple(mylist)
        # otherwise, we don't know what to do with it, return it
        # TODO: Consider throwing an exception
        else:
            print "ERROR: Can only rescale a point, not",obj
            return obj

    def rescale_pt2out(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (self.m_xmin_field,self.m_ymin_field)
        if self.m_output_mode == MODE_SCREEN:
            scale = self.m_screen_scale
            new_pmin = (self.m_xmin_screen+self.m_xmargin,self.m_ymin_screen+self.m_ymargin)
        else:
            scale = self.m_vector_scale
            new_pmin = (self.m_xmin_vector,self.m_ymin_vector)
        return self._rescale_pts(p,scale,orig_pmin,new_pmin)

    def rescale_num2out(self,n):
        """Convert num in internal units (cm) to units usable for the vector or screen. """
        if self.m_output_mode == MODE_SCREEN:
            scale = self.m_screen_scale
        else:
            scale = self.m_vector_scale
        return n*scale

