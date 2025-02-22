#!/bin/bash

./clean.sh

for i in {1..3}
do
    shieldhit --beamfile beam_plan0${i}.dat --detectfile detect_plan0${i}.dat --time="00:00:15" .
done

convertmc image --many "*.bdo"
convertmc mcpl --many "*.bdo"

# inspection
#pymcpltool NB_phasespace_plan1_p1.mcpl --stats