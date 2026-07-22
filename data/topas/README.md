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
  -N "${NSTAT:-1000000}" \
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
project inputs. The test-mode file is self-contained: it carries `Ge/gantryAngle`,
`Ge/couchAngle`, `World -> Couch -> DCM_to_IEC -> Gantry`, `BeamPosition`, the
source, and all spot time features in a single TOPAS parameter file. Keeping those
definitions in one file avoids TOPAS 4.2.p3 include-chain conflicts and preserves
future non-zero gantry/couch angles directly from the RTPLAN.

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

### 4. Run locally (low statistics)

```bash
TOPAS_EXE=/path/to/topas data/topas/run_local.sh [plan ...]
```

Launches from the repo root (mains use repo-root-relative include paths) and creates
the scratch outdir. TOPAS must be able to resolve the beam model / native scorers.

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
