# SHIELD-HIT12A Simulations

`./plan_*` contain input files for shieldhit simulations. They are entirely encapsulated and do not depend on external files.

`./results` contain the results from the SH12A runs.

## How to Run

Requires SHIELD-HIT12A version `v1.0.0` or newer.

### Standalone

From this directory you can simply run:
`$shieldhit ./plan_1b`

Windows:
`shieldhit.exe plan_1b`

### On PROMETHEUS computing cluster

using `pro.cyfronet.pl`:

From the same directory as this README file run following command:

`$ generatemc -j100 -p1000000 -s "[ -p plgrid-short --time=0:59:00]" -e "[ -t 00:55:00]"  plan_1a/`

and do this for every plan. 100 hours is plenty for good statistics.

## Postprocess

Run local script `./generate_results.sh` from same directory as this README file.
