# TOPAS simulation overview

TOPAS input is assembled from three pieces, all in **beam's-eye-view (BEV)
coordinates** — depth = beam **+Z** (downstream), origin = isocenter, rotated with
the gantry. This is the third frame in [docs/coordinates.md](../../docs/coordinates.md);
scoring in it means **no world-Y, no `RotZ 180`, no `np.flip` anywhere** (in the
inputs, the post-processing, or dicomexport).

Native OpenTOPAS only — the [Villads Topas-Extension](https://github.com/Villadslj/Topas-Extension)
is not required for the current scorers (see issue #153 for the LET/Qeff extension work).

## Toolchain

```
DICOM RTPLAN ──(dicomexport ≥1.4.4 --test-mode)──▶ generated test-mode TOPAS main
                                                            │
patchins/common_*.txt + patchins/geo*.txt ──(patch_topas_testmode.py)──▶ input/<plan_field_geo>/main.txt
                                                            │
                                      run_local.sh ──▶ results/output/<plan>/*.csv   (untracked scratch)
                                                            │
                      postprocess_local.{py,sh} ──▶ results/<plan>/*.dat + *.png + VERSION.txt + manifest.json  (tracked)
```

### 1. Export a self-contained TOPAS main — dicomexport test mode

```bash
dicomexportplan \
  -b data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv \
  -p=500.0 \
  -N "${NSTAT:-100000000}" \
  --export-fmt topas \
  --nozzle-side neg-z \
  --test-mode \
  data/resources/plans/<plan>/RN....dcm \
  /tmp/<plan>_topas.txt
```

Manifest-driven, like `tools/make_spotlists.sh`. Requires **dicomexport ≥ 1.4.4**
(`--export-fmt topas`). Exported with **`--nozzle-side neg-z`** — the verified
patient-correct IEC convention (never `pos-z` for patient runs).

Use `--test-mode`, not the beam-only export, as the starting point for runnable
project inputs. Generate this canonical input at high statistics, currently
`100000000` by default, so dicomexport's integer spot weights preserve small-MU
spots. Local and production runs can then downscale from that high-resolution
vector via `run_local.sh NSTAT=...`. The test-mode file is self-contained: it
carries `Ge/gantryAngle`, `Ge/couchAngle`, `World -> Couch -> DCM_to_IEC ->
Gantry`, `BeamPosition`, the source, and all spot time features in a single TOPAS
parameter file. Keeping those definitions in one file avoids TOPAS 4.2.p3
include-chain conflicts and preserves future non-zero gantry/couch angles
directly from the RTPLAN.

Beam model: plans 01-04 export both v2 and v5, plans 05-07 v5 only; the committed
mains/results use **v2** for 01-04. The v2 source plane is 500 mm upstream, v5 is
600 mm upstream.

### 2. Patch out test setup, patch in project geometry/scorers

The project patch step removes dicomexport's test runtime block plus the test water
box and isocenter scorer:

```topas
i:Ts/NumberOfThreads
Ge/IsoBox
Sc/IsoScore
```

and inserts project snippets from
[`input/patchins/`](input/patchins/README.md). Snippets are concatenated into the
final `main.txt`; they are **not** TOPAS `includeFile` files. This is intentional:
the final runnable file should remain one self-contained parameter chain, while
project runtime/material/scorer settings come from the named patch-ins.

Example:

```bash
tools/patch_topas_testmode.py \
  /tmp/plan01_topas_field01.txt \
  data/topas/input/plan01_field01_geoA_SOBPcent/main.txt \
  --insert data/topas/input/patchins/geoA_SOBPcent_phantom.txt \
  --insert data/topas/input/patchins/common_project_runtime_materials.txt \
  --insert data/topas/input/patchins/common_native_scorers_bev.txt
```

The `common_*.txt` files hold reusable project definitions such as physics,
materials, scoring boxes, and native scorers. The `geo*.txt` files hold
geometry-specific slab phantom definitions and the scenario output directory.
For plan06/07 range-shifter runs, dicomexport emits the `Ge/RangeShifter` block
from the RTPLAN. DICOM defines `(300A,0364) IsocenterToRangeShifterDistance` as
the distance to the downstream edge of the range shifter, so the TOPAS range
shifter position follows that RTPLAN/DICOM convention.

### 3. Phantom + scorers — `<plan_field_geo>/main.txt`

The final `main.txt` contains the dicomexport frame/source plus the inserted slab
phantom and all scorers, **all parented to `Gantry`**. Slab `TransZ`/`HLZ` come
straight from
[docs/geometry.md](../../docs/geometry.md) (isocenter-referenced z → beam +Z), so the
detector plate sits at isocenter by construction. Scorers are native OpenTOPAS with
`OutputFile` == the [output catalog](../output_catalog.json) key, so post-processing
maps each CSV to its `output_type` by filename. Scoring boxes: `ScoringZBox` (depth,
205×1 mm along Z = SH12A `Z_narrow`), `ScoringXZBox` (map_XZ), `ScoringXYBox`
(map_XY at isocenter), `TargetBox` (differential spectra).

Native TOPAS `ProtonLET` depth scorers are included for material DLET/TLET for
primary protons and all protons. They are written as `NB_Z_narrow_LET_p2/p3/p5/p6`
by post-processing after converting TOPAS's `MeV/mm/(g/cm3)` output to the catalog
`MeV/cm` convention. The missing `all` charged-particle LET pages and water LET
pages still require the corrected/custom LET scorer work tracked in issue #153.

### 4. Run locally

```bash
TOPAS_EXE=/path/to/topas data/topas/run_local.sh [plan ...]
NSTAT=10000000 TOPAS_EXE=/path/to/topas data/topas/run_local.sh [plan ...]
```

Launches from the repo root and creates the scratch outdir. TOPAS must be able to
resolve the beam model / native scorers.

Without `NSTAT`, the runner uses `1000000` histories for local checks. With
`NSTAT`, it uses the requested runtime total. In both cases it writes a temporary
main under `results/output/<plan>/.runtime/`, rescales `Tf/spotWeight/Values` from
the high-stat canonical input so the spot histories sum exactly to the runtime
total, and writes `results/output/<plan>/REQUESTED_HISTORIES`.
`postprocess_local.py` reads that sidecar first, so dose and fluence remain
normalized as MeV/g/primary and /cm2/primary for the actual run statistics.

### 5. Post-process

```bash
data/topas/postprocess_local.sh [plan ...]
```

Converts `results/output/<plan>/*.csv` (untracked scratch) into the tracked
`results/<plan>/` products: depth `.dat` (depth = +Z resampled onto the SH12A grid,
**no flip**), ENUC spectra `.dat` (total E → E/A per integer nucleon), 2D-map PNGs,
`VERSION.txt`, and `manifest.json`.

## Git tracking

Only post-processed `.dat` and 2D-map `.png` under `results/<plan>/` are tracked; the
raw scorer CSVs and `results/output/` scratch are gitignored (see `.gitignore`).

## Slurm

Cluster submission scripts are under [slurm/](slurm/).
