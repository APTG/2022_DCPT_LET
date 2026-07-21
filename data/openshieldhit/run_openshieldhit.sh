#!/usr/bin/env bash

# generatemc (mcpartools) job template for OpenShieldHIT. Pass it to generatemc
# with `-m /path/to/run_openshieldhit.sh`. OpenShieldHIT reads the same
# SHIELD-HIT12A input format, so generatemc can drive it exactly like SH12A
# (same workspace/collect machinery); only the binary and CLI flag names differ
# from run_shieldhit.sh (--beamfile= -> --beam=, etc.). The {placeholders} are
# filled in per job by mcpartools when it writes each workspace/main_run.sh.

# Exit immediately if a simple command exits with a non-zero status.
set -e

# location of the OpenShieldHIT binary file
OPENSHIELDHIT_BIN=/net/people/plgrid/plgbassler/Projects/openshieldhit/openshieldhit

# working directory, output files will be saved here
WORK_DIR={working_directory:s}

# number of particles per job
PARTICLE_NO={particle_no:d}

# seed of RNG (OpenShieldHIT caps --seedoffset at 9999)
RNG_SEED={rnd_seed:d}

# main input files (OpenShieldHIT uses the SHIELD-HIT12A input format)
BEAM_FILE={beam_file:s}
GEO_FILE={geo_file:s}
MAT_FILE={mat_file:s}
DETECT_FILE={detect_file:s}

# go to working directory
cd {working_directory:s}

# execute simulation
# NOTE: no engine time-limit / partial-save flags (do not pass generatemc's
# `-e "[ -t ...]"`) -- OpenShieldHIT partial saving is still WIP, so each job
# must run to completion within the SLURM walltime, otherwise its work is lost.
$OPENSHIELDHIT_BIN --beam=$BEAM_FILE --geo=$GEO_FILE --mat=$MAT_FILE --detect=$DETECT_FILE -n $PARTICLE_NO -N $RNG_SEED {engine_options:s} $WORK_DIR
