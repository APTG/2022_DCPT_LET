# MCNP Postprocessing

This directory's results are produced from a raw MCNP output (`.o`) file by
a single orchestrator script, `extract_tallies.sh`, which in turn calls five
standalone Python scripts that must live alongside it. Nothing is embedded
inline anymore — each step is its own file so the pipeline stays readable
and each piece can be tested/edited independently.

Results were contributed by Hrvoje Brkic.

## Layout

All six files must be kept together in the same directory:

| File | Role |
|---|---|
| `extract_tallies.sh` | Orchestrator. Splits the MCNP output into per-tally blocks (awk), writes the reduced depth/target files, then calls the five scripts below in order. |
| `compute_let_metrics.py` | DLET/TLET/DQEFF/TQEFF, native cell medium |
| `water_equivalent.py` | Water-equivalent DOSE/DLET/TLET/DQEFF/TQEFF (Bragg-Gray conversion, protons/primary only) |
| `parse_mdata.py` | Parses the companion 2D TMESH mesh dump into `xy_map.dat` / `xz_map.dat` |
| `make_png_maps.py` | Renders those maps to `xy_map_XY.png` / `xz_map_XZ.png` |
| `compute_differential_spectra.py` | Target differential fluence spectra (the subset that's physically derivable — see below) |

## Running it

```bash
./extract_tallies.sh <mcnp_output_file> [output_dir]
```

`output_dir` defaults to `./extracted_tallies`.

**Naming convention for the 2D mesh dump:** the companion TMESH dump file
must share the basename of the MCNP output file, with extension `.d`
instead of whatever the output file's extension is. For example:

```
run03.o   ->  MCNP output you pass as the argument
run03.d   ->  companion TMESH mesh dump, found automatically
```

If no matching `.d` file is found, the script skips the 2D-map steps with a
warning rather than failing.

Example:
```bash
./extract_tallies.sh path/to/run03.o data/mcnp/results/plan03_field02_geoA_rampFull
```

## What gets produced

Depth quantities are one value+error per depth cell (400–604, `Position (Z)`
in cm); target quantities are a single "cell union total" value+error over
cells 500–504.

### Depth (`depth_Z.*`)

| Files | Source | `output_type` pattern |
|---|---|---|
| `depth_Z.DOSE.{all,primary,protons,deuterons,tritons,he3,alphas}.mat` | raw MCNP F6 tallies | `depth_Z.DOSE.<species>.mat` |
| `depth_Z.FLUENCE.{all,primary,protons,deuterons,tritons,he3,alphas}.mat` | raw MCNP F4 tallies | `depth_Z.FLUENCE.<species>.mat` |
| `depth_Z.{DLET,TLET}.{all,primary,protons}.mat` | `compute_let_metrics.py`, native medium | `depth_Z.{DLET,TLET}.<species>.mat` |
| `depth_Z.{DQEFF,TQEFF}.{all,primary,protons}.mat` | `compute_let_metrics.py`, ICRP-60 Q(L) weighting | `depth_Z.{DQEFF,TQEFF}.<species>.mat` |
| `depth_Z.DOSE.{primary,protons}.H2O` | `water_equivalent.py`, Bragg-Gray | `depth_Z.DOSE.<species>.H2O` |
| `depth_Z.{DLET,TLET}.{primary,protons}.H2O` | `water_equivalent.py`, Bragg-Gray | `depth_Z.{DLET,TLET}.<species>.H2O` |
| `depth_Z.{DQEFF,TQEFF}.{primary,protons}.H2O` | `water_equivalent.py`, Bragg-Gray | not yet in `output_catalog.json` — file as `raw_output` in the manifest until it's added |

**Not produced at depth:** any `.all.H2O` variant (DOSE/DLET/TLET/DQEFF/TQEFF)
and heavy-recoil `.H2O`/LET/QEFF breakdowns. See "Known omissions" below.

### Target (`target.*`)

| Files | Source | `output_type` pattern |
|---|---|---|
| `target.DOSE.all.mat` | raw MCNP F6 tally | `target.DOSE.all.mat` |
| `target.{DLET,TLET}.{all,primary,protons}.mat` | `compute_let_metrics.py` | `target.{DLET,TLET}.<species>.mat` |
| `target.{DQEFF,TQEFF}.{all,primary,protons}.mat` | `compute_let_metrics.py` | `target.{DQEFF,TQEFF}.<species>.mat` |
| `target.{DLET,TLET}.{primary,protons}.H2O` | `water_equivalent.py`, Bragg-Gray | `target.{DLET,TLET}.<species>.H2O` |

**Not produced at target:** `target.DOSE/DQEFF/TQEFF.*.H2O` (removed by
request — only DLET/TLET-in-water are computed for the target).

### 2D maps

| Files | Source |
|---|---|
| `xy_map.dat`, `xz_map.dat` | `parse_mdata.py`, raw lateral/longitudinal mesh data |
| `xy_map_XY.png`, `xz_map_XZ.png` | `make_png_maps.py` |

Filenames must contain the literal substrings `XY`/`XZ` (case-sensitive) —
`build_pages_site.py`'s preview-image grouping matches on that substring to
sort lateral vs. longitudinal maps into the right section on the gallery
page.

**PNG styling** is matched directly against `pymchelper`'s own
`writers/plots.py` source (not eyeballed) — same `gnuplot2` colormap, same
`pcolorfast` (no aspect-ratio enforcement), same default figure size and
DPI (640×480px), same rotated colorbar label. If `pymchelper` changes its
defaults in a future version, re-diff against its source rather than
assuming this still matches.

### Target differential spectra (`spectrum_target.*`)

| File | Source | `output_type` |
|---|---|---|
| `spectrum_target.FLUENCE.all.mat.vs_DEDX` | raw tally reformat | `spectrum_target.FLUENCE.all.mat.vs_DEDX` |
| `spectrum_target.FLUENCE.primary.mat.vs_LET` | raw tally reformat | `spectrum_target.FLUENCE.primary.mat.vs_LET` |
| `spectrum_target.FLUENCE.primary.Si.vs_DEDX` | Bragg-Gray energy recovery + Si conversion | `spectrum_target.FLUENCE.primary.Si.vs_DEDX` |
| `spectrum_target.FLUENCE.protons.mat.vs_EKIN` | Bragg-Gray energy recovery | `spectrum_target.FLUENCE.protons.mat.vs_EKIN` |

**Not produced:** `all.Si.vs_DEDX`, `all.mat.vs_EKIN` (a mixed-species LET
bin has no single energy to invert — see "Known omissions"), and
deuterons/tritons/he3/alphas/heavy_recoils `.vs_EKIN` (no per-species LET
spectra are scored at the target in this MCNP deck — would need new
tallies, not a postprocessing change).

## Known omissions and why

These aren't bugs — each is a deliberate physics or scope limitation,
documented here so nobody re-derives the same investigation:

- **Mixed-species ("all") water/silicon conversion is never done.**
  Converting a LET value to a different medium requires inverting the
  medium's stopping-power curve to recover the particle's kinetic energy,
  which assumes one fixed mass/charge. An "all particles" LET bin mixes
  contributions from protons, deuterons, tritons, He-3, and alphas — the
  same LET value maps to a different energy per species, so there's no
  single energy to invert to. Producing a number anyway would be silently
  wrong physics, not just a wider error bar. This is why every `.H2O` and
  `.Si` conversion is restricted to `protons`/`primary` only.
- **`depth_Z`/`target` `{DQEFF,TQEFF}.*.H2O`** are computed but not yet
  declared with an `output_type` in `output_catalog.json` — they're
  produced correctly but won't render in the cross-code comparison gallery
  until the catalog is extended. Filed under `role: raw_output` in the
  manifest in the meantime.
- **Target `DOSE`/`DQEFF`/`TQEFF`-in-water** are not produced at all (by
  request) — only `DLET`/`TLET`-in-water are computed for the target.
- **Heavy-recoil LET/QEFF/water breakdowns** are not produced — only
  dose/fluence are broken out per species that finely; LET-family
  quantities are only available for `all`/`primary`/`protons`.
- **Per-species differential spectra (p7–p11 of `NB_target_diff.bdo`)**
  aren't producible from this deck's tallies — it only scores combined
  LET *spectra* for protons/primary/all at the target, not one per heavy
  species. Would require new MCNP tallies, not a script change.
- **The Bethe-Bloch stopping-power model** (used throughout
  `water_equivalent.py` and `compute_differential_spectra.py`) has no
  shell/Barkas/Bloch corrections. It matches NIST PSTAR water values to
  about 1–2% for protons from roughly 5–250 MeV, but degrades at low
  energy — i.e. exactly the Bragg-peak region. Treat low-energy
  (high-LET, end-of-range) bins as the least reliable numbers in any
  `.H2O`/`.Si`-converted file. Bins that fall outside the model's validity
  window are dropped with a `note:`/`warning:` on stderr, not silently
  zeroed.

## Building `manifest.json`

Each plan directory needs a `manifest.json` alongside the result files,
validated by `tools/validate_manifests.py` against
`tools/manifest.schema.json`. Copy an existing MCNP manifest as a
starting template (e.g.
`data/mcnp/results/plan01_field01_geoA_SOBPcent/manifest.json`) and update:

- `plan` — must match the parent directory name exactly
- `provenance.date` — the actual run date (`"YYYY-MM-DD"`, or `null` if
  unknown — not a placeholder string)
- `outputs[]` — one block per logical group of files. Use:
  - `role: "primary_data"` for direct MCNP tally output
  - `role: "derived"` for anything computed by `compute_let_metrics.py`,
    `water_equivalent.py`, or `compute_differential_spectra.py`
  - `role: "raw_output"` for files with no `output_type` yet (e.g. the
    depth QEFF-in-water files, or `xy_map.dat`/`xz_map.dat` themselves)
  - `role: "preview_image"` for the PNG maps (no `output_type` needed)
- Every `output_type` string must exactly match a key in
  `data/output_catalog.json` — `validate_manifests.py` checks this, so a
  typo there fails validation even though the JSON itself is well-formed.

See `docs/detector_reference.md` for the full canonical scoring layout
(the "target list" this MCNP set is filling in against) and the
`output_type` naming convention in detail.

## Troubleshooting

- **Depth profile mirrored relative to OSH/SH12A:** check the depth-cell
  formula in `extract_tallies.sh`'s awk step and both `cell_depth()`
  functions in the Python scripts — they must all use the same sign
  convention (`10.2 - 0.1 * (cell_number - 400)`), not the naive
  `-10.2 + ...` mapping.
- **2D map generated but missing from the gallery:** confirm the PNG
  filename contains `XY`/`XZ` (case-sensitive) and that the manifest's
  `preview_image` block lists the correct filenames — `build_pages_site.py`
  silently drops previews whose filenames don't match either substring.
- **`validate_manifests.py` reports `unknown output_type`:** the string
  isn't in `data/output_catalog.json` yet. Either move that file into a
  `raw_output` block (no `output_type`) to unblock validation, or propose
  a catalog extension if the quantity should render in the gallery.
- **Everything for a plan disappears after a rebuild:** almost always
  means `manifest.json` itself is missing or failed validation — check
  `python tools/validate_manifests.py` output for that specific plan
  before assuming the extraction or build scripts are broken.
