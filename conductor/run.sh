#!/bin/sh
# Run conductor
LOGDIR=~/Desktop/CRSLogs
[ -d $LOGDIR ] || mkdir -p $LOGDIR
while true
do
    LOGFILE=$LOGDIR/$(date +%Y%m%dT%H%M%S)-cond.log
    echo Running conductor with output to $LOGFILE
    python main.py > $LOGFILE 2>&1
    echo Conductor exitted, pausing 2 seconds to restart
    sleep 2
done
