#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pathfinder module

Co-related Space is an interactive multimedia installation that engages the
themes of presence, interaction, and place. Using motion tracking, laser light
and a generative soundscape, it encourages interactions between participants,
visually and sonically transforming a regularly trafficked space. Co-related
Space highlights participants' active engagement and experimentation with sound
and light, including complex direct and indirect behavior and relationships.

"""

__appname__ = "pathfinder.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# core modules

# installed modules

# local modules
from shared import config

# local classes
from priorityqueueset import PriorityQueueSet
from gridmap import GridMap

# constants
LOGFILE = config.logfile


class PathFinder(object):
    """ Computes a path in a graph using the A* algorithm.
    
        Initialize the object and then repeatedly compute_path to 
        get the path between a start point and an end point.
        
        The points on a graph are required to be hashable and 
        comparable with __eq__. Other than that, they may be 
        represented as you wish, as long as the functions 
        supplied to the constructor know how to handle them.

    """

    def __init__(self, successors, move_cost, heuristic_to_goal):
        """ Create a new PathFinder. Provided with several 
            functions that represent your graph and the costs of
            moving through it.
        
            successors:
                A function that receives a point as a single 
                argument and returns a list of "successor" points,
                the points on the graph that can be reached from
                the given point.
            
            move_cost:
                A function that receives two points as arguments
                and returns the numeric cost of moving from the 
                first to the second.
                
            heuristic_to_goal:
                A function that receives a point and a goal point,
                and returns the numeric heuristic estimation of 
                the cost of reaching the goal from the point.
        """
        self.successors = successors
        self.move_cost = move_cost
        self.heuristic_to_goal = heuristic_to_goal

    def compute_path(self, start, goal):
        """ Compute the path between the 'start' point and the 
            'goal' point. 
            
            The path is returned as an iterator to the points, 
            including the start and goal points themselves.
            
            If no path was found, an empty list is returned.
        """
        #
        # Implementation of the A* algorithm.
        #
        closed_set = {}
        
        start_node = self._Node(start)
        goal_node = self._Node(goal)
        start_node.g_cost = 0
        start_node.f_cost = self._compute_f_cost(start_node, goal_node)
        
        open_set = PriorityQueueSet()
        open_set.add(start_node)
        
        while len(open_set) > 0:
            # Remove and get the node with the lowest f_score from 
            # the open set            
            #
            curr_node = open_set.pop_smallest()
            
            if curr_node.coord == goal_node.coord:
                return self._reconstruct_path(curr_node)
            
            closed_set[curr_node] = curr_node
            
            for succ_coord in self.successors(curr_node.coord):
                succ_node = self._Node(succ_coord)
                #original only considers this node and the next node
                #succ_node.g_cost = self._compute_g_cost(curr_node, succ_node)
                # we want to consider where we are coming from as well, so we
                # provide the parent node
                succ_node.g_cost = self._compute_g_cost(curr_node, succ_node,
                    curr_node.pred, start_node, goal_node)
                succ_node.f_cost = self._compute_f_cost(succ_node, goal_node)
                
                if succ_node in closed_set:
                    continue
                   
                if open_set.add(succ_node):
                    succ_node.pred = curr_node
        
        return []

    ########################## PRIVATE ##########################
    
    # we want to consider where we are coming from as well, so we
    # provide the parent node
    def _compute_g_cost(self, from_node, to_node, pred_node=None,
            start_node=None, goal_node=None):
        costlist = [from_node.coord, to_node.coord]
        if pred_node:
            costlist.append(pred_node.coord)
        if start_node:
            costlist.append(start_node.coord)
        if goal_node:
            costlist.append(goal_node.coord)
        #print "costlist: ",costlist
        return (from_node.g_cost + self.move_cost(*costlist))

    def _compute_f_cost(self, this_node, goal_node):
        return this_node.g_cost + self._cost_to_goal(this_node, goal_node)

    def _cost_to_goal(self, this_node, goal_node):
        return self.heuristic_to_goal(this_node.coord, goal_node.coord)

    def _reconstruct_path(self, node):
        """ Reconstructs the path to the node from the start node
            (for which .pred is None)
        """
        pth = [node.coord]
        n = node
        while n.pred:
            n = n.pred
            pth.append(n.coord)
        
        return reversed(pth)

    class _Node(object):
        """ Used to represent a node on the searched graph during
            the A* search.
            
            Each Node has its coordinate (the point it represents),
            a g_cost (the cumulative cost of reaching the point 
            from the start point), a f_cost (the estimated cost
            from the start to the goal through this point) and 
            a predecessor Node (for path construction).
            
            The Node is meant to be used inside PriorityQueueSet,
            so it implements equality and hashinig (based on the 
            coordinate, which is assumed to be unique) and 
            comparison (based on f_cost) for sorting by cost.
        """
        def __init__(self, coord, g_cost=None, f_cost=None, pred=None):
            self.coord = coord
            self.g_cost = g_cost
            self.f_cost = f_cost
            self.pred = pred
        
        def __eq__(self, other):
            return self.coord == other.coord
        
        def __cmp__(self, other):
            return cmp(self.f_cost, other.f_cost)
        
        def __hash__(self):
            return hash(self.coord)

        def __str__(self):
            return 'N(%s) -> g: %s, f: %s' % (self.coord, self.g_cost, self.f_cost)

        def __repr__(self):
            return self.__str__()


if __name__ == "__main__":
            
    start = 0, 0
    goal = 1, 7
    
    tm = GridMap(8, 8)
    # normal blocks here and there
    blocks = [  (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3),
                (2, 5), (2, 5), (2, 5), (2, 7)]
    # blocks that actually make the path inaccessible
    # to test the possibility of "overcomming" blocks
    blocks = [  (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3),
                (2, 5), (2, 5), (2, 5), (2, 7),(2,4),(2,6)]
    #for b in blocks:
        #tm.set_blocked(b)
    
    pf = PathFinder(tm.successors, tm.move_cost, tm.estimate)
    
    import time
    t = time.clock()
    path = list(pf.compute_path(start, goal))
    #tm.printme(start,goal,path)

    print "Elapsed: %s" % (time.clock() - t)
    
    print path
    
    #~ import cProfile
    #~ cProfile.run("list(pf.compute_path(start, goal))")
    
    
    


    
