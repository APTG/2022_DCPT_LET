# Detector reference (`detect.dat`)

This page lists the **canonical scoring layout** for this project, unrolled one
row per scoring page — in the same order as it appears in `detect.dat`. It is
implemented natively in the SHIELD-HIT12A / openSHIELDHIT `detect.dat` files
under `data/sh12a/input/` and `data/openshieldhit/input/`, and is intended to
serve as the common reference for **other Monte Carlo codes** as well.

The **filter and detector sections are identical across all plans**; only the
geometry meshes (top of each file) differ per plan and must not be edited when
regenerating the detectors.

> **Not every MC code can score every quantity here.** This layout is the
> superset / target list. A code that cannot produce a given quantity (e.g.
> `DirtyDose`, dose-to-water, or a particular LET flavour) should simply omit
> those pages — and its limitations should be noted alongside its input set.

## Particle filters

| Filter | Selection | Description |
|------------|-------------------|-------------------------------------------|
| `Primary`  | `GEN=0, Z=1, A=1` | primary protons only |
| `Protons`  | `Z=1, A=1`        | all protons (primary + secondary) |
| `Deuterons`| `Z=1, A=2`        | ²H |
| `Tritons`  | `Z=1, A=3`        | ³H |
| `He3`      | `Z=2, A=3`        | ³He |
| `Alphas`   | `Z=2, A=4`        | ⁴He |
| `HeavyRec` | `Z>2`             | heavy recoils / fragments (C, O, …) |

A blank filter (`—` below) means the quantity is scored for **all particles**.

## Media selectors (`Settings`)

Used to score in a substitute medium (water stopping power, silicon). The
keyword differs between the two codes:

| Settings name | openSHIELDHIT | SHIELD-HIT12A |
|---------------|-----------------|-----------------|
| `in_Water`    | `Material Water`| `Medium 4` |
| `in_Si`       | `Material Si`   | `Medium 5` |

> The `Medium` indices refer to the `MEDIUM` numbering in the corresponding
> `mat.dat` (4 = Water, 5 = Si). A blank `Settings` (`—` below) scores in the
> geometry's own medium.

## Manifest `output_type` codes

The last column of every table below is the `output_type` string used in the
per-plan `manifest.json` files (`data/<code>/results/<plan>/manifest.json`). It
is a dotted code:

```text
<geometry>.<QUANTITY>.<particle>.<medium>[.vs_<differential>]
```

| Field | Values |
|-------------|--------------------------------------------------------------|
| geometry    | `map_XZ`, `map_XY`, `depth_Z`, `target`, `spectrum_target` |
| QUANTITY    | `DOSE`, `DIRTYDOSE`, `FLUENCE`, `DLET`, `TLET`, `DQEFF`, `TQEFF` |
| particle    | `all`, `primary`, `protons`, `deuterons`, `tritons`, `he3`, `alphas`, `heavy_recoils` |
| medium      | `mat` (geometry medium), `H2O` (water), `Si` (explicit silicon) |
| differential| `vs_DEDX`, `vs_LET`, `vs_ENUC` (spectra only) |

> ⚠️ `DIRTYDOSE` is a **proposed** new code token for the dirty-dose scorer, to be
> confirmed before the manifests are updated.

---

## Detectors (unrolled)

### `NB_XZ_map.bdo` — longitudinal XZ map (`Geo XZ_map`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|--------|----------|----------------|
| p1 | Dose      | — | — | `map_XZ.DOSE.all.mat` |
| p2 | DirtyDose | — | — | `map_XZ.DIRTYDOSE.all.mat` |

### `NB_XY.bdo` — lateral XY map (`Geo XY_map`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|--------|----------|----------------|
| p1 | Dose      | — | — | `map_XY.DOSE.all.mat` |
| p2 | DirtyDose | — | — | `map_XY.DIRTYDOSE.all.mat` |

### `NB_Z_narrow_dose.bdo` — depth dose per particle (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|-----------|----------|----------------|
| p1 | Dose | —         | — | `depth_Z.DOSE.all.mat` |
| p2 | Dose | Primary   | — | `depth_Z.DOSE.primary.mat` |
| p3 | Dose | Protons   | — | `depth_Z.DOSE.protons.mat` |
| p4 | Dose | Deuterons | — | `depth_Z.DOSE.deuterons.mat` |
| p5 | Dose | Tritons   | — | `depth_Z.DOSE.tritons.mat` |
| p6 | Dose | He3       | — | `depth_Z.DOSE.he3.mat` |
| p7 | Dose | Alphas    | — | `depth_Z.DOSE.alphas.mat` |
| p8 | Dose | HeavyRec  | — | `depth_Z.DOSE.heavy_recoils.mat` |

### `NB_Z_narrow_fluence.bdo` — depth fluence per particle (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|-----------|----------|----------------|
| p1 | Fluence | —         | — | `depth_Z.FLUENCE.all.mat` |
| p2 | Fluence | Primary   | — | `depth_Z.FLUENCE.primary.mat` |
| p3 | Fluence | Protons   | — | `depth_Z.FLUENCE.protons.mat` |
| p4 | Fluence | Deuterons | — | `depth_Z.FLUENCE.deuterons.mat` |
| p5 | Fluence | Tritons   | — | `depth_Z.FLUENCE.tritons.mat` |
| p6 | Fluence | He3       | — | `depth_Z.FLUENCE.he3.mat` |
| p7 | Fluence | Alphas    | — | `depth_Z.FLUENCE.alphas.mat` |
| p8 | Fluence | HeavyRec  | — | `depth_Z.FLUENCE.heavy_recoils.mat` |

### `NB_Z_narrow_dose_water.bdo` — depth dose in water (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1 | Dose      | —       | in_Water | `depth_Z.DOSE.all.H2O` |
| p2 | Dose      | Primary | in_Water | `depth_Z.DOSE.primary.H2O` |
| p3 | Dose      | Protons | in_Water | `depth_Z.DOSE.protons.H2O` |
| p4 | DirtyDose | —       | in_Water | `depth_Z.DIRTYDOSE.all.H2O` |

### `NB_Z_narrow_LET.bdo` — depth LET in medium (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1 | DLET | —       | — | `depth_Z.DLET.all.mat` |
| p2 | DLET | Primary | — | `depth_Z.DLET.primary.mat` |
| p3 | DLET | Protons | — | `depth_Z.DLET.protons.mat` |
| p4 | TLET | —       | — | `depth_Z.TLET.all.mat` |
| p5 | TLET | Primary | — | `depth_Z.TLET.primary.mat` |
| p6 | TLET | Protons | — | `depth_Z.TLET.protons.mat` |

### `NB_Z_narrow_LET_water.bdo` — depth LET in water (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1 | DLET | —       | in_Water | `depth_Z.DLET.all.H2O` |
| p2 | DLET | Primary | in_Water | `depth_Z.DLET.primary.H2O` |
| p3 | DLET | Protons | in_Water | `depth_Z.DLET.protons.H2O` |
| p4 | TLET | —       | in_Water | `depth_Z.TLET.all.H2O` |
| p5 | TLET | Primary | in_Water | `depth_Z.TLET.primary.H2O` |
| p6 | TLET | Protons | in_Water | `depth_Z.TLET.protons.H2O` |

### `NB_Z_narrow_QEFF.bdo` — depth effective quality factor (`Geo Z_narrow`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1 | DQEFF | —       | — | `depth_Z.DQEFF.all.mat` |
| p2 | DQEFF | Primary | — | `depth_Z.DQEFF.primary.mat` |
| p3 | DQEFF | Protons | — | `depth_Z.DQEFF.protons.mat` |
| p4 | TQEFF | —       | — | `depth_Z.TQEFF.all.mat` |
| p5 | TQEFF | Primary | — | `depth_Z.TQEFF.primary.mat` |
| p6 | TQEFF | Protons | — | `depth_Z.TQEFF.protons.mat` |

### `NB_target.bdo` — target scalars in medium (`Geo TARGET`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1  | DOSE  | —       | — | `target.DOSE.all.mat` |
| p2  | DLET  | —       | — | `target.DLET.all.mat` |
| p3  | DLET  | Primary | — | `target.DLET.primary.mat` |
| p4  | DLET  | Protons | — | `target.DLET.protons.mat` |
| p5  | TLET  | —       | — | `target.TLET.all.mat` |
| p6  | TLET  | Primary | — | `target.TLET.primary.mat` |
| p7  | TLET  | Protons | — | `target.TLET.protons.mat` |
| p8  | DQEFF | —       | — | `target.DQEFF.all.mat` |
| p9  | DQEFF | Primary | — | `target.DQEFF.primary.mat` |
| p10 | DQEFF | Protons | — | `target.DQEFF.protons.mat` |
| p11 | TQEFF | —       | — | `target.TQEFF.all.mat` |
| p12 | TQEFF | Primary | — | `target.TQEFF.primary.mat` |
| p13 | TQEFF | Protons | — | `target.TQEFF.protons.mat` |

### `NB_target_diff.bdo` — target differential spectra (`Geo TARGET`)

| Page | Quantity | Filter | Differential | Settings | `output_type` |
|:----:|-----------|---------|--------------|----------|----------------|
| p1  | Fluence | —         | DEDX (0–2000)          | —      | `spectrum_target.FLUENCE.all.mat.vs_DEDX` |
| p2  | Fluence | Primary   | LET (0–2000)           | —      | `spectrum_target.FLUENCE.primary.mat.vs_LET` |
| p3  | Fluence | —         | DEDX (0–2000)          | in_Si  | `spectrum_target.FLUENCE.all.Si.vs_DEDX` |
| p4  | Fluence | Primary   | DEDX (0–2000)          | in_Si  | `spectrum_target.FLUENCE.primary.Si.vs_DEDX` |
| p5  | Fluence | —         | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.all.mat.vs_ENUC` |
| p6  | Fluence | Protons   | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.protons.mat.vs_ENUC` |
| p7  | Fluence | Deuterons | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.deuterons.mat.vs_ENUC` |
| p8  | Fluence | Tritons   | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.tritons.mat.vs_ENUC` |
| p9  | Fluence | He3       | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.he3.mat.vs_ENUC` |
| p10 | Fluence | Alphas    | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.alphas.mat.vs_ENUC` |
| p11 | Fluence | HeavyRec  | ENUC (0.1–300 LOG)     | —      | `spectrum_target.FLUENCE.heavy_recoils.mat.vs_ENUC` |

### `NB_target_water.bdo` — target scalars in water (`Geo TARGET`)

| Page | Quantity | Filter | Settings | `output_type` |
|:----:|-----------|---------|----------|----------------|
| p1 | DOSE      | —       | in_Water | `target.DOSE.all.H2O` |
| p2 | DirtyDose | —       | in_Water | `target.DIRTYDOSE.all.H2O` |
| p3 | DLET      | —       | in_Water | `target.DLET.all.H2O` |
| p4 | DLET      | Primary | in_Water | `target.DLET.primary.H2O` |
| p5 | DLET      | Protons | in_Water | `target.DLET.protons.H2O` |
| p6 | TLET      | —       | in_Water | `target.TLET.all.H2O` |
| p7 | TLET      | Primary | in_Water | `target.TLET.primary.H2O` |
| p8 | TLET      | Protons | in_Water | `target.TLET.protons.H2O` |

### `NB_target_water_diff.bdo` — target differential spectra in water (`Geo TARGET`)

| Page | Quantity | Filter | Differential | Settings | `output_type` |
|:----:|-----------|---------|--------------|----------|----------------|
| p1 | Fluence | —       | DEDX (0–2000) | in_Water | `spectrum_target.FLUENCE.all.H2O.vs_DEDX` |
| p2 | Fluence | Primary | LET (0–2000)  | in_Water | `spectrum_target.FLUENCE.primary.H2O.vs_LET` |

**Total: 76 scoring pages across 12 output files.**

## Code-specific notes

SHIELD-HIT12A and openSHIELDHIT share the `detect.dat` syntax above, except:

- **Media selector:** `Material <name>` (openSHIELDHIT) vs `Medium <index>` (SHIELD-HIT12A) — see the table above.
- **`DirtyDose`** requires SHIELD-HIT12A ≥ v1.1.1-5 (unreleased at time of writing); older builds reject the detector.

When porting this layout to another MC code, reproduce the file names, geometries
and page order where the code supports the quantity, and document any pages that
are dropped because the code cannot score them.
