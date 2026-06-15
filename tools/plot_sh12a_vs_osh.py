#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plot SH12A vs OpenShieldHit for all matching .dat files in their results trees."
        )
    )
    parser.add_argument(
        "--sh12a-root",
        type=Path,
        default=Path("data/sh12a/results"),
        help="Root folder with SH12A result .dat files.",
    )
    parser.add_argument(
        "--osh-root",
        type=Path,
        default=Path("data/openshieldhit/results"),
        help="Root folder with OpenShieldHit result .dat files.",
    )
    parser.add_argument(
        "--sh12a-input-root",
        type=Path,
        default=Path("data/sh12a/input"),
        help="Root folder with SH12A input decks (used for title hints).",
    )
    parser.add_argument(
        "--osh-input-root",
        type=Path,
        default=Path("data/openshieldhit/input"),
        help="Root folder with OpenShieldHit input decks (used for title hints).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/comparisons/sh12a_vs_osh"),
        help="Directory where generated comparison plots are stored.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=140,
        help="Figure DPI for output PNG files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional cap on number of file pairs to plot (0 = all).",
    )
    return parser.parse_args()


def collect_dat_files(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*.dat"))
        if path.is_file()
    }


def load_xy(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.genfromtxt(path, comments="#", invalid_raise=False)
    if data.size == 0:
        raise ValueError("file has no numeric data")

    if data.ndim == 1:
        x = np.arange(data.shape[0], dtype=float)
        y = data.astype(float)
        return x, y

    if data.ndim != 2:
        raise ValueError(f"unsupported array dimension: {data.ndim}")

    if data.shape[1] == 1:
        y = data[:, 0].astype(float)
        x = np.arange(y.shape[0], dtype=float)
        return x, y

    x = data[:, 0].astype(float)
    y = data[:, 1].astype(float)
    finite_mask = np.isfinite(x) & np.isfinite(y)
    x = x[finite_mask]
    y = y[finite_mask]
    if x.size == 0:
        raise ValueError("no finite x/y samples")
    return x, y


def normalize_metric_name(filename: str) -> str:
    base = re.sub(r"\.dat$", "", filename, flags=re.IGNORECASE)
    base = re.sub(r"_p\d+$", "", base)
    base = re.sub(r"^NB_", "", base)
    return base.replace("_", " ")


def plan_input_hint(plan: str, sh12a_input_root: Path, osh_input_root: Path) -> str:
    for base in (sh12a_input_root / plan, osh_input_root / plan):
        if not base.exists():
            continue

        sobp_files = sorted(base.glob("sobp*.dat"))
        if sobp_files:
            return sobp_files[0].stem

        beam_file = base / "beam.dat"
        if beam_file.exists():
            return beam_file.stem

        detect_file = base / "detect.dat"
        if detect_file.exists():
            return detect_file.stem

    return ""


def make_plot(
    rel_path: Path,
    sh12a_file: Path,
    osh_file: Path,
    out_file: Path,
    sh12a_input_root: Path,
    osh_input_root: Path,
    dpi: int,
) -> None:
    x_sh, y_sh = load_xy(sh12a_file)
    x_osh, y_osh = load_xy(osh_file)

    plan = rel_path.parts[0] if rel_path.parts else "unknown_plan"
    metric = normalize_metric_name(rel_path.name)
    hint = plan_input_hint(plan, sh12a_input_root, osh_input_root)

    title_parts = [plan, metric]
    if hint:
        title_parts.append(f"input: {hint}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x_sh, y_sh, lw=1.8, label="SH12A")
    ax.plot(x_osh, y_osh, lw=1.5, ls="--", label="OpenShieldHit")
    ax.set_title(" | ".join(title_parts))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.35)
    ax.legend()

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_file, dpi=dpi)
    plt.close(fig)


def main() -> int:
    args = parse_args()

    sh12a_map = collect_dat_files(args.sh12a_root)
    osh_map = collect_dat_files(args.osh_root)

    shared_keys = sorted(set(sh12a_map).intersection(osh_map))
    if args.limit > 0:
        shared_keys = shared_keys[: args.limit]

    if not shared_keys:
        print("No shared .dat files found between roots.")
        return 1

    print(f"Found {len(shared_keys)} shared .dat file pairs.")

    made = 0
    skipped = 0
    for rel_path in shared_keys:
        out_file = (args.out_dir / rel_path).with_suffix(".png")
        try:
            make_plot(
                rel_path,
                sh12a_map[rel_path],
                osh_map[rel_path],
                out_file,
                args.sh12a_input_root,
                args.osh_input_root,
                args.dpi,
            )
            made += 1
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            print(f"[skip] {rel_path}: {exc}")

    print(f"Done. Wrote {made} plot(s) to: {args.out_dir}")
    if skipped:
        print(f"Skipped {skipped} pair(s) due to parse/plot errors.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
