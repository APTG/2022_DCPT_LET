# SHIELD-HIT12A Simulations

`./plan*` contain input files for shieldhit simulations. They are entirely encapsulated and do not depend on external files.

`./results` contain the results from the SH12A runs.

## How to Run

Requires SHIELD-HIT12A version `v1.0.0` or newer.

### Standalone

From this directory you can simply run:
`$shieldhit ./plan01_geoB_SOBP95`

Windows:
`shieldhit.exe plan01_geoB_SOBP95`

### On ARES computing cluster

using `ares.cyfronet.pl`:

Start a interactive node, for compilation (if needed)
`$ srun -p plgrid-now -N 1 -n 1 -A plgccbmc12-cpu --time=0:59:00 --pty /bin/bash -l`
`$ module load mcpartools shieldhit`

From the same directory as this README file run following command:

`$ generatemc -j100 -p1000000 -s "[ -A plgccbmc12-cpu -p plgrid --time=0:59:00]" -e "[ -t 00:55:00]"  plan01_geoB_SOBP95/`

on login node:
`$ module load mcpartools shieldhit`
`$ ./submit.sh`

and do this for every plan. 100 hours is plenty for good statistics.

## Postprocess

Run local script `./generate_results.sh` from same directory as this README file.
