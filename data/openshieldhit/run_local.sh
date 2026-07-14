#!/bin/bash

EXE="openshieldhit"
STAT="1000000"
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
