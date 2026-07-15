# Detector reference (`detect.dat`)

The tables below define the **canonical scoring layout** for this project. It is
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

## Media selectors (`Settings`)

Used to score in a substitute medium (water stopping power, silicon). The
keyword differs between the two codes:

| Settings name | openSHIELDHIT | SHIELD-HIT12A |
|---------------|-----------------|-----------------|
| `in_Water`    | `Material Water`| `Medium 4` |
| `in_Si`       | `Material Si`   | `Medium 5` |

> The `Medium` indices refer to the `MEDIUM` numbering in the corresponding
> `mat.dat` (4 = Water, 5 = Si).

## Output files

Each `Quantity` line becomes one page (`__pNN`) inside its `.bdo` file. Where a
filter is not given the quantity covers **all particles**.

| File | Geometry | Medium | Pages | Content |
|-------------------------------|-----------|--------|:-----:|-------------------------------------------------|
| `NB_XZ_map.bdo`               | XZ_map    | —      | 2     | Dose, DirtyDose |
| `NB_XY.bdo`                   | XY_map    | —      | 2     | Dose, DirtyDose |
| `NB_Z_narrow_dose.bdo`        | Z_narrow  | —      | 8     | Dose per particle group |
| `NB_Z_narrow_fluence.bdo`     | Z_narrow  | —      | 8     | Fluence per particle group |
| `NB_Z_narrow_dose_water.bdo`  | Z_narrow  | water  | 4     | Dose (all/primary/protons) + DirtyDose |
| `NB_Z_narrow_LET.bdo`         | Z_narrow  | —      | 6     | DLET & TLET (all/primary/protons) |
| `NB_Z_narrow_LET_water.bdo`   | Z_narrow  | water  | 6     | DLET & TLET (all/primary/protons) |
| `NB_Z_narrow_QEFF.bdo`        | Z_narrow  | —      | 6     | DQEFF & TQEFF (all/primary/protons) |
| `NB_target.bdo`               | TARGET    | —      | 13    | Dose, DLET, TLET, DQEFF, TQEFF |
| `NB_target_diff.bdo`          | TARGET    | —/Si   | 11    | Differential fluence spectra (DEDX, LET, EKIN) |
| `NB_target_water.bdo`         | TARGET    | water  | 8     | Dose, DirtyDose, DLET, TLET |
| `NB_target_water_diff.bdo`    | TARGET    | water  | 2     | Differential fluence spectra (DEDX, LET) |

**Total: 76 scoring pages.**

## Page index per file

Particle-resolved files (`NB_Z_narrow_dose`, `NB_Z_narrow_fluence`) share the
same page order:

| Page | Particle group |
|:----:|----------------|
| p1   | all particles |
| p2   | Primary |
| p3   | Protons |
| p4   | Deuterons |
| p5   | Tritons |
| p6   | He3 |
| p7   | Alphas |
| p8   | HeavyRec |

`NB_Z_narrow_dose_water`:

| Page | Quantity |
|:----:|----------|
| p1   | Dose (all), in water |
| p2   | Dose Primary, in water |
| p3   | Dose Protons, in water |
| p4   | DirtyDose, in water |

LET / Qeff files (`NB_Z_narrow_LET[_water]`, `NB_Z_narrow_QEFF`) — each metric
scored for all / Primary / Protons:

| Page | Quantity | | Page | Quantity |
|:----:|----------|-|:----:|----------|
| p1   | DLET / DQEFF (all)     | | p4 | TLET / TQEFF (all) |
| p2   | … Primary             | | p5 | … Primary |
| p3   | … Protons             | | p6 | … Protons |

`NB_target` (medium) / `NB_target_water` (water):

| File | p1 | p2 | p3–5 | p6–8 | p8–10 | p11–13 |
|------|----|----|------|------|-------|--------|
| `NB_target`       | Dose | DLET (all) | DLET/TLET blocks | … | DQEFF block | TQEFF block |
| `NB_target_water` | Dose | DirtyDose  | DLET (all/prim/prot) | TLET (all/prim/prot) | — | — |

> `NB_target` scores DOSE (p1), then DLET (p2–4), TLET (p5–7), DQEFF (p8–10),
> TQEFF (p11–13), each as all / Primary / Protons.

Differential-spectra files (`NB_target_diff`, `NB_target_water_diff`) use `Diff1`
binning; consult the `detect.dat` directly for exact bin definitions
(DEDX/LET over 0–2000, EKIN over 0.1–300 MeV LOG).

## Code-specific notes

SHIELD-HIT12A and openSHIELDHIT share the `detect.dat` syntax above, except:

- **Media selector:** `Material <name>` (openSHIELDHIT) vs `Medium <index>` (SHIELD-HIT12A) — see the table above.
- **`DirtyDose`** requires SHIELD-HIT12A ≥ v1.1.1-5 (unreleased at time of writing); older builds reject the detector.

When porting this layout to another MC code, reproduce the file names, geometries
and page order where the code supports the quantity, and document any pages that
are dropped because the code cannot score them.
