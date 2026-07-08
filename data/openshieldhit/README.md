# OpenShieldHIT Simulations

This directory contains input and result files for early tests with
[OpenShieldHIT](https://github.com/openshieldhit/openshieldhit), a new Monte
Carlo particle transport code written from scratch.

These inputs are adapted from the SHIELD-HIT12A cases in `../sh12a/input`.
They are intended both as benchmark-style comparison cases and as convenient
development test cases for OpenShieldHIT.

## Current Status

This is an early OpenShieldHIT test set. The calculations represented here are
not expected to be physics-complete yet.

Important caveats:

- The calculations use Gaussian straggling instead of Vavilov straggling.
- Secondary particles are not generated yet, so these simulations are primary
  particle only.
- Differential scoring outputs are disabled because OpenShieldHIT does not
  currently support that workflow.

Despite these limitations, the code is already very fast, and primary-particle
results are becoming useful for development comparisons.

The results included here were calculated with `1e6` primary particles. This is
intended as a quick development/test statistic; the full reference simulations
use `1e8` primary particles.

## Layout

- `input/plan*/` contains self-contained OpenShieldHIT input directories.
- `results/plan*/` contains postprocessed output files for the matching input
  directory.
- `postprocess_local.sh` converts local `.bdo` output files to PNG images and
  ASCII plot data.

The input directories deliberately duplicate a few shared material data files,
such as `Air.txt`, `Water.txt`, `Lucite.txt`, and `Polycarb.txt`, instead of
using a common directory. This keeps each plan self-contained and easy to copy
or run locally. This may need to be revisited for larger cluster workflows,
especially if these cases are later driven through `pymchelper` tooling.

## Running Simulations

These cases are useful for anyone who wants to try OpenShieldHIT on realistic
small development inputs. Run the executable against one of the input
directories:

```bash
openshieldhit ../2022_DCPT_LET/data/openshieldhit/input/plan06_field01_geoF_SOBP/ -vv -n1000000
```

This runs `1e6` primary particles with verbose output. On one tested local
single-threaded run, this case completed in about 5 minutes, which makes it a
convenient quick test while developing the transport code.

If you are developing OpenShieldHIT locally, replace `openshieldhit` with the
path to your local build, for example `./build_rel/bin/openshieldhit`.

You can replace `plan06_field01_geoF_SOBP` with any other directory under
`input/plan*/`.

## Postprocessing Local Runs

Run the postprocessing script from this directory:

```bash
./postprocess_local.sh
```

With no arguments, the script works through all directories matching
`input/plan*` in parallel. Set `THREADS=1` for serial postprocessing.

To postprocess selected plans only, pass one or more plan names or input paths:

```bash
./postprocess_local.sh plan01_field01_geoA_SOBPcent
./postprocess_local.sh input/plan01_field01_geoA_SOBPcent input/plan02_field01_geoD_mono
```

The script runs `convertmc` in each selected input directory:

```bash
convertmc image --many "*.bdo"
convertmc plotdata --many <non-2D .bdo files>
```

The 2D map files `NB_XY*.bdo` and `NB_XZ_map*.bdo` are converted to images but
are intentionally excluded from ASCII plot data conversion, since those files
would become excessively large.

Generated `NB*.png` and `NB*.dat` files are moved into the corresponding
`results/<plan>/` directory.
