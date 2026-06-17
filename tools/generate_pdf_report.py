#!/usr/bin/env python3
"""Generate a multi-page PDF report of all MC comparison plots.

One matplotlib figure per (plan, output_type), organised by plan then
geometry section. 2D map sections show PNG previews side-by-side.

Usage:
    python tools/generate_pdf_report.py
    python tools/generate_pdf_report.py --out pages-site/report.pdf
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import yaml


PAGE_SIZE = (11.69, 8.27)   # A4 landscape, inches

GEOMETRY_SECTIONS = [
    ("depth_Z",         "Depth profiles"),
    ("spectrum_target", "LET / dE/dx spectra"),
    ("target",          "Target volume scalars"),
    ("map_XZ",          "2D longitudinal maps (XZ)"),
    ("map_XY",          "2D transverse maps (XY)"),
]


# ---------------------------------------------------------------------------
# Data loading  (mirrors generate_comparison_plots.py)
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
    """First file per (plan, output_type, code) only — same deduplication as plot generator."""
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
# Axes-level figure builders
# ---------------------------------------------------------------------------

def _axis_label(meta: dict, axis: str) -> str:
    a = meta.get(axis, {})
    unit = a.get("unit", "")
    quant = a.get("quantity", axis)
    return f"{quant} [{unit}]" if unit else quant


def draw_profile(ax: plt.Axes, traces: list[dict], code_styles: dict, meta: dict, is_spectrum: bool) -> None:
    for t in traces:
        style = code_styles.get(t["code_short"], {})
        color = style.get("display_color", "#888888")
        name = style.get("name", t["code_short"])
        try:
            x, y, yerr = read_profile(t["path"])
        except Exception as exc:
            print(f"  WARNING: cannot read {t['path']}: {exc}")
            continue
        kw: dict = dict(color=color, label=name, linewidth=1.2)
        if is_spectrum:
            kw["drawstyle"] = "steps-post"
        ax.plot(x, y, **kw)
        if yerr is not None and not is_spectrum:
            ax.fill_between(x, y - yerr, y + yerr, alpha=0.15, color=color)

    ax.set_xlabel(_axis_label(meta, "axis_x"), fontsize=8)
    ax.set_ylabel(_axis_label(meta, "axis_y"), fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3)
    if is_spectrum:
        ax.set_xscale("log")
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
# Page-count pre-calculation (needed for TOC)
# ---------------------------------------------------------------------------

def count_plan_pages(
    plan: str,
    by_geom: dict[str, list[str]],
    preview_images: dict[str, dict[str, list[Path]]],
) -> int:
    """Return the number of plot/image pages a plan will produce (excluding its header page)."""
    n = 0
    plan_prev = preview_images.get(plan, {})
    for geom_class, _ in GEOMETRY_SECTIONS:
        ots = by_geom.get(geom_class, [])
        if not ots:
            continue
        if geom_class in ("map_XZ", "map_XY"):
            has_img = any(
                any((geom_class == "map_XZ") == ("XZ" in p.name) for p in paths)
                for paths in plan_prev.values()
            )
            if has_img:
                n += 1
        else:
            n += len(ots)
    return n


def build_page_map(
    plans: list[str],
    plans_by_geom: dict[str, dict[str, list[str]]],
    preview_images: dict[str, dict[str, list[Path]]],
) -> dict[str, int]:
    """
    Return {plan: first_page_number} where page 1 = cover, page 2 = TOC.
    Each plan occupies 1 header page + count_plan_pages() plot pages.
    """
    page = 3  # cover=1, toc=2
    plan_start: dict[str, int] = {}
    for plan in plans:
        plan_start[plan] = page
        page += 1 + count_plan_pages(plan, plans_by_geom[plan], preview_images)
    return plan_start


# ---------------------------------------------------------------------------
# Cover / TOC / section header pages
# ---------------------------------------------------------------------------

def write_report_cover(pdf: PdfPages, plans: list[str], code_styles: dict, generated_at: str) -> None:
    fig = plt.figure(figsize=PAGE_SIZE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.axis("off")

    ax.text(0.5, 0.80, "DCPT LET-measurements 2022",
            fontsize=24, fontweight="bold", ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.70, "MC Code Comparison Report",
            fontsize=16, color="#555", ha="center", transform=ax.transAxes)

    code_names = [s.get("name", k) for k, s in sorted(code_styles.items())]
    ax.text(0.5, 0.55, f"Codes:  {',  '.join(code_names)}",
            fontsize=11, ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.47, f"{len(plans)} plans",
            fontsize=11, ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.32, generated_at,
            fontsize=9, color="#999", ha="center", transform=ax.transAxes)

    pdf.savefig(fig)
    plt.close(fig)


def write_toc(
    pdf: PdfPages,
    plans: list[str],
    plan_start: dict[str, int],
    plans_by_geom: dict[str, dict[str, list[str]]],
    preview_images: dict[str, dict[str, list[Path]]],
) -> None:
    fig = plt.figure(figsize=PAGE_SIZE)
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.axis("off")

    fig.text(0.5, 0.96, "Table of Contents", fontsize=14, fontweight="bold",
             ha="center", va="top")

    col_x_plan = 0.0
    col_x_n    = 0.72
    col_x_page = 0.88

    # Header row
    ax.text(col_x_plan, 1.0, "Plan", fontsize=8, fontweight="bold", va="top", transform=ax.transAxes)
    ax.text(col_x_n,    1.0, "Plots", fontsize=8, fontweight="bold", va="top", ha="right", transform=ax.transAxes)
    ax.text(col_x_page, 1.0, "Page", fontsize=8, fontweight="bold", va="top", ha="right", transform=ax.transAxes)
    ax.axhline(0.985, color="#aaa", linewidth=0.5)

    row_h = 0.96 / max(len(plans), 1)
    for i, plan in enumerate(plans):
        y = 0.97 - (i + 1) * row_h
        n_plots = count_plan_pages(plan, plans_by_geom[plan], preview_images)
        page = plan_start[plan]
        bg = "#f5f5f5" if i % 2 == 0 else "white"
        ax.axhspan(y, y + row_h, color=bg, zorder=0)
        ax.text(col_x_plan, y + row_h * 0.35, plan, fontsize=8, va="bottom", transform=ax.transAxes)
        ax.text(col_x_n,    y + row_h * 0.35, str(n_plots), fontsize=8, va="bottom",
                ha="right", color="#555", transform=ax.transAxes)
        ax.text(col_x_page, y + row_h * 0.35, str(page), fontsize=8, va="bottom",
                ha="right", transform=ax.transAxes)

    pdf.savefig(fig)
    plt.close(fig)


def write_plan_header(pdf: PdfPages, plan: str, codes: set[str], code_styles: dict, n_plots: int) -> None:
    fig = plt.figure(figsize=PAGE_SIZE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#f7f7f7")
    ax.axis("off")

    ax.text(0.5, 0.62, plan,
            fontsize=20, fontweight="bold", ha="center", transform=ax.transAxes)
    code_names = [code_styles.get(c, {}).get("name", c) for c in sorted(codes)]
    ax.text(0.5, 0.48, f"Codes:  {',  '.join(code_names)}",
            fontsize=12, ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.38, f"{n_plots} output types",
            fontsize=10, color="#777", ha="center", transform=ax.transAxes)

    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-root", type=Path, default=Path("data"))
    p.add_argument("--catalog", type=Path, default=Path("data/output_catalog.json"))
    p.add_argument("--out", type=Path, default=Path("pages-site/report.pdf"))
    return p.parse_args()


def main() -> int:
    args = parse_args()

    catalog = load_catalog(args.catalog)
    code_styles = load_code_styles(args.data_root)
    manifests = load_manifests(args.data_root)
    index = build_index(manifests)
    preview_images = collect_preview_images(manifests)

    # Collect plans → output_types and plans → codes
    plans_ots: dict[str, set[str]] = defaultdict(set)
    plan_codes: dict[str, set[str]] = defaultdict(set)
    for (plan, ot), traces in index.items():
        plans_ots[plan].add(ot)
        for t in traces:
            plan_codes[plan].add(t["code_short"])

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    sorted_plans = sorted(plans_ots)

    # Pre-compute geometry groupings and page map for TOC
    plans_by_geom: dict[str, dict[str, list[str]]] = {}
    for plan in sorted_plans:
        by_geom: dict[str, list[str]] = defaultdict(list)
        for ot in plans_ots[plan]:
            geom = catalog.get(ot, {}).get("geometry", ot.split(".")[0])
            by_geom[geom].append(ot)
        plans_by_geom[plan] = {g: sorted(v) for g, v in by_geom.items()}

    plan_start = build_page_map(sorted_plans, plans_by_geom, preview_images)

    total_pages = 0
    with PdfPages(args.out) as pdf:
        d = pdf.infodict()
        d["Title"] = "DCPT LET-measurements 2022 — MC Comparison Report"
        d["Author"] = "APTG"
        d["CreationDate"] = datetime.now(timezone.utc)

        write_report_cover(pdf, sorted_plans, code_styles, generated_at)
        write_toc(pdf, sorted_plans, plan_start, plans_by_geom, preview_images)

        for plan in sorted_plans:
            by_geom = plans_by_geom[plan]
            n_plots = count_plan_pages(plan, by_geom, preview_images)
            write_plan_header(pdf, plan, plan_codes[plan], code_styles, n_plots)

            for geom_class, section_title in GEOMETRY_SECTIONS:
                ots = sorted(by_geom.get(geom_class, []))
                if not ots:
                    continue

                if geom_class in ("map_XZ", "map_XY"):
                    plan_prev = preview_images.get(plan, {})
                    # Collect the matching preview per code
                    imgs: list[tuple[str, Path]] = []
                    for code_short, paths in sorted(plan_prev.items()):
                        for p in paths:
                            if (geom_class == "map_XZ") == ("XZ" in p.name):
                                imgs.append((code_short, p))
                                break
                    if not imgs:
                        continue
                    n = len(imgs)
                    fig, axes = plt.subplots(1, n, figsize=PAGE_SIZE, squeeze=False)
                    fig.suptitle(f"{plan}  —  {section_title}", fontsize=10, fontweight="bold")
                    for ax, (code_short, img_path) in zip(axes[0], imgs):
                        try:
                            ax.imshow(plt.imread(str(img_path)))
                            ax.axis("off")
                            ax.set_title(code_styles.get(code_short, {}).get("name", code_short), fontsize=8)
                        except Exception as exc:
                            print(f"  WARNING: cannot load {img_path}: {exc}")
                            ax.axis("off")
                    plt.tight_layout(rect=[0, 0, 1, 0.93])
                    pdf.savefig(fig)
                    plt.close(fig)
                    total_pages += 1
                    print(f"  {plan}/{geom_class}  (preview images)")

                else:
                    for ot in ots:
                        traces = index.get((plan, ot), [])
                        if not traces:
                            continue
                        meta = catalog.get(ot, {})
                        label = meta.get("label", ot)

                        fig, ax = plt.subplots(figsize=PAGE_SIZE)
                        fig.suptitle(
                            f"{plan}  —  {section_title}\n{label}",
                            fontsize=10, fontweight="bold",
                        )
                        try:
                            if geom_class == "target":
                                draw_scalar(ax, traces, code_styles, meta)
                            else:
                                draw_profile(ax, traces, code_styles, meta,
                                             is_spectrum=(geom_class == "spectrum_target"))
                        except Exception as exc:
                            print(f"  WARNING: error rendering {plan}/{ot}: {exc}")
                            ax.text(0.5, 0.5, f"Error: {exc}", ha="center", va="center",
                                    transform=ax.transAxes, color="red", fontsize=8)

                        plt.tight_layout(rect=[0, 0, 1, 0.90])
                        pdf.savefig(fig)
                        plt.close(fig)
                        total_pages += 1
                        print(f"  {plan}/{ot}")

    print(f"\nPDF written to: {args.out}  ({total_pages} plot pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
