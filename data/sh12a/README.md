# SHIELD-HIT12A Simulations

`./plan_*` contain input files for shieldhit simulations. They are entirely encapsulated and do not depend on external files.

`./results` contain the results from the SH12A runs.

## How to Run
Requires SHIELD-HIT12A unreleased development version,
at least `v0.9.2-207-gc0824825` or newer.

From this directory you can simply run:
`$shieldhit ./plan_1b`

On PROMETHEUS computing cluster `pro.cyfronet.pl`:

download https://raw.githubusercontent.com/DataMedSci/mcpartools/master/mcpartools/mcengine/data/run_shieldhit.sh

and edit `run_shieldhit.sh`:
a) `module load plgrid/tools/gcc/10.1.0`
b) it links to the shieldhit binary (comment out reassignment later in script)

assuming script is located in `$HOME`, you can run from this directory:

`$ generatemc -j400 -p1000000 -s "[ -p plgrid-short --time=0:59:00]" -e "[ -t 00:55:00]"  -m ~/run_shieldhit.sh plan_1a/``

and do this for every plan. 400 hours is plenty for good statistics.

## Postprocess:
Run local script `./generate_results.sh` from same directory as this README file.
