#!/usr/bin/env python3
"""Post-process local TOPAS runs into the shared .dat depth-profile format.

Mirrors the role of data/sh12a/postprocess_local.sh for TOPAS: it turns the
native TOPAS CSV scorer output into the repository's 3-column depth-profile
`.dat` files (depth[cm], value, rel_err), and writes inspection PNGs for 2D
maps plus a VERSION.txt into data/topas/results/<plan>/.

Coordinate handling (no flip)
-----------------------------
TOPAS scores in BEAM coordinates: the phantom + scoring are parented to
dicomexport's "Gantry" frame, so depth = beam +Z (downstream), isocenter Z=0,
rotated with the gantry. That is the SAME sense as the SH12A grid, so there is no
flip -- depth = +Z directly. We only resample onto the shared isocenter-referenced
grid read from the plan's SHIELD-HIT12A `detect.dat` (`Z_narrow` mesh) so the TOPAS
profile lines up bin-for-bin with sh12a / OSH / FLUKA. See docs/coordinates.md.

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
# CSV's stem IS its output_type. Depth profiles (depth_Z.*) are read as depth = +Z;
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
    # Native TOPAS ProtonLET only covers protons. The all-charged and water-LET
    # pages remain absent until the corrected/custom LET scorer is available.
    "depth_Z.DLET.primary.mat": ("NB_Z_narrow_LET_p2.dat", "Depth profiles - native TOPAS proton LET in material (Z_narrow)"),
    "depth_Z.DLET.protons.mat": ("NB_Z_narrow_LET_p3.dat", "Depth profiles - native TOPAS proton LET in material (Z_narrow)"),
    "depth_Z.TLET.primary.mat": ("NB_Z_narrow_LET_p5.dat", "Depth profiles - native TOPAS proton LET in material (Z_narrow)"),
    "depth_Z.TLET.protons.mat": ("NB_Z_narrow_LET_p6.dat", "Depth profiles - native TOPAS proton LET in material (Z_narrow)"),
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
    "map_XZ.DOSE.all.mat": "NB_XZ_map_p1.png",
    "map_XY.DOSE.all.mat": "NB_XY_p1.png",
}

TARGET_OUTPUTS = {
    "target.DOSE.all.mat": ("NB_target_p01.txt", "Target scalars in material"),
    "target.DLET.primary.mat": ("NB_target_p03.txt", "Target scalars in material"),
    "target.DLET.protons.mat": ("NB_target_p04.txt", "Target scalars in material"),
    "target.TLET.primary.mat": ("NB_target_p06.txt", "Target scalars in material"),
    "target.TLET.protons.mat": ("NB_target_p07.txt", "Target scalars in material"),
    "target.DOSE.all.H2O": ("NB_target_water_p1.txt", "Target scalars in water"),
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


def topas_parameter_file(csv_path: Path) -> Path | None:
    for line in csv_path.read_text(errors="ignore").splitlines()[:20]:
        m = re.match(r"#\s*Parameter File:\s*(.+?)\s*$", line)
        if m:
            path = Path(m[1])
            return path if path.is_absolute() else REPO_ROOT / path
    return None


def topas_length_cm(param_file: Path | None, key: str, seen: set[str] | None = None) -> float:
    if param_file is None or not param_file.is_file():
        return 0.0
    seen = seen or set()
    if key in seen:
        return 0.0
    seen.add(key)

    pattern = re.compile(rf"^\s*d:{re.escape(key)}\s*=\s*([^\s#]+)(?:\s+([a-zA-Z]+))?")
    for line in param_file.read_text(errors="ignore").splitlines():
        m = pattern.match(line)
        if not m:
            continue
        value, unit = m[1], m[2] or "cm"
        try:
            length = float(value)
        except ValueError:
            length = topas_length_cm(param_file, value, seen)
        if unit == "mm":
            return length / 10.0
        if unit == "m":
            return length * 100.0
        return length
    return 0.0


def topas_output_scale(output_type: str, histories: int | None) -> float:
    """Convert native TOPAS CSV Sum values into the benchmark convention.

    TOPAS dose scorers write total Gy accumulated over the run; the prototype
    NB dose files are MeV/g/primary. TOPAS fluence scorers write total
    /mm2; the prototype fluence files are /cm2/source-particle.
    """
    if ".DLET." in output_type or ".TLET." in output_type:
        # TOPAS ProtonLET reports MeV/mm/(g/cm3); the catalog convention is MeV/cm.
        return 10.0
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
    """Read a Z-binned TOPAS scorer (beam +Z = depth) and return
    [depth, value, rel_err] resampled onto target_centres. No flip: TOPAS scores in
    beam coordinates, so depth = +Z directly (see docs/coordinates.md)."""
    z_bins: int | None = None
    z_width_cm: float | None = None
    rows: list[tuple[int, float]] = []
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            m = re.match(r"#\s*Z\s+in\s+(\d+)\s+bins\s+of\s+([-0-9.eE]+)\s+cm", s)
            if m:
                z_bins = int(m[1])
                z_width_cm = float(m[2])
            continue
        cols = [c.strip() for c in s.split(",")]
        if len(cols) < 4:
            continue
        try:
            rows.append((int(cols[2]), float(cols[3])))  # cols = x,y,z,value; z index
        except ValueError:
            continue

    if z_bins is None or z_width_cm is None or not rows:
        print(f"  warning: could not parse TOPAS depth CSV {csv_path}", file=sys.stderr)
        return None

    values_by_z = np.zeros(z_bins, dtype=float)
    for z_idx, value in rows:
        if 0 <= z_idx < z_bins:
            values_by_z[z_idx] = value

    param_file = topas_parameter_file(csv_path)
    z_offset_cm = topas_length_cm(param_file, "Ge/ScoringZBox/TransZ")
    z_centres = (np.arange(z_bins, dtype=float) + 0.5) * z_width_cm
    z_centres -= 0.5 * z_bins * z_width_cm
    z_centres += z_offset_cm
    values = values_by_z * scale

    # Beam coordinates: depth = +Z directly, no negation/flip. The box is centered
    # in the Gantry frame. Include the scorer TransZ so shifted depth scorers
    # land on the same isocenter-referenced axis as SH12A.
    depth = z_centres

    # Native CSV output currently contains only Sum, so statistical errors are
    # unavailable here.
    rel = np.zeros_like(values)

    order = np.argsort(depth)
    val_i = np.interp(target_centres, depth[order], values[order], left=0.0, right=0.0)
    rel_i = np.interp(target_centres, depth[order], rel[order], left=0.0, right=0.0)
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


def topas_2d_map_png(csv_path: Path, png_path: Path, scale: float) -> bool:
    """Render a native TOPAS 2D scorer CSV to a compact inspection PNG."""
    axis_cols = (0, 1)
    if csv_path.stem.startswith("map_XZ."):
        axis_cols = (0, 2)

    bins: dict[str, int] = {"X": 1, "Y": 1, "Z": 1}
    widths_cm: dict[str, float] = {"X": 5.0, "Y": 5.0, "Z": 0.2}
    rows: list[tuple[int, int, float]] = []
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            m = re.match(r"#\s*([XYZ])\s+in\s+(\d+)\s+bins?\s+of\s+([-0-9.eE]+)\s+cm", s)
            if m:
                bins[m[1]] = int(m[2])
                widths_cm[m[1]] = float(m[3])
            continue
        cols = [c.strip() for c in s.split(",")]
        if len(cols) < 4:
            continue
        try:
            rows.append((int(cols[axis_cols[0]]), int(cols[axis_cols[1]]), float(cols[3]) * scale))
        except ValueError:
            continue

    x_bins = bins.get("X")
    y_axis = "Z" if axis_cols[1] == 2 else "Y"
    y_bins = bins.get(y_axis)
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

    param_file = topas_parameter_file(csv_path)
    x_width = widths_cm.get("X", 1.0)
    y_width = widths_cm.get(y_axis, 1.0)
    y_offset = topas_length_cm(param_file, "Ge/ScoringXZBox/TransZ") if y_axis == "Z" else 0.0
    extent = [
        -0.5 * x_bins * x_width,
        0.5 * x_bins * x_width,
        -0.5 * y_bins * y_width + y_offset,
        0.5 * y_bins * y_width + y_offset,
    ]

    fig, ax = plt.subplots(figsize=(6.4, 4.8), constrained_layout=True)
    im = ax.imshow(data, origin="lower", cmap="gnuplot2", aspect="equal", extent=extent, vmin=0.0)
    ax.set_xlabel("Position (X) [cm]")
    ax.set_ylabel(f"Position ({y_axis}) [cm]")
    ax.grid(color="0.5", alpha=0.45)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    if ".DOSE." in csv_path.stem:
        cbar.set_label("Dose [MeV/g/prim]")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=100)
    plt.close(fig)
    return True


def topas_target_scalar(csv_path: Path, txt_path: Path, output_type: str, scale: float, histories: int | None) -> bool:
    """Write a one-voxel TOPAS target scorer as a SH12A-style scalar text file."""
    bins: dict[str, int] = {"X": 1, "Y": 1, "Z": 1}
    widths_cm: dict[str, float] = {"X": 5.0, "Y": 5.0, "Z": 0.2}
    value: float | None = None
    for line in csv_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            m = re.match(r"#\s*([XYZ])\s+in\s+(\d+)\s+bins?\s+of\s+([-0-9.eE]+)\s+cm", s)
            if m:
                bins[m[1]] = int(m[2])
                widths_cm[m[1]] = float(m[3])
            continue
        cols = [c.strip() for c in s.split(",")]
        try:
            value = float(cols[3] if len(cols) >= 4 else cols[0]) * scale
            break
        except ValueError:
            continue

    if value is None:
        print(f"  warning: could not parse TOPAS target scalar CSV {csv_path}", file=sys.stderr)
        return False

    quantity = output_type.split(".")[1]
    x_bins, y_bins, z_bins = bins["X"], bins["Y"], bins["Z"]
    x_half = 0.5 * x_bins * widths_cm["X"]
    y_half = 0.5 * y_bins * widths_cm["Y"]
    z_half = 0.5 * z_bins * widths_cm["Z"]
    primaries = float(histories) if histories is not None else 0.0

    txt_path.write_text(
        "\n".join(
            [
                "#   DETECTOR OUTPUT MSH/DMSH",
                f"#   X BIN:{x_bins:6d} Y BIN:{y_bins:6d} Z BIN:{z_bins:6d}",
                f"#                DETECTOR TYPE: {quantity:<10s}",
                f"#   X START:{-x_half: .3E} Y START:{-y_half: .3E} Z START:{-z_half: .3E}",
                f"#   X END  :{x_half: .3E} Y END  :{y_half: .3E} Z END  :{z_half: .3E}",
                f"#   PRIMARIES: {primaries:.3E}",
                f" {0.0: .7E}  {0.0: .7E}  {0.0: .7E}  {value: .16E}  {0.0: .16E}",
                "",
            ]
        )
    )
    return True


def topas_version(csv_path: Path) -> str:
    for ln in csv_path.read_text(errors="ignore").splitlines()[:40]:
        m = re.search(r"TOPAS\s+[Vv]ersion[:\s]+([^\s,]+)", ln)
        if m:
            return m[1]
    return "unknown"


def requested_histories(plan: str) -> int | None:
    sidecar = TOPAS_ROOT / "results" / "output" / plan / "REQUESTED_HISTORIES"
    if sidecar.is_file():
        mh = re.match(r"\s*(\d+)\s*$", sidecar.read_text(errors="ignore"))
        if mh:
            return int(mh[1])

    main = TOPAS_ROOT / "input" / plan / "main.txt"
    if not main.is_file():
        return None
    text = main.read_text(errors="ignore")
    mh = re.search(r"REQUESTED_HISTORIES:\s*(\d+)", text)
    if mh:
        return int(mh[1])

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
            "Depth profiles - native TOPAS proton LET in material (Z_narrow)",
            "primary_data",
            [
                "depth_Z.DLET.primary.mat",
                "depth_Z.DLET.protons.mat",
                "depth_Z.TLET.primary.mat",
                "depth_Z.TLET.protons.mat",
            ],
        ),
        (
            "Target scalars in material",
            "primary_data",
            [
                "target.DOSE.all.mat",
                "target.DLET.primary.mat",
                "target.DLET.protons.mat",
                "target.TLET.primary.mat",
                "target.TLET.protons.mat",
            ],
        ),
        (
            "Target scalars in water",
            "primary_data",
            [
                "target.DOSE.all.H2O",
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
            "native": "topas-bev",
            "to_patient": (
                "TOPAS scores in beam coordinates (depth = +Z downstream, isocenter Z=0, "
                "phantom + scoring parented to dicomexport's Gantry frame). depth = +Z "
                "directly, no flip; postprocess_local.py only resamples onto the SH12A "
                "Z_narrow grid."
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
                "Native TOPAS smoke-test outputs. Native ProtonLET depth profiles are "
                "available for primary/all protons in material only; all-charged LET, "
                "water LET, Qeff, heavy recoils, and corrected LET spectra are not yet produced."
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
    target_csvs = sorted(out_dir.glob("target.*.csv")) if out_dir.is_dir() else []
    if not depth_csvs and not spec_csvs and not map_csvs and not target_csvs:
        print(f"  skip {plan}: no TOPAS depth/spectrum CSV in results/output/{plan}/")
        return False

    print(f"\n== Processing: {plan} ==")
    target = read_target_grid(plan)
    target_enuc = read_target_enuc_grid(plan)
    histories = requested_histories(plan)
    results_dir.mkdir(parents=True, exist_ok=True)

    wrote = 0
    ref_csv = depth_csvs[0] if depth_csvs else spec_csvs[0] if spec_csvs else map_csvs[0] if map_csvs else target_csvs[0]
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
        scale = topas_output_scale(csv_path.stem, histories)
        if topas_2d_map_png(csv_path, png, scale):
            print(f"  wrote {png.relative_to(REPO_ROOT)}")
            manifest_outputs.setdefault("preview_image", []).append(png_name)
            wrote += 1

    for csv_path in target_csvs:
        mapped = TARGET_OUTPUTS.get(csv_path.stem)
        if mapped is None:
            continue
        txt_name, _ = mapped
        txt = results_dir / txt_name
        scale = topas_output_scale(csv_path.stem, histories)
        if topas_target_scalar(csv_path, txt, csv_path.stem, scale, histories):
            print(f"  wrote {txt.relative_to(REPO_ROOT)}")
            manifest_outputs.setdefault(csv_path.stem, []).append(txt_name)
            wrote += 1

    if wrote == 0:
        return False

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
