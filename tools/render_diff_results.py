#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from plot_sh12a_vs_osh import (
    centers_to_edges,
    format_page_title,
    humanize_geo_label,
    infer_x_label,
    infer_y_label,
    is_diff_plot,
    load_xy,
    lookup_output_metadata,
    plan_input_hint,
)
import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render differential OpenShieldHit result .dat files as binned stair PNG plots."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="Plan results directory containing .dat/.png files.",
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        required=True,
        help="OpenShieldHit input root, e.g. data/openshieldhit/input.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=140,
        help="Figure DPI for overwritten PNG output.",
    )
    return parser.parse_args()


def render_diff_plot(
    dat_path: Path,
    rel_path: Path,
    input_root: Path,
    dpi: int,
) -> bool:
    output_meta, page_index = lookup_output_metadata(rel_path, input_root, input_root)
    page_meta = output_meta.pages[page_index] if output_meta else None
    if not is_diff_plot(rel_path, page_meta):
        return False

    x, y = load_xy(dat_path)
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    if x.size == 0:
        raise ValueError(f"no finite samples in {dat_path}")

    edges = centers_to_edges(x)
    plan = rel_path.parts[0] if rel_path.parts else dat_path.parent.name
    geo_label = humanize_geo_label(output_meta.geo) if output_meta else None
    block_label = output_meta.name if output_meta else dat_path.stem
    page_label = f"page {page_index + 1}" if output_meta and len(output_meta.pages) > 1 else None
    hint = plan_input_hint(plan, input_root, input_root)

    title_top_parts = [plan]
    if geo_label:
        title_top_parts.append(geo_label)
    if block_label:
        title_top_parts.append(block_label)
    if page_label:
        title_top_parts.append(page_label)

    title_bottom_parts = [format_page_title(page_meta)] if page_meta else [dat_path.stem]
    if hint:
        title_bottom_parts.append(f"input: {hint}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.stairs(y, edges, lw=1.8, color="C0", baseline=None)
    ax.set_title(" | ".join(title_top_parts) + "\n" + " | ".join(title_bottom_parts))
    ax.set_xlabel(infer_x_label(rel_path, page_meta))
    ax.set_ylabel(infer_y_label(page_meta))
    ax.grid(True, alpha=0.35)

    png_path = dat_path.with_suffix(".png")
    fig.tight_layout()
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)
    return True


def main() -> int:
    args = parse_args()

    results_dir = args.results_dir.resolve()
    plan = results_dir.name
    rendered = 0

    for dat_path in sorted(results_dir.glob("*.dat")):
        rel_path = Path(plan) / dat_path.name
        try:
            if render_diff_plot(dat_path, rel_path, args.input_root.resolve(), args.dpi):
                rendered += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {dat_path.name}: {exc}")

    print(f"Rendered {rendered} differential stair plot(s) in: {results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
