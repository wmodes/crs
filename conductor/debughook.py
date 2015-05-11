# code snippet, to be included in 'sitecustomize.py'
import sys

def info(etype, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(etype, value, tb)
    else:
        import traceback, pdb
        # we are NOT in interactive mode, print the exception...
        traceback.print_exception(etype, value, tb)
        print
        # ...then start the debugger in post-mortem mode.
        pdb.pm()

sys.excepthook = info
