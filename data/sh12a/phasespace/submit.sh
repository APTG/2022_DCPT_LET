#!/bin/bash

#PARTICLES=1000000
#JOBS=100
#WALLTIME=00:59:00

PARTICLES=100
JOBS=2
WALLTIME=00:02:00


ml shieldhit
ml mcpartools

#generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan1.dat detect_plan1.dat plan1.dat -e ["--beamfile=beam_plan1.dat --detectfile=detect_plan1.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace1
generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan2.dat detect_plan2.dat geo_plan2.dat plan2.dat -e ["--geofile=geo_plan2.dat --beamfile=beam_plan2.dat --detectfile=detect_plan2.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w target_workspace2 -m run_shieldhit.sh
#generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan3.dat detect_plan3.dat plan3.dat -e ["--beamfile=beam_plan3.dat --detectfile=detect_plan3.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace3