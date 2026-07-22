#!/bin/bash

# run_local.sh is only for local sanity checks (does the plan run, is the output
# reasonable). Production statistics are meant to be run on the HPC.
#
# TEMPORARY: OpenShieldHIT has no HPC submission script yet (it will rely on
# pymchelper's `generatemc`). Until then we override the beam.dat NSTAT (100k)
# with 1M primaries below, just so a local run yields halfway decent statistics.
# The sh12a run_local.sh does NOT override, so it runs beam.dat's 100k -- expect
# the two codes' local results to differ in primary count until the OSH HPC path
# exists. Once it does, drop the -n override and let beam.dat drive the count.
EXE="openshieldhit -v"
STAT="1000000"   # local-only override of beam.dat NSTAT (see note above)
INPUT_DIR="input"
THREADS=20

# List of all possible directories
ALL_DIRS=(
  plan01_field01_geoA_SOBPcent
  plan01_field01_geoB_SOBP95
  plan01_field01_geoC_SOBP74
  plan02_field01_geoD_mono
  plan03_field01_geoA_rampFull
  plan03_field02_geoA_rampFull
  plan04_field01_geoA_rampMiddle
  plan04_field02_geoA_rampMiddle
  plan05_field01_geoE_SOBP
  plan06_field01_geoF_SOBP
  plan07_field01_geoG_SOBP
)

# If no argument is provided, run for all directories in parallel
if [ $# -eq 0 ]; then
  printf "%s\n" "${ALL_DIRS[@]}" | parallel -j${THREADS} ${EXE} "${INPUT_DIR}/{}/" -vv -n${STAT}
else
  # Run only for the provided directory
  ${EXE} "${INPUT_DIR}/${1}/" -vv -n${STAT}
fi
