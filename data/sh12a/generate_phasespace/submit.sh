#!/bin/bash

PARTICLES=1000000
JOBS=100
WALLTIME=00:59:00

SPOTLIST1=../../resources/plans/plan01_sobp/spotlist_plan01_field01.dat
SPOTLIST2=../../resources/plans/plan02_mono/spotlist_plan02_field01.dat
SPOTLIST3=../../resources/plans/plan03_sobp_raystation/spotlist_plan03_field01.dat

BEAM1=beam_plan01_field01.dat
BEAM2=beam_plan02_field01.dat
BEAM3=beam_plan03_field01.dat

DETECT1=detect_plan01.dat
DETECT2=detect_plan02.dat
DETECT3=detect_plan03.dat

WORKSPACE1=workspace1
WORKSPACE2=workspace2
WORKSPACE3=workspace3


generatemc -p ${PARTICLES} -j ${JOBS} . -x ${BEAM1} ${SPOTLIST1} -e ["--beamfile=${BEAM1} --detectfile=${DETECT1}"] -s ["-p plgrid --time ${WALLTIME}"] -w $WORKSPACE1
generatemc -p ${PARTICLES} -j ${JOBS} . -x ${BEAM2} ${SPOTLIST2} -e ["--beamfile=${BEAM2} --detectfile=${DETECT2}"] -s ["-p plgrid --time ${WALLTIME}"] -w $WORKSPACE2
generatemc -p ${PARTICLES} -j ${JOBS} . -x ${BEAM3} ${SPOTLIST3} -e ["--beamfile=${BEAM3} --detectfile=${DETECT3}"] -s ["-p plgrid --time ${WALLTIME}"] -w $WORKSPACE3
