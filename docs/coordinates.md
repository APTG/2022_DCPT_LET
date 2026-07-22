# Coordinate conventions

This document is the **authoritative contract** for coordinate systems in this
repository. It exists because several codes internally disagree on beam direction
and axis orientation, and those disagreements are *invisible* for symmetric fields
but become silent errors for asymmetric / anthropomorphic plans.

Read this before adding a new MC code, editing a scoring geometry, writing a
plotter, or comparing 2D/3D maps across codes.


## TL;DR

1. The **DICOM/IEC patient frame is canonical** for anything 2D/3D and for anything
   anthropomorphic. It is the only frame that survives contact with real anatomy.
2. **"depth" is a derived scalar**, not a world axis: the signed distance along the
   beam central axis, increasing in the direction of travel, referenced to the
   isocenter. Every 1D `depth_Z` profile is expressed in this scalar and is therefore
   independent of a code's internal +Z / −Z choice.
3. Each MC code may keep whatever internal convention is natural to it, but must
   **declare one explicit transform to the patient frame** (in its result manifest).
   Ad-hoc, undocumented flips (`np.flip`, `RotZ 180`, "depth is really Y") are not
   allowed — they must be expressed as that one declared transform.


## Why this matters (the trap)

For a single field at gantry 0° / couch 0°, the "native MC" frame used by most codes
here (beam travels **+Z**) is exactly a **180° rotation** of the DICOM/IEC patient
frame about a lateral axis. A 180° rotation:

- flips the sign of the travel axis (harmless — this is why +Z vs −Z is a free choice
  for a symmetric water box), **and**
- **mirrors one lateral axis** (X↔−X or Y↔−Y).

With a symmetric 10×10 fluence the lateral mirror is invisible, so everything "works"
today. For asymmetric / anthropomorphic anatomy the mirror is **not** a symmetry, so
it silently flips left/right. There is currently no TPS-DICOM ingestion in the
analysis code, so nothing yet maps DICOM→sim in a principled way; the moment a TPS
overlay is added, this mirror becomes a real, wrong result.

The fix is to stop standardizing the *input geometry* convention (which would mean
painfully flipping the MCPL files and every native input) and instead standardize the
**output frame** (patient) plus the **derived depth scalar**. The +Z / −Z / Y-axis
choices then become private per-code details behind one declared transform.


## The three frames in play

| Frame | Convention | Used by |
|---|---|---|
| **Patient / DICOM / IEC** (canonical) | Beam enters from +Z, travels **−Z**; isocenter at origin. Anatomy, RTSTRUCT, RTDOSE live here. | TPS (Eclipse/RayStation); target for all cross-code 2D/3D comparison |
| **Native MC** | Source at z = −50 cm, travels **+Z**; depth = +Z | SH12A, OpenSHIELDHIT, FLUKA, `docs/`, `data/output_catalog.json`, all plotters |
| **MCPL phase-space** | Source at z = +50 cm (v2) / +60 cm (v5), travels **−Z** | MCNP, PHITS (via RSSA/SSW / dump conversion) |
| **BEV (beam's-eye-view)** | Origin = isocenter, **+Z downstream**, rotated with the gantry (`World→Couch→DCM_to_IEC→Gantry`). Coincides with Native MC at gantry/couch 0°. | TOPAS (phantom + scoring parented to dicomexport's `Gantry`) |

For a 0°/0° field the native MC frame is a 180° rotation of the patient frame (see
above). The MCPL frame is the native MC frame with the travel axis reversed (source on
the +z side). The **BEV** frame is the gantry-aware generalization: it rotates with the
gantry/couch and, at gantry/couch 0°, its +Z-downstream depth axis coincides with the
Native MC +Z — which is why TOPAS, scoring in BEV, lines up bin-for-bin with SH12A.


## Depth as a derived scalar

`depth_Z` outputs (see `data/output_catalog.json`) are 1D profiles whose x-axis is
**depth**, defined as:

> signed distance along the beam central axis from the isocenter, increasing in the
> direction of particle travel.

Because it is defined *relative to the beam and the isocenter*, depth does not depend
on whether a code stores the beam as +Z, −Z, or gantry-rotated in BEV. This is why the
existing 1D comparisons are valid across codes today and remain valid under this
contract. A code's readback must produce depth in this sense — and the cleanest way is
to **score in a frame where depth is already +Z** (as TOPAS now does in BEV), so no
`np.flip` is ever needed.


## Per-code transform to the patient frame

Each code declares its native frame and the transform to the patient frame in its
result manifest (`frame` block, see `tools/manifest.schema.json`). Summary:

| Code | Native frame | Transform to patient / derived depth |
|---|---|---|
| SH12A, OpenSHIELDHIT | Native MC (+Z, source −50) | 180° about a lateral axis for 2D/3D maps; depth = +z (already increasing along travel) |
| FLUKA | Native MC (+Z, source −50) | same as SH12A |
| MCNP, PHITS | MCPL (−Z, source +50/+60) | travel axis reversed vs native MC; depth taken along −z from source side |
| TOPAS | **BEV** (+Z downstream, gantry-rotated, origin isocenter) | Identity to the derived depth (depth = +Z directly); 2D maps come out as X–Z (longitudinal) and X–Y (transverse) in the beam frame. **No reversal, no flip.** |

**TOPAS setup.** The TOPAS input is generated by dicomexport (`--export-fmt topas`,
**dicomexport ≥ 1.4.4**) in **`--test-mode`**, exported with **`--nozzle-side
neg-z`** (the verified patient-correct IEC convention; never `pos-z` for patient
runs). The generated file is self-contained: it keeps `Ge/gantryAngle`,
`Ge/couchAngle`, the **BEV frame** (`World→Couch→DCM_to_IEC→Gantry`),
`BeamPosition`, source, and spot time features in a single TOPAS parameter chain.
[`tools/patch_topas_testmode.py`](../tools/patch_topas_testmode.py) then removes the
dicomexport test runtime/water-scorer blocks and inserts project snippets from
[`data/topas/input/patchins/`](../data/topas/input/patchins/README.md). The final
`main.txt` files **parent the slab phantom + all scoring to `Gantry`**, so everything
is scored in BEV with depth = +Z while future non-zero gantry/couch angles come
directly from the RTPLAN. Slab `TransZ` come from
[`docs/geometry.md`](geometry.md) (isocenter-referenced z), so the detector sits at
isocenter by construction. See [`data/topas/README.md`](../data/topas/README.md) for
the full toolchain.

> **Note:** because TOPAS scores in BEV (+Z = depth), the post-processing
> ([`data/topas/postprocess_local.py`](../data/topas/postprocess_local.py)) does **no**
> reversal/flip — it only resamples the +Z profile onto the shared SH12A `Z_narrow`
> grid, and the 2D maps come out X–Z / X–Y directly. (Plotter auto-remap of maps into
> the patient frame for non-zero gantry is still deferred, see below.)


## Beam model v2 vs v5 (source-plane distance)

The beam-model / phase-space **source plane** sits *upstream* of the isocenter at a
distance that depends on the beam model (see
[`data/resources/dcpt_beam_model/README.md`](../data/resources/dcpt_beam_model/README.md)):

- **v2**: 50 cm upstream (valid until July 2024).
- **v5**: 60 cm upstream (valid from August 2024). v5 was moved further upstream so
  range shifters cannot collide with the beam start positions. **v5 is also a physics
  change** (cyclotron hardware update), so the beam itself differs from v2 — not only
  the plane distance.

The beam-model parameters are defined on that plane and are **independent of transport
direction**, so the same model feeds both the +Z native setups and the −Z MCPL
phase-space. The source-plane distance is a direction-independent offset already
encapsulated by the per-code transform above; it does not change the frame
architecture. It does, however, mean:

- **Plans 01–04** span the changeover → they carry **two spotlists (v2 and v5)**.
- **Plans 05–07** are recent → **v5 only**.

Every result must record which beam model / source plane it used (manifest `frame`
block).


## 2D maps: required orientation

2D maps (`map_XZ`, `map_XY`) must be produced so that, once each code's declared
transform is applied, `x` and `y` correspond to the **patient-frame** lateral
directions and depth to the beam axis as defined above. The required orientation is
recorded in the `orientation` field of each geometry class in
[`data/output_catalog.json`](../data/output_catalog.json). Until the plotters perform
automatic remapping (deferred), maps are displayed as raw per-code PNGs selected only
by an `XZ` / `XY` filename tag — no transpose/flip reconciliation happens, so **do not**
rely on visual symmetry to conclude a map is correctly oriented. A validation guard that
cross-checks each map's declared `frame` against the catalog is planned (see Deferred).


## Deferred (not yet implemented)

- TPS RTDOSE/RTSTRUCT ingestion and direct patient-frame overlay in the plotters.
- A shared BEV↔patient transform utility and result readback that automatically remaps
  every code's 2D/3D maps into the patient frame end-to-end.
- Full anthropomorphic comparison pipeline.

Tracked in [APTG/2022_DCPT_LET#150](https://github.com/APTG/2022_DCPT_LET/issues/150).


## See also

- [`README.md`](../README.md) — native +Z convention statement (points here).
- [`docs/geometry.md`](geometry.md) — phantom / detector z-extents (patient frame).
- [`docs/scoring.md`](scoring.md) — scoring volumes and the `depth_Z` / map geometries.
- [`data/resources/phasespace/README.md`](../data/resources/phasespace/README.md) —
  MCPL source convention.
- [`data/resources/dcpt_beam_model/README.md`](../data/resources/dcpt_beam_model/README.md)
  — v2/v5 beam models.
