#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module that handles plots strip charts of OSC messages.
"""


__appname__ = "oscplotter.py"
__author__ = "Brent Townshend"

# core modules
from time import time
import logging
import logging.config
import sys
import os
import json
import types
import signal
import sys

# matplotlib
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# installed modules
sys.path.append('..')     # Add path to find OSC
from OSC import OSCServer, OSCClient, OSCMessage

# init logging
logger=logging.getLogger("oscplotter")



# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is
# set to False
def handle_timeout(self):
    self.timed_out = True

class OSCPlotter(object):

    """Set up OSC server and other handlers."""

    def __init__(self, port, scope):
        host="localhost"
        logger.info( "Initializing server at %s:%d"%(host,port))
        try:
            self.m_oscserver = OSCServer( (host, port) )
        except:
            logger.fatal("System:Unable to create OSC handler at %s:%d"%(host,port),exc_info=True)
            sys.exit(1)
        self.m_oscserver.timeout = 0
        self.m_oscserver.print_tracebacks = True
        self.m_scope = scope
        self.m_fnum = 0
        
        # add a method to an instance of the class
        self.m_oscserver.handle_timeout = types.MethodType(handle_timeout,self.m_oscserver)

        # this registers a 'default' handler (for unmatched messages), 
        # an /'error' handler, an '/info' handler.
        # And, if the client supports it, a '/subscribe' &
        # '/unsubscribe' handler
        self.m_oscserver.addDefaultHandlers()
        self.m_oscserver.addMsgHandler("default", self.default_handler)
        self.m_oscserver.addMsgHandler("/pf/frame", self.pf_frame)
#        self.m_oscserver.addMsgHandler("/pf/update", self.pf_update)
        self.m_oscserver.addMsgHandler("/conductor/attr", self.cond_attr)

    def handle(self):
        self.m_oscserver.handle_request()

    def cond_attr(self, path, tags, args, source):
        attr=args[0]
        uid=args[1]
        value=args[2]
        logger.info("%d.%s=%f"%(uid,attr,value))
        if attr=="kinetic":
            self.m_scope.append(uid,self.m_fnum,value)
            
    def pf_update(self, path, tags, args, source):
        t=args[1]
        uid=args[2]
        x=args[3]
        logger.debug("uid=%d,t=%f, x=%f"%(uid,t,x))
#        self.m_scope.append(uid,t,x)

    def pf_frame(self, path, tags, args, source):
        self.m_fnum=args[0]
        if self.m_fnum%5==0:
            self.m_scope.update(self.m_fnum)
        
    def default_handler(self, path, tags, args, source):
#        logger.debug("got message for "+path+" with tags "+tags)
        return None


class ScopeChannel:
    def __init__(self,ax,c):
        logger.info("Creating new channel "+str(c))
        self.ax = ax
        self.channel = c
        self.tdata=[]
        self.ydata=[]
        self.line=None
        
    def prune(self,mint,maxt):
        "Keep only points in given time range"
        self.ydata=[self.ydata[i] for i in range(len(self.tdata)) if self.tdata[i]<=maxt and self.tdata[i]>=mint]
        self.tdata=[self.tdata[i] for i in range(len(self.tdata)) if self.tdata[i]<=maxt and self.tdata[i]>=mint]
        if len(self.tdata)==0 and self.line != None:
            logger.info("Removing line for channel "+str(self.channel))
            self.line.remove()
            self.line=None
            
    def append(self,t,y):
        self.tdata.append(t)
        self.ydata.append(y)
        if self.line==None:
            logger.info("Adding new line for channel "+str(self.channel))
            self.line = Line2D(self.tdata, self.ydata)
            self.ax.add_line(self.line)
        else:
            self.line.set_data(self.tdata, self.ydata)

    def len(self):
        return len(self.tdata)

    def min(self):
        return min(self.ydata)

    def max(self):
        return max(self.ydata)
    
class Scope:
    def __init__(self, ax, history=200):
        self.ax = ax
        self.history = history
        self.future=0.1
        self.ax.set_ylim(0,1)
        self.ax.set_xlim(0, self.history)
        self.channels={}

    def append(self, c, t, y):
        if c not in self.channels:
            self.channels[c]=ScopeChannel(self.ax,c)
        self.channels[c].append(t,y)
        (bottom,top)=self.ax.get_ylim()
        if y<bottom or y>top:
            if y<bottom:
                bottom=y
            if y>top:
                top=y
            self.ax.set_ylim(bottom,top)
            
    def update(self,t):
        # Prune old data from all channels
        for c in self.channels.itervalues():
            c.prune(t-self.history,t+self.future)

        # Remove any empty channels
        self.channels={k:v for (k,v) in self.channels.iteritems() if v.len()>0}
    
        # Set axes limits
        self.ax.set_xlim(t-self.history, t+self.future)
    
        # if len(self.channels)>0:
        #     ymin=min([c.min() for c in self.channels.itervalues()])
        #     ymax=max([c.max() for c in self.channels.itervalues()])
        #     self.ax.set_ylim(ymin,ymax)

        # Redraw
        self.ax.figure.canvas.draw()

# init logging
def setup_logging(default_path='logging.json',     default_level=logging.INFO,env_key='LOG_CFG'):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

# Handle control-C
keepRunning=True
def signal_handler(signal, frame):
        global keepRunning
        print '<Ctrl+C>'
        keepRunning=False

def main():
    signal.signal(signal.SIGINT, signal_handler)
    setup_logging()
    fig, ax = plt.subplots()
    scope = Scope(ax)
    plt.show(block=False)
    osc = OSCPlotter(7790,scope)
    while keepRunning:
        try: 
            osc.handle()
        except:
            logger.fatal("Caught exception")
            sys.exit(1)
        
if __name__ == '__main__':
    sys.exit(main())
