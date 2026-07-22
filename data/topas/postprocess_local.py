#!/usr/bin/env python3
"""Post-process local TOPAS runs into the shared .dat depth-profile format.

Mirrors the role of data/sh12a/postprocess_local.sh for TOPAS: it turns the
native TOPAS CSV scorer output into the repository's 3-column depth-profile
`.dat` files (depth[cm], value, rel_err), and writes inspection PNGs for 2D
maps plus a VERSION.txt into data/topas/results/<plan>/.

Coordinate readback (the reason this lives in one place)
-------------------------------------------------------
TOPAS scores dose/LET along its world **Y** axis. The generated source is
rotated so the beam travels world -Y. With the scorer rotation used here, the
local-Y bin index is mirrored relative to the SH12A depth axis.
This script applies the declared Y -> depth readback exactly once:

  1. read the TOPAS local-Y bin centres and map depth = -localY,
  2. read the shared isocenter-referenced depth grid from the plan's
     SHIELD-HIT12A `detect.dat` (`Z_narrow` mesh), and
  3. resample onto that 205-bin grid so the TOPAS profile is directly
     comparable to sh12a / OSH / FLUKA.

instead of the scattered `np.flip` that used to sit in the (now removed)
notebooks/topas_plan*.py.

Requires: numpy.

Usage:
    data/topas/postprocess_local.py                 # all plans with TOPAS output
    data/topas/postprocess_local.py plan02_field01_geoD_mono
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPAS_ROOT = REPO_ROOT / "data" / "topas"
MEV_PER_G_TO_GY = 1.602176634e-10

# Scorer OutputFile names in main.txt are the data/output_catalog.json keys, so a
# CSV's stem IS its output_type. Depth profiles (depth_Z.*) get the Y->depth readback;
# target spectra (spectrum_target.*.vs_ENUC) get total kinetic E -> ENUC per species.
#
DEPTH_OUTPUTS = {
    "depth_Z.DOSE.all.mat": ("NB_Z_narrow_dose_p1.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.primary.mat": ("NB_Z_narrow_dose_p2.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.protons.mat": ("NB_Z_narrow_dose_p3.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.deuterons.mat": ("NB_Z_narrow_dose_p4.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.tritons.mat": ("NB_Z_narrow_dose_p5.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.he3.mat": ("NB_Z_narrow_dose_p6.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.DOSE.alphas.mat": ("NB_Z_narrow_dose_p7.dat", "Depth profiles - dose in material (Z_narrow)"),
    "depth_Z.FLUENCE.all.mat": ("NB_Z_narrow_fluence_p1.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.primary.mat": ("NB_Z_narrow_fluence_p2.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.protons.mat": ("NB_Z_narrow_fluence_p3.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.deuterons.mat": ("NB_Z_narrow_fluence_p4.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.tritons.mat": ("NB_Z_narrow_fluence_p5.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.he3.mat": ("NB_Z_narrow_fluence_p6.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.FLUENCE.alphas.mat": ("NB_Z_narrow_fluence_p7.dat", "Depth profiles - fluence in material (Z_narrow)"),
    "depth_Z.DOSE.all.H2O": ("NB_Z_narrow_dose_water_p1.dat", "Depth profiles - dose in water (Z_narrow)"),
    "depth_Z.DOSE.primary.H2O": ("NB_Z_narrow_dose_water_p2.dat", "Depth profiles - dose in water (Z_narrow)"),
    "depth_Z.DOSE.protons.H2O": ("NB_Z_narrow_dose_water_p3.dat", "Depth profiles - dose in water (Z_narrow)"),
}

SPECTRUM_OUTPUTS = {
    "spectrum_target.FLUENCE.protons.mat.vs_ENUC": (
        "NB_target_diff_p06.dat",
        "spectrum_target.FLUENCE.protons.mat.vs_ENUC",
        1,
    ),
    "spectrum_target.FLUENCE.deuterons.mat.vs_ENUC": (
        "NB_target_diff_p07.dat",
        "spectrum_target.FLUENCE.deuterons.mat.vs_ENUC",
        2,
    ),
    "spectrum_target.FLUENCE.tritons.mat.vs_ENUC": (
        "NB_target_diff_p08.dat",
        "spectrum_target.FLUENCE.tritons.mat.vs_ENUC",
        3,
    ),
    "spectrum_target.FLUENCE.he3.mat.vs_ENUC": (
        "NB_target_diff_p09.dat",
        "spectrum_target.FLUENCE.he3.mat.vs_ENUC",
        3,
    ),
    "spectrum_target.FLUENCE.alphas.mat.vs_ENUC": (
        "NB_target_diff_p10.dat",
        "spectrum_target.FLUENCE.alphas.mat.vs_ENUC",
        4,
    ),
}

MAP_OUTPUTS = {
    "map_XY.DOSE.all.mat": "NB_XY_p1.png",
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


def read_target_enuc_grid(plan: str) -> np.ndarray:
    """Return the SH12A ENUC spectrum bin centres for NB_target_diff_p05..p11."""
    detect = REPO_ROOT / "data" / "sh12a" / "input" / plan / "detect.dat"
    emin, emax, nbins = 0.1, 300.0, 150
    if detect.is_file():
        lines = detect.read_text().splitlines()
        for i, ln in enumerate(lines):
            if "Diff1Type" in ln and "ENUC" in ln:
                for pln in reversed(lines[max(0, i - 3) : i]):
                    m = re.match(r"\s*Diff1\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(\d+)", pln)
                    if m:
                        emin, emax, nbins = float(m[1]), float(m[2]), int(m[3])
                        break
                break
    edges = np.linspace(emin, emax, nbins + 1)
    return 0.5 * (edges[:-1] + edges[1:])


def topas_output_scale(output_type: str, histories: int | None) -> float:
    """Convert native TOPAS CSV Sum values into the benchmark convention.

    TOPAS dose scorers write total Gy accumulated over the run; the prototype
    NB dose files are MeV/g/source-particle. TOPAS fluence scorers write total
    /mm2; the prototype fluence files are /cm2/source-particle.
    """
    if histories is None:
        print("  warning: unknown TOPAS history count; writing native TOPAS sums", file=sys.stderr)
        return 1.0
    if ".DOSE." in output_type:
        return 1.0 / (histories * MEV_PER_G_TO_GY)
    if ".FLUENCE." in output_type:
        return 100.0 / histories
    return 1.0


def topas_depth_profile(
    csv_path: Path,
    target_centres: np.ndarray,
    scale: float,
) -> np.ndarray | None:
    """Read a Y-binned TOPAS scorer and return [value, rel_err] resampled onto
    target_centres, after the documented Y -> depth readback."""
    y_bins: int | None = None
    y_width_cm: float | None = None
    rows: list[tuple[int, float]] = []
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            m = re.match(r"#\s*Y\s+in\s+(\d+)\s+bins\s+of\s+([-0-9.eE]+)\s+cm", s)
            if m:
                y_bins = int(m[1])
                y_width_cm = float(m[2])
            continue
        cols = [c.strip() for c in s.split(",")]
        if len(cols) < 4:
            continue
        try:
            rows.append((int(cols[1]), float(cols[3])))
        except ValueError:
            continue

    if y_bins is None or y_width_cm is None or not rows:
        print(f"  warning: could not parse TOPAS depth CSV {csv_path}", file=sys.stderr)
        return None

    values_by_y = np.zeros(y_bins, dtype=float)
    for y_idx, value in rows:
        if 0 <= y_idx < y_bins:
            values_by_y[y_idx] = value

    y_centres = (np.arange(y_bins, dtype=float) + 0.5) * y_width_cm
    y_centres -= 0.5 * y_bins * y_width_cm
    values = values_by_y

    values = values_by_y * scale

    # ---- Y -> depth readback (see module docstring / docs/coordinates.md) ----
    # Geometry A is centered at isocenter; TOPAS local-Y is opposite to the
    # shared SH12A Z_narrow depth axis.
    depth = -y_centres

    # Native CSV output currently contains only Sum, so statistical errors are
    # unavailable here.
    rel = np.zeros_like(values)

    order = np.argsort(depth)
    val_i = np.interp(target_centres, depth[order], values[order], left=0.0, right=0.0)
    rel_i = np.interp(target_centres, depth, rel, left=0.0, right=0.0)
    return np.column_stack([target_centres, val_i, rel_i])


def topas_enuc_spectrum(csv_path: Path, target_enuc: np.ndarray, scale: float, mass_number: int) -> np.ndarray | None:
    """Convert a native TOPAS Fluence-vs-PreStep-energy histogram (total kinetic
    energy, MeV) into a differential fluence spectrum vs ENUC (MeV/u).
    Returns [enuc_center, dPhi/dENUC, rel_err].
    NOTE: best-effort CSV parse; validate the column/row layout against a real
    TOPAS EBins output on the first run."""
    emin, emax, nbins = 0.0, 250.0, None
    vals: list[float] = []
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            m = re.search(
                r"Binned by pre-step energy in\s+(\d+)\s+bins\s+of\s+[-0-9.eE]+\s+\w+\s+"
                r"from\s+([-0-9.eE]+)\s+\w+\s+to\s+([-0-9.eE]+)\s+\w+",
                s,
            )
            if m:
                nbins, emin, emax = int(m[1]), float(m[2]), float(m[3])
            continue
        cols = [c.strip() for c in s.split(",") if c.strip()]
        try:
            vals.extend(float(c) for c in cols)
        except ValueError:
            continue
    if not vals:
        return None
    v = np.asarray(vals, dtype=float)
    if nbins is not None and len(v) == nbins + 2:
        # TOPAS writes underflow and overflow entries around the requested
        # energy bins. They are not part of the regular ENUC axis.
        v = v[1:-1]
    elif nbins is not None and len(v) != nbins:
        print(
            f"  warning: {csv_path.name} header says {nbins} energy bins, parsed {len(v)}",
            file=sys.stderr,
        )
    edges_total = np.linspace(emin, emax, len(v) + 1)
    ecen_enuc = 0.5 * (edges_total[:-1] + edges_total[1:]) / mass_number
    ewidth_total = edges_total[1] - edges_total[0]
    # dE_total = A * dENUC, so dPhi/dENUC = A * dPhi/dE_total.
    density = v * scale * mass_number / ewidth_total
    val_i = np.interp(target_enuc, ecen_enuc, density, left=0.0, right=0.0)
    return np.column_stack([target_enuc, val_i, np.zeros_like(target_enuc)])


def topas_2d_map_png(csv_path: Path, png_path: Path) -> bool:
    """Render a native TOPAS 2D scorer CSV to a compact inspection PNG."""
    x_bins: int | None = None
    y_bins: int | None = None
    rows: list[tuple[int, int, float]] = []
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            mx = re.match(r"#\s*X\s+in\s+(\d+)\s+bins", s)
            my = re.match(r"#\s*Y\s+in\s+(\d+)\s+bins", s)
            if mx:
                x_bins = int(mx[1])
            if my:
                y_bins = int(my[1])
            continue
        cols = [c.strip() for c in s.split(",")]
        if len(cols) < 4:
            continue
        try:
            rows.append((int(cols[0]), int(cols[1]), float(cols[3])))
        except ValueError:
            continue

    if x_bins is None or y_bins is None or not rows:
        print(f"  warning: could not parse TOPAS 2D CSV {csv_path}", file=sys.stderr)
        return False

    data = np.zeros((y_bins, x_bins), dtype=float)
    for x_idx, y_idx, value in rows:
        if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
            data[y_idx, x_idx] = value

    os.environ.setdefault("MPLCONFIGDIR", str(TOPAS_ROOT / "results" / "output" / ".matplotlib"))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  warning: matplotlib is required to write TOPAS map PNGs", file=sys.stderr)
        return False

    fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)
    im = ax.imshow(data, origin="lower", cmap="viridis", aspect="equal")
    ax.set_title(csv_path.stem)
    ax.set_xlabel("X bin")
    ax.set_ylabel("Y bin")
    fig.colorbar(im, ax=ax, shrink=0.85)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    return True


def topas_version(csv_path: Path) -> str:
    for ln in csv_path.read_text(errors="ignore").splitlines()[:40]:
        m = re.search(r"TOPAS\s+[Vv]ersion[:\s]+([^\s,]+)", ln)
        if m:
            return m[1]
    return "unknown"


def requested_histories(plan: str) -> int | None:
    main = TOPAS_ROOT / "input" / plan / "main.txt"
    if not main.is_file():
        return None
    text = main.read_text(errors="ignore")
    m = re.search(r"^\s*includeFile\s*=\s*(\S+)", text, re.MULTILINE)
    if not m:
        return None
    beam = REPO_ROOT / m[1]
    if not beam.is_file():
        return None
    mh = re.search(r"REQUESTED_HISTORIES:\s*(\d+)", beam.read_text(errors="ignore"))
    return int(mh[1]) if mh else None


def write_manifest(plan: str, results_dir: Path, version: str, outputs: dict[str, list[str]]) -> None:
    def files_for(output_types: list[str]) -> list[dict]:
        files = []
        for output_type in output_types:
            for path in outputs.get(output_type, []):
                files.append({"path": path, "output_type": output_type})
        return files

    groups = [
        (
            "Depth profiles - dose in material (Z_narrow)",
            "primary_data",
            [
                "depth_Z.DOSE.all.mat",
                "depth_Z.DOSE.primary.mat",
                "depth_Z.DOSE.protons.mat",
                "depth_Z.DOSE.deuterons.mat",
                "depth_Z.DOSE.tritons.mat",
                "depth_Z.DOSE.he3.mat",
                "depth_Z.DOSE.alphas.mat",
            ],
        ),
        (
            "Depth profiles - fluence in material (Z_narrow)",
            "primary_data",
            [
                "depth_Z.FLUENCE.all.mat",
                "depth_Z.FLUENCE.primary.mat",
                "depth_Z.FLUENCE.protons.mat",
                "depth_Z.FLUENCE.deuterons.mat",
                "depth_Z.FLUENCE.tritons.mat",
                "depth_Z.FLUENCE.he3.mat",
                "depth_Z.FLUENCE.alphas.mat",
            ],
        ),
        (
            "Depth profiles - dose in water (Z_narrow)",
            "primary_data",
            [
                "depth_Z.DOSE.all.H2O",
                "depth_Z.DOSE.primary.H2O",
                "depth_Z.DOSE.protons.H2O",
            ],
        ),
        (
            "Differential fluence spectra in target (material)",
            "derived",
            [
                "spectrum_target.FLUENCE.all.mat.vs_ENUC",
                "spectrum_target.FLUENCE.protons.mat.vs_ENUC",
                "spectrum_target.FLUENCE.deuterons.mat.vs_ENUC",
                "spectrum_target.FLUENCE.tritons.mat.vs_ENUC",
                "spectrum_target.FLUENCE.he3.mat.vs_ENUC",
                "spectrum_target.FLUENCE.alphas.mat.vs_ENUC",
            ],
        ),
    ]

    manifest_outputs = []
    for description, role, output_types in groups:
        files = files_for(output_types)
        if files:
            manifest_outputs.append({"description": description, "role": role, "files": files})

    preview_files = [{"path": p} for p in outputs.get("preview_image", [])]
    if preview_files:
        manifest_outputs.append(
            {
                "description": "2D dose map PNG previews",
                "role": "preview_image",
                "files": preview_files,
            }
        )

    stats = {"normalization": "per_primary"}
    histories = requested_histories(plan)
    if histories is not None:
        stats["n_primaries"] = histories

    manifest = {
        "schema_version": "1",
        "plan": plan,
        "code": {"name": "TOPAS", "short": "topas", "version": version},
        "frame": {
            "native": "topas-y",
            "to_patient": (
                "TOPAS slab geometry scores depth along world Y. postprocess_local.py "
                "applies the documented Y->depth readback before writing NB_Z_narrow*.dat."
            ),
            "beam_model": "v2" if plan.startswith(("plan01", "plan02", "plan03", "plan04")) else "v5",
        },
        "provenance": {
            "date": _dt.date.today().isoformat(),
            "input_path": f"data/topas/input/{plan}",
        },
        "statistics": stats,
        "capabilities": {
            "notes": (
                "Native TOPAS smoke-test outputs. Qeff, heavy recoils, and corrected "
                "LET spectra are not yet produced."
            )
        },
        "outputs": manifest_outputs,
    }
    (results_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def process_plan(input_dir: Path) -> bool:
    plan = input_dir.name
    # main.txt writes its scorer CSVs to results/output/<plan>/ (untracked scratch);
    # the tracked .dat go to results/<plan>/.
    results_dir = TOPAS_ROOT / "results" / plan
    out_dir = TOPAS_ROOT / "results" / "output" / plan
    depth_csvs = sorted(out_dir.glob("depth_Z.*.csv")) if out_dir.is_dir() else []
    spec_csvs = sorted(out_dir.glob("spectrum_target.*.vs_ENUC.csv")) if out_dir.is_dir() else []
    map_csvs = sorted(out_dir.glob("map_*.csv")) if out_dir.is_dir() else []
    if not depth_csvs and not spec_csvs and not map_csvs:
        print(f"  skip {plan}: no TOPAS depth/spectrum CSV in results/output/{plan}/")
        return False

    print(f"\n== Processing: {plan} ==")
    target = read_target_grid(plan)
    target_enuc = read_target_enuc_grid(plan)
    histories = requested_histories(plan)
    results_dir.mkdir(parents=True, exist_ok=True)

    wrote = 0
    ref_csv = depth_csvs[0] if depth_csvs else spec_csvs[0] if spec_csvs else map_csvs[0]
    manifest_outputs: dict[str, list[str]] = {}

    for csv_path in depth_csvs:                        # stem == catalog output_type
        mapped = DEPTH_OUTPUTS.get(csv_path.stem)
        if mapped is None:
            continue
        dat_name, _ = mapped
        scale = topas_output_scale(csv_path.stem, histories)
        prof = topas_depth_profile(csv_path, target, scale)  # Y->depth readback onto sh12a grid
        if prof is None:
            continue
        dat = results_dir / dat_name
        np.savetxt(dat, prof, fmt="%.6g")
        print(f"  wrote {dat.relative_to(REPO_ROOT)}")
        manifest_outputs.setdefault(csv_path.stem, []).append(dat_name)
        wrote += 1

    species_specs: list[np.ndarray] = []
    for csv_path in spec_csvs:
        mapped = SPECTRUM_OUTPUTS.get(csv_path.stem)
        if mapped is None:
            continue
        dat_name, output_type, mass_number = mapped
        scale = topas_output_scale(output_type, histories)
        spec = topas_enuc_spectrum(csv_path, target_enuc, scale, mass_number)
        if spec is None:
            continue
        species_specs.append(spec)
        dat = results_dir / dat_name
        np.savetxt(dat, spec, fmt="%.6g")
        print(f"  wrote {dat.relative_to(REPO_ROOT)}")
        manifest_outputs.setdefault(output_type, []).append(dat_name)
        wrote += 1
    if species_specs:
        all_spec = species_specs[0].copy()
        all_spec[:, 1] = sum(spec[:, 1] for spec in species_specs)
        dat_name = "NB_target_diff_p05.dat"
        output_type = "spectrum_target.FLUENCE.all.mat.vs_ENUC"
        dat = results_dir / dat_name
        np.savetxt(dat, all_spec, fmt="%.6g")
        print(f"  wrote {dat.relative_to(REPO_ROOT)}")
        manifest_outputs.setdefault(output_type, []).append(dat_name)
        wrote += 1

    for csv_path in map_csvs:
        png_name = MAP_OUTPUTS.get(csv_path.stem)
        if png_name is None:
            continue
        png = results_dir / png_name
        if topas_2d_map_png(csv_path, png):
            print(f"  wrote {png.relative_to(REPO_ROOT)}")
            manifest_outputs.setdefault("preview_image", []).append(png_name)
            wrote += 1

    version = topas_version(ref_csv)
    histories = requested_histories(plan)
    version_text = (
        f"filedate: {_dt.datetime.now().astimezone():%a, %d %b %Y %H:%M:%S %z}\n"
        f"mc_code_version: {version}\n"
    )
    if histories is not None:
        version_text += f"number_of_primaries: {histories}\n"
    version_text += "normalization: per_primary\n"
    (results_dir / "VERSION.txt").write_text(version_text)
    print(f"  wrote {(results_dir / 'VERSION.txt').relative_to(REPO_ROOT)}")
    write_manifest(plan, results_dir, version, manifest_outputs)
    print(f"  wrote {(results_dir / 'manifest.json').relative_to(REPO_ROOT)}")
    return wrote > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plans", nargs="*", help="Plan directory names (default: all with a main.txt).")
    args = ap.parse_args()

    if args.plans:
        input_dirs = [TOPAS_ROOT / "input" / p for p in args.plans]
    else:
        input_dirs = sorted(
            d for d in (TOPAS_ROOT / "input").glob("plan*_field*_geo*")
            if any(d.glob("main*.txt"))
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
