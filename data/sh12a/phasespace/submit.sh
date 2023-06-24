#!/bin/bash
generatemc -p 1000000 -j 100 . -x beam_plan1.dat detect_plan1.dat plan1.dat -e ["--beamfile=beam_plan1.dat --detectfile=detect_plan1.dat"] -s ["-p plgrid"]
sleep 1
generatemc -p 1000000 -j 100 . -x beam_plan2.dat detect_plan2.dat plan2.dat -e ["--beamfile=beam_plan2.dat --detectfile=detect_plan2.dat"] -s ["-p plgrid"]
sleep 1
generatemc -p 1000000 -j 100 . -x beam_plan3.dat detect_plan3.dat plan3.dat -e ["--beamfile=beam_plan3.dat --detectfile=detect_plan3.dat"] -s ["-p plgrid"]