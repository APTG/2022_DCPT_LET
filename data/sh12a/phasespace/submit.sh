#!/bin/bash

PARTICLES=1000000
JOBS=100
WALLTIME=00:59:00


generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan1.dat detect_plan1.dat plan1.dat -e ["--beamfile=beam_plan1.dat --detectfile=detect_plan1.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace1
generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan1r.dat detect_plan1r.dat plan1r.dat -e ["--beamfile=beam_plan1r.dat --detectfile=detect_plan1r.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace1r

generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan2.dat detect_plan2.dat plan2.dat -e ["--beamfile=beam_plan2.dat --detectfile=detect_plan2.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace2

generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan3i.dat detect_plan3i.dat plan3i.dat -e ["--beamfile=beam_plan3i.dat --detectfile=detect_plan3i.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace3i
generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan3j.dat detect_plan3j.dat plan3j.dat -e ["--beamfile=beam_plan3j.dat --detectfile=detect_plan3j.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace3j
generatemc -p ${PARTICLES} -j ${JOBS} . -x beam_plan3k.dat detect_plan3k.dat plan3k.dat -e ["--beamfile=beam_plan3k.dat --detectfile=detect_plan3k.dat"] -s ["-p plgrid --time ${WALLTIME}"] -w workspace3k

