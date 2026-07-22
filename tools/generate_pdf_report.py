#!/usr/bin/env python3
"""Generate per-plan PDF reports with clickable section bookmarks.

One PDF per plan written to {out_dir}/{plan}.pdf.  Each PDF has a
PDF outline (visible in the viewer sidebar) with one entry per
geometry section.  All plans are generated in parallel.

Usage:
    python tools/generate_pdf_report.py --out-dir pages-site/plans
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pypdf import PdfReader, PdfWriter
import yaml


PAGE_SIZE = (11.69, 8.27)  # A4 landscape, inches

GEOMETRY_SECTIONS = [
    ("depth_Z",         "Depth profiles"),
    ("spectrum_target", "Target spectra"),
    ("target",          "Target volume scalars"),
    ("map_XZ",          "2D longitudinal maps (XZ)"),
    ("map_XY",          "2D transverse maps (XY)"),
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["output_types"]


def load_code_styles(data_root: Path) -> dict[str, dict]:
    styles: dict[str, dict] = {}
    for yaml_path in sorted(data_root.glob("*/code.yaml")):
        info = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        styles[info["short"]] = info
    return styles


def load_manifests(data_root: Path) -> list[dict]:
    entries = []
    for p in sorted(data_root.rglob("manifest.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        data["_dir"] = p.parent
        entries.append(data)
    return entries


def build_index(manifests: list[dict]) -> dict[tuple[str, str], list[dict]]:
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for m in manifests:
        plan = m["plan"]
        code_short = m["code"]["short"]
        result_dir = m["_dir"]
        for entry in m.get("outputs", []):
            if entry.get("role") not in ("primary_data", "derived"):
                continue
            for f in entry.get("files", []):
                ot = f.get("output_type")
                if not ot:
                    continue
                key = (plan, ot, code_short)
                if key in seen:
                    continue
                seen.add(key)
                index[(plan, ot)].append(
                    {"code_short": code_short, "path": result_dir / f["path"]}
                )
    return dict(index)


def collect_preview_images(manifests: list[dict]) -> dict[str, dict[str, list[Path]]]:
    previews: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
    for m in manifests:
        for entry in m.get("outputs", []):
            if entry.get("role") != "preview_image":
                continue
            for f in entry.get("files", []):
                p = m["_dir"] / f["path"]
                if p.exists():
                    previews[m["plan"]][m["code"]["short"]].append(p)
    return dict(previews)


def read_profile(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    x, y = data[:, 0], data[:, 1]
    yerr = data[:, 2] if data.shape[1] >= 3 else None
    return x, y, yerr


def read_scalar(path: Path) -> tuple[float, float | None]:
    data = np.loadtxt(path, comments="#")
    if data.ndim == 0:
        return float(data), None
    row = data if data.ndim == 1 else data[0]
    if row.size >= 5:
        value, rel_err = float(row[3]), float(row[4])
        return value, abs(value * rel_err)
    elif row.size == 4:
        return float(row[3]), None
    elif row.size >= 2:
        value, rel_err = float(row[0]), float(row[1])
        return value, abs(value * rel_err)
    return float(row[0]), None


# ---------------------------------------------------------------------------
# Axes-level drawing helpers
# ---------------------------------------------------------------------------

def _axis_label(meta: dict, axis: str) -> str:
    a = meta.get(axis, {})
    unit = a.get("unit", "")
    quant = a.get("quantity", axis)
    return f"{quant} [{unit}]" if unit else quant


def centers_to_edges(x: np.ndarray, *, log_spacing: bool) -> np.ndarray:
    """Infer bin edges from bin centers for stair rendering."""
    if x.size == 1:
        half_width = x[0] * 0.5 if log_spacing and x[0] > 0 else 0.5
        return np.array([x[0] - half_width, x[0] + half_width])

    if log_spacing and np.all(x > 0):
        edges = np.empty(x.size + 1, dtype=float)
        edges[1:-1] = np.sqrt(x[:-1] * x[1:])
        edges[0] = x[0] ** 2 / edges[1]
        edges[-1] = x[-1] ** 2 / edges[-2]
        return edges

    midpoints = (x[:-1] + x[1:]) / 2.0
    edges = np.empty(x.size + 1, dtype=float)
    edges[1:-1] = midpoints
    edges[0] = x[0] - (midpoints[0] - x[0])
    edges[-1] = x[-1] + (x[-1] - midpoints[-1])
    return edges


def stairs_xy(x: np.ndarray, y: np.ndarray, *, log_spacing: bool) -> tuple[np.ndarray, np.ndarray]:
    edges = centers_to_edges(x, log_spacing=log_spacing)
    return np.repeat(edges, 2)[1:-1], np.repeat(y, 2)


def draw_profile(ax: plt.Axes, traces: list[dict], code_styles: dict,
                 meta: dict, is_spectrum: bool) -> None:
    is_depth_fluence = (
        meta.get("geometry") == "depth_Z"
        and meta.get("quantity") == "FLUENCE"
    )
    log_y = is_spectrum or is_depth_fluence

    for t in traces:
        style = code_styles.get(t["code_short"], {})
        color = style.get("display_color", "#888888")
        name  = style.get("name", t["code_short"])
        try:
            x, y, yerr = read_profile(t["path"])
        except Exception as exc:
            print(f"  WARNING: cannot read {t['path']}: {exc}")
            continue

        if is_spectrum:
            positive_x = x > 0
            x = x[positive_x]
            y = y[positive_x]
            if yerr is not None:
                yerr = yerr[positive_x]
            if x.size == 0:
                print(f"  WARNING: cannot plot {t['path']}: no positive bins for log-log spectrum")
                continue

        if log_y:
            positive_y = y > 0
            if not np.any(positive_y):
                print(f"  WARNING: cannot plot {t['path']}: no positive y values for log-y plot")
                continue
            y = np.where(positive_y, y, np.nan)
            if yerr is not None:
                yerr = np.where(positive_y, yerr, np.nan)

        x_plot, y_plot = stairs_xy(x, y, log_spacing=is_spectrum)
        yerr_plot = np.repeat(yerr, 2) if yerr is not None else None

        kw: dict = dict(color=color, label=name, linewidth=1.2)
        ax.plot(x_plot, y_plot, **kw)
        if yerr_plot is not None and not is_spectrum:
            ax.fill_between(x_plot, y_plot - yerr_plot, y_plot + yerr_plot,
                            alpha=0.15, color=color)
    ax.set_xlabel(_axis_label(meta, "axis_x"), fontsize=8)
    ax.set_ylabel(_axis_label(meta, "axis_y"), fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3)
    if is_spectrum:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    ax.legend(fontsize=7, loc="best")


def draw_scalar(ax: plt.Axes, traces: list[dict], code_styles: dict, meta: dict) -> None:
    names, values, errors, colors = [], [], [], []
    for t in traces:
        style = code_styles.get(t["code_short"], {})
        try:
            val, err = read_scalar(t["path"])
        except Exception as exc:
            print(f"  WARNING: cannot read {t['path']}: {exc}")
            continue
        names.append(style.get("name", t["code_short"]))
        values.append(val)
        errors.append(err if err is not None else 0.0)
        colors.append(style.get("display_color", "#888888"))
    if not values:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    y_pos = list(range(len(names)))
    ax.barh(y_pos, values, xerr=errors if any(errors) else None,
            color=colors, height=0.5, error_kw={"linewidth": 0.8, "capsize": 3})
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel(_axis_label(meta, "axis_y"), fontsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(True, axis="x", alpha=0.3)


# ---------------------------------------------------------------------------
# Per-plan PDF generation
# ---------------------------------------------------------------------------

def _plan_header_page(pdf: PdfPages, plan: str, codes: set[str],
                      code_styles: dict, generated_at: str) -> None:
    fig = plt.figure(figsize=PAGE_SIZE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#f7f7f7")
    ax.axis("off")
    ax.text(0.5, 0.62, plan, fontsize=18, fontweight="bold",
            ha="center", transform=ax.transAxes)
    code_names = [code_styles.get(c, {}).get("name", c) for c in sorted(codes)]
    ax.text(0.5, 0.47, f"Codes:  {',  '.join(code_names)}",
            fontsize=11, ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.30, generated_at, fontsize=9, color="#999",
            ha="center", transform=ax.transAxes)
    pdf.savefig(fig)
    plt.close(fig)


def generate_plan_pdf(
    plan: str,
    by_geom: dict[str, list[str]],
    plan_index: dict[str, list[dict]],
    plan_previews: dict[str, list[Path]],
    catalog: dict,
    code_styles: dict,
    generated_at: str,
    out_path: Path,
) -> int:
    """
    Generate one plan PDF.  Returns the number of plot pages written.
    Uses a temp file then post-processes with pypdf to add outline bookmarks.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect codes present in this plan
    codes: set[str] = set()
    for traces in plan_index.values():
        for t in traces:
            codes.add(t["code_short"])

    section_pages: list[tuple[str, int]] = []  # (title, 0-indexed page number)
    page = 0
    total_plots = 0

    fd, tmp_path_str = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    tmp_path = Path(tmp_path_str)

    try:
        with PdfPages(tmp_path) as pdf:
            _plan_header_page(pdf, plan, codes, code_styles, generated_at)
            page += 1

            for geom_class, section_title in GEOMETRY_SECTIONS:
                ots = by_geom.get(geom_class, [])
                if not ots:
                    continue

                section_start = page

                if geom_class in ("map_XZ", "map_XY"):
                    imgs: list[tuple[str, Path]] = []
                    for code_short, paths in sorted(plan_previews.items()):
                        for p in paths:
                            if (geom_class == "map_XZ") == ("XZ" in p.name):
                                imgs.append((code_short, p))
                                break
                    if not imgs:
                        continue
                    n = len(imgs)
                    fig, axes = plt.subplots(1, n, figsize=PAGE_SIZE, squeeze=False)
                    fig.suptitle(section_title, fontsize=10, fontweight="bold")
                    for ax, (cs, img_path) in zip(axes[0], imgs):
                        try:
                            ax.imshow(plt.imread(str(img_path)))
                            ax.axis("off")
                            ax.set_title(code_styles.get(cs, {}).get("name", cs), fontsize=8)
                        except Exception as exc:
                            print(f"  WARNING: {img_path}: {exc}")
                            ax.axis("off")
                    plt.tight_layout(rect=[0, 0, 1, 0.93])
                    pdf.savefig(fig)
                    plt.close(fig)
                    page += 1
                    total_plots += 1

                else:
                    for ot in ots:
                        traces = plan_index.get(ot, [])
                        if not traces:
                            continue
                        meta = catalog.get(ot, {})
                        fig, ax = plt.subplots(figsize=PAGE_SIZE)
                        fig.suptitle(
                            f"{section_title}  —  {meta.get('label', ot)}",
                            fontsize=10, fontweight="bold",
                        )
                        try:
                            if geom_class == "target":
                                draw_scalar(ax, traces, code_styles, meta)
                            else:
                                draw_profile(ax, traces, code_styles, meta,
                                             is_spectrum=(geom_class == "spectrum_target"))
                        except Exception as exc:
                            print(f"  WARNING {plan}/{ot}: {exc}")
                            ax.text(0.5, 0.5, f"Error: {exc}", ha="center",
                                    va="center", transform=ax.transAxes,
                                    color="red", fontsize=8)
                        plt.tight_layout(rect=[0, 0, 1, 0.93])
                        pdf.savefig(fig)
                        plt.close(fig)
                        page += 1
                        total_plots += 1

                section_pages.append((section_title, section_start))

        # Post-process: add PDF outline (sidebar bookmarks) with pypdf
        reader = PdfReader(str(tmp_path))
        writer = PdfWriter()
        writer.append(reader)
        for title, pg in section_pages:
            writer.add_outline_item(title, pg)
        with open(str(out_path), "wb") as fh:
            writer.write(fh)

    finally:
        tmp_path.unlink(missing_ok=True)

    return total_plots


# ---------------------------------------------------------------------------
# Worker (top-level so ProcessPoolExecutor can pickle it)
# ---------------------------------------------------------------------------

def _worker(args: tuple) -> tuple[str, int]:
    (plan, by_geom, plan_index, plan_previews,
     catalog, code_styles, generated_at, out_path) = args
    n = generate_plan_pdf(plan, by_geom, plan_index, plan_previews,
                          catalog, code_styles, generated_at, out_path)
    return plan, n


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate(data_root: Path, catalog_path: Path, out_dir: Path) -> int:
    """Generate one PDF per plan in parallel. Returns 0 on success."""
    catalog    = load_catalog(catalog_path)
    code_styles = load_code_styles(data_root)
    manifests  = load_manifests(data_root)
    index      = build_index(manifests)
    previews   = collect_preview_images(manifests)

    # Organise by plan
    plans_ots: dict[str, set[str]] = defaultdict(set)
    for (plan, ot) in index:
        plans_ots[plan].add(ot)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out_dir.mkdir(parents=True, exist_ok=True)

    worker_args = []
    for plan in sorted(plans_ots):
        by_geom: dict[str, list[str]] = defaultdict(list)
        for ot in plans_ots[plan]:
            geom = catalog.get(ot, {}).get("geometry", ot.split(".")[0])
            by_geom[geom].append(ot)
        by_geom = {g: sorted(v) for g, v in by_geom.items()}

        plan_index   = {ot: index[(plan, ot)] for ot in plans_ots[plan]
                        if (plan, ot) in index}
        plan_previews = previews.get(plan, {})
        out_path      = out_dir / f"{plan}.pdf"

        worker_args.append((
            plan, by_geom, plan_index, plan_previews,
            catalog, code_styles, generated_at, out_path,
        ))

    workers = min(len(worker_args), os.cpu_count() or 4)
    print(f"Generating {len(worker_args)} plan PDFs "
          f"({workers} parallel workers)...")

    errors = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_worker, a): a[0] for a in worker_args}
        for fut in as_completed(futures):
            plan = futures[fut]
            try:
                _, n_plots = fut.result()
                print(f"  done  {plan}  ({n_plots} pages)")
            except Exception as exc:
                print(f"  ERROR {plan}: {exc}")
                errors += 1

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-root", type=Path, default=Path("data"))
    p.add_argument("--catalog",   type=Path, default=Path("data/output_catalog.json"))
    p.add_argument("--out-dir",   type=Path, default=Path("pages-site/plans"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    return generate(args.data_root, args.catalog, args.out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
