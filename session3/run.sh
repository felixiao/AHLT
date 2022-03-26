#! /bin/bash

BASEDIR=/Users/Felix/Documents/MAI/AHLT/LAB/AHLT/
export PYTHONPATH=$BASEDIR/util

$BASEDIR/util/corenlp-server.sh -quiet true -port 9000 -timeout 15000  &
sleep 1

# python3.7 baseline-DDI.py ../data/devel devel.out > devel.stats

kill `cat /tmp/corenlp-server.running`
sleep 1
