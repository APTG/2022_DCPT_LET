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
   tools/make_topas.sh              # writes data/topas/input/beam/plan<NN>_<model>_field0N.txt for all plans
   NSTAT=1000000 tools/make_topas.sh   # override target protons (low-stat local default)
   ```

   Manifest-driven (like `tools/make_spotlists.sh`): it exports every plan/field
   from DICOM. The export uses `--nozzle-side neg-z` (the verified patient-correct
   IEC convention). The generated file is beam-only and **geometry-independent**, so
   it is written once per plan into `data/topas/input/beam/` and shared by every
   geometry variant's `main.txt` (which `includeFile`s it) — mirroring how the
   SH12A/OSH spotlists are stored once per plan. Beam model: plans 01–04 export
   **both** v2 and v5, plans 05–07 v5 only. The committed `main.txt` and the
   results use **v2** for plans 01–04; the v5 beam files are provided so users can
   run the v5 variant themselves (point `main.txt`'s includeFile at
   `beam/plan<NN>_v5_field0N.txt`) without regenerating from DICOM.

2. **Run locally** at low statistics:

   ```bash
   TOPAS_EXE=/path/to/topas data/topas/run_local.sh [plan...]
   ```

3. **Post-process** the TOPAS CSV output into the shared `.dat` depth-profile
   format (applies the Y→depth readback onto the common isocenter-referenced grid)
   write inspection PNGs for 2D maps, and write `VERSION.txt`:

   ```bash
   data/topas/postprocess_local.sh [plan...]
   ```

For cluster submission, see the scripts under [slurm/](slurm/).

## Dependencies for Python data analysis

- numpy
- topas2numpy
