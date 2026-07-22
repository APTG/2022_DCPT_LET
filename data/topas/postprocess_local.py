#!/usr/bin/env python3
"""Post-process local TOPAS runs into the shared .dat depth-profile format.

Mirrors the role of data/sh12a/postprocess_local.sh for TOPAS: it turns the
native TOPAS CSV scorer output into the repository's 3-column depth-profile
`.dat` files (depth[cm], value, rel_err), moves them into
data/topas/results/<plan>/, and writes a VERSION.txt.

Coordinate readback (the reason this lives in one place)
-------------------------------------------------------
TOPAS scores dose/LET along its world **Y** axis, and after the
`DCM_to_IEC` (RotX=90) + scoring `RotZ 180` the increasing-Y bin index runs
*opposite* to physical depth (see docs/coordinates.md). This script applies the
declared Y -> depth readback exactly once:

  1. read the TOPAS Y bin centres and reverse them (Y -> travel direction),
  2. align the phantom entrance to the shared isocenter-referenced depth grid
     read from the plan's SHIELD-HIT12A `detect.dat` (`Z_narrow` mesh), and
  3. resample onto that 205-bin grid so the TOPAS profile is directly
     comparable to sh12a / OSH / FLUKA.

instead of the scattered `np.flip` that used to sit in the (now removed)
notebooks/topas_plan*.py.

Requires: numpy, topas2numpy.

Usage:
    data/topas/postprocess_local.py                 # all plans with TOPAS output
    data/topas/postprocess_local.py plan02_field01_geoD_mono
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPAS_ROOT = REPO_ROOT / "data" / "topas"

# TOPAS CSV scorer file -> (output_type stem for the .dat, human label).
# The current main_*.txt score DoseToWater and ProtonLET in the Y box; both are
# proton, water-referenced quantities.
CSV_OUTPUTS = {
    "Scoring_protonD_YBox.csv": ("depth_Z.DOSE.protons.H2O", "dose"),
    "Scoring_protonLET_YBox.csv": ("depth_Z.DLET.protons.H2O", "dlet"),
}


def read_target_grid(plan: str) -> np.ndarray:
    """Return the shared depth grid (bin centres, cm) from the plan's SH12A
    detect.dat Z_narrow mesh, so TOPAS lands on the exact same axis as the other
    codes. Falls back to the scoring.md default (-10.25..10.25, 205 bins)."""
    detect = REPO_ROOT / "data" / "sh12a" / "input" / plan / "detect.dat"
    zmin, zmax, nbins = -10.25, 10.25, 205
    if detect.is_file():
        lines = detect.read_text().splitlines()
        for i, ln in enumerate(lines):
            if "Name" in ln and "Z_narrow" in ln:
                for zl in lines[i : i + 6]:
                    m = re.match(r"\s*Z\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(\d+)", zl)
                    if m:
                        zmin, zmax, nbins = float(m[1]), float(m[2]), int(m[3])
                        break
                break
    else:
        print(f"  warning: {detect} not found; using default depth grid", file=sys.stderr)
    edges = np.linspace(zmin, zmax, nbins + 1)
    return 0.5 * (edges[:-1] + edges[1:])


def topas_depth_profile(csv_path: Path, target_centres: np.ndarray) -> np.ndarray | None:
    """Read a Y-binned TOPAS scorer and return [value, rel_err] resampled onto
    target_centres, after the documented Y -> depth readback."""
    try:
        from topas2numpy import BinnedResult
    except ImportError:
        print("topas2numpy is required: pip install topas2numpy", file=sys.stderr)
        raise

    res = BinnedResult(str(csv_path))
    # The scoring box is 1 x N x 1: the non-trivial axis is Y (index 1).
    y_dim = max(range(len(res.dimensions)), key=lambda d: res.dimensions[d].n_bins)
    y_centres = np.asarray(res.dimensions[y_dim].get_bin_centers(), dtype=float)
    values = np.squeeze(np.asarray(res.data["Sum"], dtype=float))

    # ---- Y -> depth readback (see module docstring / docs/coordinates.md) ----
    # Reverse so depth increases along travel, then shift the phantom entrance
    # (first TOPAS bin after reversal) onto the target grid's entrance (zmin).
    # NOTE: this entrance alignment is the one calibration to confirm against a
    # first real run; it assumes the TOPAS phantom front face and the SH12A
    # Z_narrow entrance coincide.
    depth = y_centres[::-1]
    values = values[::-1]
    depth = depth - depth[0] + target_centres[0]

    # Relative statistical error if TOPAS reported it, else zeros.
    if "Standard_Deviation" in res.data and "Histories_with_Scored_Quantity" in res.data:
        std = np.squeeze(np.asarray(res.data["Standard_Deviation"], dtype=float))[::-1]
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(values != 0, std / np.abs(values), 0.0)
    else:
        rel = np.zeros_like(values)

    val_i = np.interp(target_centres, depth, values, left=0.0, right=0.0)
    rel_i = np.interp(target_centres, depth, rel, left=0.0, right=0.0)
    return np.column_stack([target_centres, val_i, rel_i])


def topas_version(csv_path: Path) -> str:
    for ln in csv_path.read_text(errors="ignore").splitlines()[:40]:
        m = re.search(r"TOPAS\s+[Vv]ersion[:\s]+([^\s,]+)", ln)
        if m:
            return m[1]
    return "unknown"


def process_plan(input_dir: Path) -> bool:
    plan = input_dir.name
    # TOPAS writes to the outdir declared in main_*.txt (e.g. results/output/plan_1a/).
    # Search anywhere under results/ for this plan's CSVs.
    results_dir = TOPAS_ROOT / "results" / plan
    csv_dirs = {p.parent for name in CSV_OUTPUTS for p in (TOPAS_ROOT / "results").rglob(name)}
    if not csv_dirs:
        print(f"  skip {plan}: no TOPAS CSV output found under data/topas/results/")
        return False

    print(f"\n== Processing: {plan} ==")
    target = read_target_grid(plan)
    results_dir.mkdir(parents=True, exist_ok=True)

    wrote = 0
    ref_csv = None
    for out_dir in sorted(csv_dirs):
        for csv_name, (output_type, stem) in CSV_OUTPUTS.items():
            csv_path = out_dir / csv_name
            if not csv_path.is_file():
                continue
            ref_csv = ref_csv or csv_path
            prof = topas_depth_profile(csv_path, target)
            if prof is None:
                continue
            dat = results_dir / f"NB_topas_Z_narrow_{stem}.dat"
            header = f"# TOPAS depth profile, output_type={output_type}\n# depth[cm]  value  rel_err"
            np.savetxt(dat, prof, fmt="%.6g", header=header, comments="")
            print(f"  wrote {dat.relative_to(REPO_ROOT)}")
            wrote += 1

    if ref_csv is not None:
        version = topas_version(ref_csv)
        (results_dir / "VERSION.txt").write_text(
            f"filedate: {_dt.datetime.now().astimezone():%a, %d %b %Y %H:%M:%S %z}\n"
            f"mc_code_version: {version}\n"
            "normalization: per_primary\n"
        )
        print(f"  wrote {(results_dir / 'VERSION.txt').relative_to(REPO_ROOT)}")
    return wrote > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plans", nargs="*", help="Plan directory names (default: all with a main_*.txt).")
    args = ap.parse_args()

    if args.plans:
        input_dirs = [TOPAS_ROOT / "input" / p for p in args.plans]
    else:
        input_dirs = sorted(
            d for d in (TOPAS_ROOT / "input").glob("plan*_field*_geo*")
            if any(d.glob("main_*.txt"))
        )

    any_ok = False
    for d in input_dirs:
        any_ok |= process_plan(d)
    if not any_ok:
        print("\nNo TOPAS output processed. Run data/topas/run_local.sh first.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
