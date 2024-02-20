#!/bin/bash

# script for testing the setup

./clean.sh

shieldhit --beamfile beam_plan1.dat --detectfile detect_plan1.dat --time="00:00:15" .
shieldhit --beamfile beam_plan1r.dat --detectfile detect_plan1r.dat --time="00:00:15" .
shieldhit --beamfile beam_plan2.dat --detectfile detect_plan2.dat --time="00:00:15" .
shieldhit --beamfile beam_plan3i.dat --detectfile detect_plan3i.dat --time="00:00:15" .
shieldhit --beamfile beam_plan3j.dat --detectfile detect_plan3j.dat --time="00:00:15" .
shieldhit --beamfile beam_plan3k.dat --detectfile detect_plan3k.dat --time="00:00:15" .

convertmc image --many "*.bdo"
convertmc mcpl --many "*.bdo"

# inspection
#pymcpltool NB_phasespace_plan1_p1.mcpl --stats