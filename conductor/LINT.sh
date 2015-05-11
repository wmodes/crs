#!/bin/sh
# Run pylint on source code
SUPPRESS="-dW0613 -dC0330 -dR0201"
pylint -fparseable -d C0111 -dW0403 -dR0902 -dR0913 -dR0914 -dR0912 -dR0903 -dC0103 -dC0301 -dC0326 -dC0303 -dC0302 -dR0904 -dI0011 -dR0915 $SUPPRESS [a-o]*.py
!
