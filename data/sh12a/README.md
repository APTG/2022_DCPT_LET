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

using `ares.cyfronet.pl`:

On login node and from the same directory as this README file run following command:

```bash
$ module load mcpartools shieldhit
$ generatemc -j100 -p2000000 -s "[ -A plgccbmc12-cpu -p plgrid --time=1:59:00]" -e "[ -t 01:55:00]" input/planX/
$ ./input/planX/run......./submit.sh
```

and do this for every plan.

## Postprocess

```bash
$ srun -p plgrid-now -N 1 -n 1 -A plgccbmc12-cpu --time=0:59:00 --pty /bin/bash -l
$ module load mcpartools shieldhit
$ ./generate_results.sh
```