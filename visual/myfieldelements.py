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

# installed modules

# local modules
from shared import config
from shared import debug

# local classes
from windowelements import Window
from pathelements import GridMap
from pathfinder import PathFinder
from shared.fieldelements import Field
from mydataelements import MyCell,MyConnector,MyGroup

# constants
# removed to allow multiple simultaneous modes
#MODE_SCREEN = 1
#MODE_VECTOR = 2
#MODE_DEFAULT = MODE_SCREEN
# replaced this:
#    if self.m_output_mode == MODE_SCREEN:
# with this
#    if GRAPHMODES & GRAPHOPTS['screen']:
GRAPHMODES = config.graphic_modes
GRAPHOPTS = {'screen': 1, 'osc': 2, 'etherdream':3}

LOGFILE = config.logfile

DEF_DIAM = config.default_diam
DEF_LINECOLOR = config.default_linecolor
DEF_BODYCOLOR = config.default_bodycolor
DEF_GUIDECOLOR = config.default_guidecolor
DEF_BKGDCOLOR = config.default_bkgdcolor

RAD_PAD = config.diam_padding     # increased diam of circle around bodies
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
PATH_UNIT = config.path_unit
BLOCK_FUZZ = config.fuzzy_area_for_cells

# init debugging
dbug = debug.Debug()


class MyField(Field):
    """An object representing the field.  """

    cellClass = MyCell
    connectorClass = MyConnector
    groupClass = MyGroup

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
        self.m_path_scale = 1.0/self.m_path_unit
        self.m_screen_scale = 1
        self.m_vector_scale = 1
        # our default margins, one will be overwriten below
        self.m_xmargin = int(self.m_xmax_screen*DEF_MARGIN)
        self.m_ymargin = int(self.m_ymax_screen*DEF_MARGIN)
        self.set_scaling()
        self.m_screen = object
        self.m_pathgrid = object
        self.m_pathfinder = object
        super(MyField, self).__init__()
        self.make_path_grid()

    # Screen Stuff

    def init_screen(self):
        # initialize window
        #(xmax_screen,ymax_screen) = self.screenMax()
        width = self.m_xmax_screen - self.m_xmin_screen
        height = self.m_ymax_screen - self.m_ymin_screen
        if dbug.LEV & dbug.FIELD: print "field:init_screen"
        self.m_screen = Window(self,width=width,height=height)
        # set window background color = r, g, b, alpha
        # each value goes from 0.0 to 1.0
        # ... perform some additional initialisation
        # moved to window class
        #pyglet.gl.glClearColor(*DEF_BKGDCOLOR)
        #self.m_screen.clear()
        # register draw routing with pyglet
        # TESTED: These functions are being called correctly, and params are
        # being passed correctly
        self.m_screen.set_minimum_size(XMAX_SCREEN/4, YMAX_SCREEN/4)
        self.m_screen.set_visible()

    # Scaling

    def set_scaling(self,pmin_field=None,pmax_field=None,pmin_vector=None,pmax_vector=None,
                      pmin_screen=None,pmax_screen=None,path_unit=None):
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
            self.m_path_scale = 1.0/path_unit
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

        if dbug.LEV & dbug.MORE: print "Field dims:",(xmin_field,ymin_field),\
                                                     (xmax_field,ymax_field)

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
        #if GRAPHMODES & GRAPHOPTS['osc']:
            #vector_aspect = float(xmax_vector-xmin_vector)/(ymax_vector-ymin_vector)
        if GRAPHMODES & GRAPHOPTS['screen']:
            screen_aspect = float(xmax_screen-xmin_screen)/(ymax_screen-ymin_screen)
            if field_aspect > screen_aspect:
                if dbug.LEV & dbug.MORE: print "Field:SetScaling:Longer in the x dimension"
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
                        int(((ymax_screen-ymin_screen)-
                            ((ymax_field-ymin_field)*self.m_screen_scale)) / 2)
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
                        int(((xmax_screen-xmin_screen)-
                            ((xmax_field-xmin_field)*self.m_screen_scale)) / 2)
            if dbug.LEV & dbug.MORE: print "Screen dims:",(xmin_screen,ymin_screen),\
                                                          (xmax_screen,ymax_screen)
            #print "Screen scale:",self.m_screen_scale
            #print "Screen margins:",(self.m_xmargin,self.m_ymargin)
            if dbug.LEV & dbug.MORE: print "Used screen space:",\
                        self.rescale_pt2screen((xmin_field,ymin_field)),\
                        self.rescale_pt2screen((xmax_field,ymax_field))

    # Everything

    #CHANGE: incorporated into draw
    #def render_all(self):
    #    """Render all the cells and connectors."""
    #    self.render_all_cells()
    #    self.render_all_connectors()
    #    self.render_all_groups()

    def draw_all(self):
        """Draw all the cells and connectors."""
        self.m_screen.draw_guides()
        self.draw_all_cells()
        self.calc_all_paths()
        self.draw_all_connectors()
        self.draw_all_groups()

    #CHANGE: incorporated into draw
    #def render_cell(self,cell):
    #    """Render a cell.
    #
    #    We first check if the cell is good.
    #    If not, we increment its suspect count
    #    If yes, render it.
    #    """
    #    if self.is_cell_good_to_go(cell.m_id):
    #        cell.render()
    #        #del self.m_suspect_cells[cell.m_id]

    #def render_all_cells(self):
    #    # we don't call the Cell's render-er directly because we have some
    #    # logic here at this level
    #    for cell in self.m_cell_dict.values():
    #        self.render_cell(cell)

    def draw_cell(self,cell):
        if self.is_cell_good_to_go(cell.m_id):
            cell.draw()

    def draw_all_cells(self):
        # we don't call the Cell's draw-er directly because we may want
        # to introduce logic at this level
        for cell in self.m_cell_dict.values():
            self.draw_cell(cell)

    # Connectors

    #CHANGE: incorporated into draw
    #def render_connector(self,connector):
    #    """Render a connector.
    #
    #    We first check if the connector's two cells are both good.
    #    If not, we increment its suspect count
    #    If yes, render it.
    #    """
    #    if self.is_conx_good_to_go(connector.m_id):
    #        connector.render()

    #CHANGE: incorporated into draw
    #def render_all_connectors(self):
    #    # we don't call the Connector's render-er directly because we have some
    #    # logic here at this level
    #    for connector in self.m_conx_dict.values():
    #        self.render_connector(connector)

    def draw_connector(self,connector):
        if self.is_conx_good_to_go(connector.m_id):
            connector.draw()

    def draw_all_connectors(self):
        # we don't call the Connector's draw-er directly because we may want
        # to introduce logic at this level
        for connector in self.m_conx_dict.values():
            connector.update()
            self.draw_connector(connector)


    # Groups

    #CHANGE: incorporated into draw
    #def render_group(self,group):
    #    """Render a group.
    #
    #    We first check if the group's is in the group list
    #    If yes, render it.
    #    """
    #    if self.is_group_good_to_go(group.m_id):
    #        group.render()

    #CHANGE: incorporated into draw
    #def render_all_groups(self):
    #    # we don't call the Connector's render-er directly because we have some
    #    # logic here at this level
    #    for group in self.m_group_dict.values():
    #        self.render_group(group)

    def draw_group(self,group):
        if self.is_group_good_to_go(group.m_id):
            group.draw()

    def draw_all_groups(self):
        # we don't call the Connector's draw-er directly because we may want
        # to introduce logic at this level
        for group in self.m_group_dict.values():
            self.draw_group(group)

    # Distances - TODO: temporary -- this info will come from the conductor subsys

    #def dist_sqd(self,cell0,cell1):
    # moved to superclass
    #def calc_distances(self):
    # moved to superclass

    # Paths

    def calc_all_paths(self):
        self.reset_path_grid()
        self.set_path_blocks()
        self.calc_connector_paths()

    def make_path_grid(self):
        # for our pathfinding, we're going to overlay a grid over the field with
        # squares that are sized by a constant in the config file
        origdim = (self.m_xmax_field, self.m_ymax_field)
        newdim = self.rescale_pt2path(origdim)
        self.m_pathgrid = GridMap(
                                *self.rescale_pt2path(
                                        (self.m_xmax_field, self.m_ymax_field)))
        self.m_pathfinder = PathFinder(
                                self.m_pathgrid.successors, 
                                self.m_pathgrid.move_cost, 
                                self.m_pathgrid.estimate)

    def reset_path_grid(self):
        self.m_pathgrid.reset_grid()
        # we store the results of all the paths, why? Not sure we need to anymore
        #self.allpaths = []

    def set_path_blocks(self):
        #print "***Before path: ",self.m_cell_dict
        for cell in self.m_cell_dict.values():
            if self.is_cell_good_to_go(cell.m_id):
                origpt = (cell.m_x, cell.m_y)
                newpt = self.rescale_pt2path(origpt)
                self.m_pathgrid.set_blocked(
                        self.rescale_pt2path((cell.m_x, cell.m_y)),
                        self.rescale_num2path(cell.m_diam/2),
                        BLOCK_FUZZ)

    def calc_connector_paths(self):
        """ Find path for all the connectors.

        We sort the connectors by distance and do easy paths for the closest 
        ones first.
        """
        #conx_dict_rekeyed = self.m_conx_dict
        #for i in conx_dict_rekeyed.iterkeys():
        conx_dict_rekeyed = {}
        for connector in self.m_conx_dict.values():
            if self.is_conx_good_to_go(connector.m_id):
                # normally we'd take the sqrt to get the distance, but here this is 
                # just used as a sort comparison, so we'll not take the hit for sqrt
                score = (connector.m_cell0.m_x - connector.m_cell1.m_x)**2 + \
                        (connector.m_cell0.m_y - connector.m_cell1.m_y)**2
                # here we save time by reindexing as we go through it
                conx_dict_rekeyed[score] = connector
        for i in sorted(conx_dict_rekeyed.iterkeys()):
            connector = conx_dict_rekeyed[i]
            #print "findpath--id:",connector.m_id,"dist:",i**0.5
            path = self.find_path(connector)
            connector.add_path(path)
            #import pdb;pdb.set_trace()

    def find_path(self, connector):
        """ Find path in path_grid and then scale it appropriately."""
        start = self.rescale_pt2path((connector.m_cell0.m_x, connector.m_cell0.m_y))
        goal = self.rescale_pt2path((connector.m_cell1.m_x, connector.m_cell1.m_y))
        # TODO: Either here or in compute_path we first try several simple/dumb
        # paths, reserving A* for the ones that are blocked and need more
        # smarts. We sort the connectors by distance and do easy paths for the
        # closest ones first.
        path = list(self.m_pathgrid.easy_path(start, goal))
        #if not path:
        #path = list(self.m_pathfinder.compute_path(start, goal))
        # take results of found paths and block them on the map
        self.m_pathgrid.set_block_line(path)
        #self.allpaths = self.allpaths + path
        rescaled_path = self.rescale_path2pt(path)
        #import pdb;pdb.set_trace()
        return rescaled_path
        
    def print_grid(self):
        self.m_pathgrid.printme()
    # Scaling conversions

    def _convert(self,obj,scale,min1,min2):
        """Recursively converts numbers in an object.

        This function accepts single integers, tuples, lists, or combinations.

        """
        if isinstance(obj, (int, float)):
            #return(int(obj*scale) + min)
            if isinstance(min1, int) and isinstance(min2, int):
                return int((obj-min1)*scale) + min2
            return (obj-min1)*scale + min2
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

    def scale2screen(self,n):
        """Convert internal unit (m) to units usable for screen. """
        return self._convert(n,self.m_screen_scale,self.m_xmin_field,self.m_xmin_screen)

    def scale2vector(self,n):
        """Convert internal unit (m) to units usable for vector. """
        return self._convert(n,self.m_vector_scale,self.m_xmin_field,self.m_xmin_vector)

    def scale2path(self,n):
        """Convert internal unit (m) to units usable for pathfinding. """
        return self._convert(n,self.m_path_scale,self.m_xmin_field,0)

    def path2scale(self,n):
        """Convert pathfinding units to internal unit (cm). """
        #print "m_path_scale",self.m_path_scale
        return self._convert(n,1/self.m_path_scale,0,self.m_xmin_field)

    def _rescale_pts(self,obj,scale,orig_pmin,new_pmin,type=None):
        """Recursively rescales points or lists of points.

        This function accepts single integers, tuples, lists, or combinations.

        """
        # if this is a point, rescale it
        if isinstance(obj, tuple) and len(obj) == 2 and \
                isinstance(obj[0], (int,float)) and \
                isinstance(obj[1], (int,float)):
            # if we were given ints (pixel scaling), return ints
            if type == 'int':
                x = int((obj[0]-orig_pmin[0])*scale) + new_pmin[0]
                y = int((obj[1]-orig_pmin[1])*scale) + new_pmin[1]
            # otherwise (m scaling), return floats
            else:
                x = float(obj[0]-orig_pmin[0])*scale + new_pmin[0]
                y = float(obj[1]-orig_pmin[1])*scale + new_pmin[1]
            return x,y
        # if this is a list, examine each element, return list
        elif isinstance(obj, (list,tuple)):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i, scale, orig_pmin, 
                              new_pmin, type))
            return mylist
        # if this is a tuple, examine each element, return tuple
        elif isinstance(obj, tuple):
            mylist = []
            for i in obj:
                mylist.append(self._rescale_pts(i, scale, orig_pmin, new_pmin))
            return tuple(mylist)
        # otherwise, we don't know what to do with it, return it
        # TODO: Consider throwing an exception
        else:
            print "ERROR: Can only rescale a point, not",obj
            return obj

    def rescale_pt2screen(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (self.m_xmin_field,self.m_ymin_field)
        scale = self.m_screen_scale
        new_pmin = (self.m_xmin_screen+self.m_xmargin,self.m_ymin_screen+self.m_ymargin)
        return self._rescale_pts(p,scale,orig_pmin,new_pmin, 'int')

    def rescale_pt2vector(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (self.m_xmin_field,self.m_ymin_field)
        scale = self.m_vector_scale
        new_pmin = (self.m_xmin_vector,self.m_ymin_vector)
        return self._rescale_pts(p,scale,orig_pmin,new_pmin, 'float')

    def rescale_pt2path(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (self.m_xmin_field,self.m_ymin_field)
        scale = self.m_path_scale
        new_pmin = (0,0)
        return self._rescale_pts(p,scale,orig_pmin,new_pmin, 'int')

    def rescale_path2pt(self,p):
        """Convert coord in internal units (cm) to units usable for the vector or screen. """
        orig_pmin = (0.0,0.0)
        scale = 1.0/self.m_path_scale
        new_pmin = (self.m_xmin_field,self.m_ymin_field)
        return self._rescale_pts(p, scale, orig_pmin, new_pmin, 'float')

    def rescale_num2screen(self,n):
        """Convert num in internal units (cm) to units usable for screen. """
        return int(n * self.m_screen_scale)

    def rescale_num2vector(self,n):
        """Convert num in internal units (cm) to units usable for vector. """
        return float(n) * self.m_vector_scale

    def rescale_num2path(self,n):
        """Convert num in internal units (cm) to units usable for vector. """
        return int(n * self.m_path_scale)

    def rescale_path2num(self,n):
        """Convert num in internal units (cm) to units usable for vector. """
        return float(n) / self.m_path_scale

