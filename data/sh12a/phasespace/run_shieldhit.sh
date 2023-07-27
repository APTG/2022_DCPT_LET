#!/usr/bin/env bash

# Exit immediately if a simple command exits with a non-zero status.
set -e

# working directory, output files will be saved here
WORK_DIR={working_directory:s}

# number of particles per job
PARTICLE_NO={particle_no:d}

# seed of RNG
RNG_SEED={rnd_seed:d}

# main SHIELD-HIT12A input files
BEAM_FILE={beam_file:s}
GEO_FILE={geo_file:s}
MAT_FILE={mat_file:s}
DETECT_FILE={detect_file:s}

# go to working directory
cd {working_directory:s}

# execute simulation
shieldhit --beamfile=$BEAM_FILE --geofile=$GEO_FILE --matfile=$MAT_FILE --detectfile=$DETECT_FILE -n $PARTICLE_NO -N $RNG_SEED {engine_options:s} $WORK_DIR
convertmc mcpl --many "*phase*bdo"