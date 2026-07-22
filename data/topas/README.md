# TOPAS simulation overview

The TOPAS extensions needed for these simulations can be found here:
<https://github.com/Villadslj/Topas-Extension>

## Coordinate convention

TOPAS runs in the DICOM→IEC "nozzle" frame (beam along world **Y**). Depth is
recovered at post-processing time, not by ad-hoc flips. See
[docs/coordinates.md](../../docs/coordinates.md) for the authoritative contract.

## Workflow

1. **Generate the beam input** (from the DICOM plans, via dicomexport ≥ 1.4.4):

   ```bash
   tools/make_topas.sh              # writes beam_<model>_field0N.txt into each input dir
   NSTAT=1000000 tools/make_topas.sh   # override target protons (low-stat local default)
   ```

   The export uses `--nozzle-side neg-z` (the verified patient-correct IEC
   convention). The generated file is beam-only; the phantom geometry and scoring
   live in the hand-maintained `main_*.txt`, which `includeFile`s it.

2. **Run locally** at low statistics:

   ```bash
   TOPAS_EXE=/path/to/topas data/topas/run_local.sh [plan...]
   ```

3. **Post-process** the TOPAS CSV output into the shared `.dat` depth-profile
   format (applies the Y→depth readback onto the common isocenter-referenced grid)
   and write `VERSION.txt`:

   ```bash
   data/topas/postprocess_local.sh [plan...]
   ```

For cluster submission, see the scripts under [slurm/](slurm/).

## Dependencies for Python data analysis

- numpy
- topas2numpy
