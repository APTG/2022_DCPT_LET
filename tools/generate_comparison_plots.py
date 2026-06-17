#!/usr/bin/env python3
"""Generate interactive Plotly HTML comparison plots from per-plan manifests.

For every (plan, output_type) group that has data from at least --min-codes
MC codes, reads the corresponding .dat/.txt data files and writes a
self-contained interactive HTML file.

Opening the HTML in any browser gives a fully interactive plot:
  - hover  → shows exact values for all codes at that x position
  - click legend  → toggles a code on/off
  - drag  → zoom;  double-click  → reset view
  - toolbar  → download as SVG

Output layout:
    {out_dir}/{plan}/{output_type}.html

Usage:
    python tools/generate_comparison_plots.py
    python tools/generate_comparison_plots.py --out-dir _pages/plots/ --min-codes 2
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
import yaml


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------


def load_catalog(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))["output_types"]


def load_code_styles(data_root: Path) -> dict[str, dict]:
    """Read all data/*/code.yaml files, keyed by code short name."""
    styles: dict[str, dict] = {}
    for yaml_path in sorted(data_root.glob("*/code.yaml")):
        info = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        styles[info["short"]] = info
    return styles


def collect_manifests(data_root: Path) -> list[dict]:
    entries: list[dict] = []
    for p in sorted(data_root.rglob("manifest.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        data["_dir"] = p.parent
        entries.append(data)
    return entries


def build_index(
    manifests: list[dict],
) -> dict[tuple[str, str], list[dict]]:
    """
    Returns {(plan, output_type): [{code_short, path, role}, ...]}.
    Only includes primary_data and derived entries that carry an output_type.
    Multiple files from the same code with the same output_type are all kept
    (e.g. the two equivalent NB_target_diff_p1 / _p3 pages in sh12a).
    """
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for m in manifests:
        plan = m["plan"]
        code_short = m["code"]["short"]
        result_dir = m["_dir"]
        for entry in m.get("outputs", []):
            role = entry.get("role", "")
            if role not in ("primary_data", "derived"):
                continue
            for f in entry.get("files", []):
                output_type = f.get("output_type")
                if not output_type:
                    continue
                index[(plan, output_type)].append(
                    {"code_short": code_short, "path": result_dir / f["path"], "role": role}
                )
    return dict(index)


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------


def read_profile(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """
    Read a 2- or 3-column ASCII profile (comments start with #).
    Returns (x, y, yerr) where yerr is None if absent.
    The error column is assumed to be absolute.
    """
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    x, y = data[:, 0], data[:, 1]
    yerr = data[:, 2] if data.shape[1] >= 3 else None
    return x, y, yerr


def read_scalar(path: Path) -> tuple[float, float | None]:
    """
    Read a single-voxel scalar output file. Returns (value, abs_error or None).

    Two known formats:
      SH12A .txt  – 5 cols (x y z value rel_error) with # header lines
      MCNP  .dat  – 2 cols (value rel_error), no header
    The relative error is converted to absolute.
    """
    data = np.loadtxt(path, comments="#")
    if data.ndim == 0:
        return float(data), None
    row = data if data.ndim == 1 else data[0]
    if row.size >= 5:
        value, rel_err = float(row[3]), float(row[4])
    elif row.size >= 2:
        value, rel_err = float(row[0]), float(row[1])
    else:
        return float(row[0]), None
    return value, abs(value * rel_err)


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------

_DASH_STYLES = ["solid", "dash", "dot", "dashdot", "longdash"]


def _axis_label(meta: dict, axis: str) -> str:
    a = meta.get(axis, {})
    unit = a.get("unit", "")
    quant = a.get("quantity", axis)
    return f"{quant} [{unit}]" if unit else quant


def make_profile_figure(
    meta: dict,
    traces: list[dict],
    code_styles: dict[str, dict],
) -> go.Figure:
    """
    One Scatter trace per file.  Files from the same code share a legend group
    and colour but use different line dashes.  If a code has only one file, only
    that one appears in the legend; additional files are shown with dashed lines
    and get their own legend entry using a shorter label.
    """
    # Group files by code, preserving insertion order
    by_code: dict[str, list[Path]] = defaultdict(list)
    seen: set[Path] = set()  # deduplicate identical paths (e.g. p1 == p3 in sh12a)
    for t in traces:
        p = t["path"]
        if p not in seen:
            by_code[t["code_short"]].append(p)
            seen.add(p)

    is_spectrum = meta.get("geometry") == "spectrum_target"
    fig = go.Figure()

    for code_short, paths in by_code.items():
        style = code_styles.get(code_short, {})
        color = style.get("display_color", "#888888")
        code_name = style.get("name", code_short)

        for file_idx, path in enumerate(paths):
            try:
                x, y, yerr = read_profile(path)
            except Exception as exc:
                print(f"  WARNING: cannot read {path}: {exc}")
                continue

            if len(paths) == 1:
                name = code_name
                show_legend = True
            else:
                # Multiple files from same code: show all in legend
                name = f"{code_name} · {path.stem}"
                show_legend = True

            kw: dict[str, Any] = {
                "x": x,
                "y": y,
                "mode": "lines",
                "name": name,
                "legendgroup": code_short,
                "showlegend": show_legend,
                "line": {
                    "color": color,
                    "dash": _DASH_STYLES[file_idx % len(_DASH_STYLES)],
                    "width": 1.5,
                },
                "hovertemplate": (
                    f"<b>{name}</b><br>"
                    "x=%{x:.4g}<br>y=%{y:.4g}<extra></extra>"
                ),
            }
            if yerr is not None:
                kw["error_y"] = {
                    "type": "data",
                    "array": yerr,
                    "visible": True,
                    "color": color,
                    "thickness": 0.8,
                    "width": 0,
                }
            fig.add_scatter(**kw)

    xlab = _axis_label(meta, "axis_x")
    ylab = _axis_label(meta, "axis_y")

    fig.update_layout(
        xaxis_title=xlab,
        yaxis_title=ylab,
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        margin={"l": 70, "r": 20, "t": 80, "b": 60},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e0e0e0", zeroline=False,
                     type="log" if is_spectrum else "linear")
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", zeroline=False,
                     type="log" if is_spectrum else "linear")
    return fig


def make_scalar_figure(
    meta: dict,
    traces: list[dict],
    code_styles: dict[str, dict],
) -> go.Figure:
    """Grouped bar chart with one bar per file, coloured by code."""
    names, values, errors, colors = [], [], [], []
    for t in traces:
        style = code_styles.get(t["code_short"], {})
        color = style.get("display_color", "#888888")
        code_name = style.get("name", t["code_short"])
        try:
            value, abs_err = read_scalar(t["path"])
        except Exception as exc:
            print(f"  WARNING: cannot read {t['path']}: {exc}")
            continue
        names.append(f"{code_name}<br><sub>{t['path'].name}</sub>")
        values.append(value)
        errors.append(abs_err if abs_err is not None else 0.0)
        colors.append(color)

    fig = go.Figure(go.Bar(
        x=names,
        y=values,
        error_y={"type": "data", "array": errors, "visible": any(e > 0 for e in errors)},
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>value=%{y:.4g}<extra></extra>",
    ))
    ylab = _axis_label(meta, "axis_y") or meta.get("quantity", "value")
    fig.update_layout(
        xaxis_title="MC code",
        yaxis_title=ylab,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin={"l": 70, "r": 20, "t": 80, "b": 120},
    )
    fig.update_yaxes(showgrid=True, gridcolor="#e0e0e0", zeroline=True, zerolinecolor="#ccc")
    return fig


# ---------------------------------------------------------------------------
# HTML wrapper
# ---------------------------------------------------------------------------


def to_html(fig: go.Figure, title: str) -> str:
    """Embed the figure in a minimal standalone HTML page (Plotly.js from CDN)."""
    plot_div = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={
            "responsive": True,
            "displaylogo": False,
            "toImageButtonOptions": {"format": "svg", "filename": title},
        },
    )
    safe_title = title.replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    body  {{ margin: 0; font-family: "Segoe UI", Arial, sans-serif; background: #f6f4ef; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 1rem 1rem 2rem; }}
    h2    {{ margin: 0 0 0.8rem; font-size: 1.1rem; color: #1b2226; }}
    .plotly-graph-div {{ height: 520px; width: 100%; }}
  </style>
</head>
<body>
<div class="wrap">
  <h2>{safe_title}</h2>
  {plot_div}
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root", type=Path, default=Path("data"),
        help="Root directory containing code.yaml files and manifest.json files (default: data).",
    )
    parser.add_argument(
        "--catalog", type=Path, default=Path("data/output_catalog.json"),
        help="Path to output_catalog.json (default: data/output_catalog.json).",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("_pages/plots"),
        help="Output directory for generated HTML files (default: _pages/plots).",
    )
    parser.add_argument(
        "--min-codes", type=int, default=1,
        help="Minimum number of distinct codes required to generate a plot (default: 1).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    catalog = load_catalog(args.catalog)
    code_styles = load_code_styles(args.data_root)
    manifests = collect_manifests(args.data_root)
    index = build_index(manifests)

    print(
        f"Catalog: {len(catalog)} output types  |  "
        f"Codes: {len(code_styles)}  |  "
        f"Manifests: {len(manifests)}  |  "
        f"Groups: {len(index)} (plan × output_type)"
    )

    n_written = n_skipped = n_errors = 0
    for (plan, output_type), traces in sorted(index.items()):
        n_codes = len({t["code_short"] for t in traces})
        if n_codes < args.min_codes:
            n_skipped += 1
            continue

        meta = catalog.get(output_type, {})
        geometry = meta.get("geometry", output_type.split(".")[0])
        label = meta.get("label", output_type)
        title = f"{label} — {plan}"
        out_path = args.out_dir / plan / f"{output_type}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if geometry in ("depth_Z", "spectrum_target"):
                fig = make_profile_figure(meta, traces, code_styles)
            elif geometry == "target":
                fig = make_scalar_figure(meta, traces, code_styles)
            else:
                # map_XZ / map_XY – skip until heatmap support is added
                print(f"  skip  {plan}/{output_type}  (geometry '{geometry}' not yet rendered)")
                n_skipped += 1
                continue
        except Exception as exc:
            print(f"  ERROR {plan}/{output_type}: {exc}")
            n_errors += 1
            continue

        fig.update_layout(title={"text": title, "font": {"size": 13}, "x": 0, "xanchor": "left"})
        out_path.write_text(to_html(fig, title), encoding="utf-8")
        code_list = ", ".join(sorted({t["code_short"] for t in traces}))
        print(f"  wrote {out_path.relative_to(args.out_dir)}  [{code_list}]")
        n_written += 1

    print(f"\nDone: {n_written} plots written, {n_skipped} skipped, {n_errors} errors.")
    return 1 if n_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
