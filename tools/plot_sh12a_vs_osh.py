#!/usr/bin/env python3

from __future__ import annotations

import argparse
from contextlib import nullcontext
from dataclasses import dataclass
from functools import lru_cache
import os
import re
from pathlib import Path

_MATPLOTLIB_CACHE = Path(__file__).resolve().parent.parent / ".matplotlib"
_MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MATPLOTLIB_CACHE))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402


PAGE_RE = re.compile(r"^(?P<stem>.+?)_p(?P<page>\d+)$")
POSITION_FILE_HINTS = ("NB_Z_narrow",)
MEDIUM_LABELS = {
    "in_Si": "in Si",
    "in_Water": "in Water",
}
QUANTITY_LABELS = {
    "FLUENCE": "Fluence",
    "DOSE": "Dose",
    "DLET": "DLET",
    "TLET": "TLET",
    "DQEFF": "DQEFF",
    "TQEFF": "TQEFF",
}
QUANTITY_UNITS = {
    "FLUENCE": "1/cm^2/prim",
    "DOSE": "MeV/g/prim",
    "DLET": "MeV/cm",
    "TLET": "MeV/cm",
    "DQEFF": "dim.less",
    "TQEFF": "dim.less",
}
DIFF_TYPE_LABELS = {
    "DEDX": "DEDX",
    "LET": "LET",
}
DIFF_TYPE_UNITS = {
    "DEDX": "MeV/cm",
    "LET": "MeV/cm",
}


@dataclass(frozen=True)
class PageMetadata:
    quantity: str
    component: str | None = None
    medium: str | None = None
    diff1_type: str | None = None
    diff1_medium: str | None = None


@dataclass(frozen=True)
class OutputMetadata:
    name: str
    geo: str | None = None
    pages: tuple[PageMetadata, ...] = ()


def strip_inline_comment(line: str) -> str:
    return line.split("#", 1)[0].rstrip()


def normalize_name_token(token: str) -> str:
    return token.strip().replace("-", "").upper()


def humanize_medium(token: str | None) -> str | None:
    if not token:
        return None
    return MEDIUM_LABELS.get(token, token.replace("_", " "))


def format_quantity_label(page_meta: PageMetadata, include_unit: bool = True) -> str:
    quantity = QUANTITY_LABELS.get(page_meta.quantity, page_meta.quantity)
    parts = []
    if page_meta.component:
        parts.append(page_meta.component)
    parts.append(quantity)
    medium = humanize_medium(page_meta.medium or page_meta.diff1_medium)
    if medium:
        parts.append(medium)
    label = " ".join(parts)
    unit = QUANTITY_UNITS.get(page_meta.quantity)
    if include_unit and unit:
        return f"{label} [{unit}]"
    return label


def format_diff_label(page_meta: PageMetadata, include_unit: bool = True) -> str:
    if not page_meta.diff1_type:
        return "x"
    diff_type = DIFF_TYPE_LABELS.get(page_meta.diff1_type, page_meta.diff1_type)
    medium = humanize_medium(page_meta.diff1_medium)
    label = diff_type if not medium else f"{diff_type} {medium}"
    unit = DIFF_TYPE_UNITS.get(page_meta.diff1_type)
    if include_unit and unit:
        return f"{label} [{unit}]"
    return label


def humanize_geo_label(geo: str | None) -> str | None:
    if not geo:
        return None
    return geo.replace("_", " ")


def format_page_title(page_meta: PageMetadata) -> str:
    metric = format_quantity_label(page_meta, include_unit=False)
    if page_meta.diff1_type:
        return f"{metric} vs {format_diff_label(page_meta, include_unit=False)}"
    return metric


def is_diff_plot(rel_path: Path, page_meta: PageMetadata | None) -> bool:
    if page_meta and page_meta.diff1_type:
        return True
    return "_diff_" in f"_{rel_path.stem}_"


def infer_x_label(rel_path: Path, page_meta: PageMetadata | None) -> str:
    if page_meta and page_meta.diff1_type:
        return format_diff_label(page_meta)
    if any(rel_path.stem.startswith(prefix) for prefix in POSITION_FILE_HINTS):
        return "Position [cm]"
    return "x"


def infer_y_label(page_meta: PageMetadata | None) -> str:
    if page_meta:
        return format_quantity_label(page_meta)
    return "y"


def parse_quantity_line(line: str) -> PageMetadata:
    payload = strip_inline_comment(line).split(None, 1)[1]
    tokens = payload.split()
    quantity = normalize_name_token(tokens[0])
    component = None
    medium = None
    for token in tokens[1:]:
        if token in {"Primary", "Protons"}:
            component = token
        elif token in MEDIUM_LABELS:
            medium = token
    return PageMetadata(quantity=quantity, component=component, medium=medium)


def parse_diff1type_line(line: str, current_page: PageMetadata) -> PageMetadata:
    payload = strip_inline_comment(line).split(None, 1)[1]
    tokens = payload.split()
    diff1_type = normalize_name_token(tokens[0])
    diff1_medium = None
    for token in tokens[1:]:
        if token in MEDIUM_LABELS:
            diff1_medium = token
            break
    if diff1_medium is None:
        diff1_medium = current_page.medium
    return PageMetadata(
        quantity=current_page.quantity,
        component=current_page.component,
        medium=current_page.medium or diff1_medium,
        diff1_type=diff1_type,
        diff1_medium=diff1_medium,
    )


@lru_cache(maxsize=None)
def parse_detect_outputs(detect_path: Path) -> dict[str, OutputMetadata]:
    outputs: dict[str, OutputMetadata] = {}
    current_name: str | None = None
    current_pages: list[PageMetadata] | None = None
    current_geo: str | None = None

    for raw_line in detect_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "Output":
            current_name = None
            current_pages = None
            current_geo = None
            continue
        if line.startswith("Filename "):
            filename = strip_inline_comment(line).split(None, 1)[1]
            current_name = Path(filename).stem
            current_pages = []
            continue
        if line.startswith("Geo "):
            current_geo = strip_inline_comment(line).split(None, 1)[1]
            if current_name is not None and current_pages is not None:
                outputs[current_name] = OutputMetadata(
                    name=current_name,
                    geo=current_geo,
                    pages=tuple(current_pages),
                )
            continue
        if line.startswith("Quantity ") and current_pages is not None:
            current_pages.append(parse_quantity_line(line))
            if current_name is not None:
                outputs[current_name] = OutputMetadata(
                    name=current_name,
                    geo=current_geo,
                    pages=tuple(current_pages),
                )
            continue
        if line.startswith("Diff1Type ") and current_pages:
            current_pages[-1] = parse_diff1type_line(line, current_pages[-1])
            if current_name is not None:
                outputs[current_name] = OutputMetadata(
                    name=current_name,
                    geo=current_geo,
                    pages=tuple(current_pages),
                )

    return outputs


def lookup_output_metadata(
    rel_path: Path,
    sh12a_input_root: Path,
    osh_input_root: Path,
) -> tuple[OutputMetadata | None, int]:
    plan = rel_path.parts[0] if rel_path.parts else ""
    stem = rel_path.stem
    match = PAGE_RE.match(stem)
    if match:
        block_name = match.group("stem")
        page_index = int(match.group("page")) - 1
    else:
        block_name = stem
        page_index = 0

    for root in (osh_input_root, sh12a_input_root):
        detect_path = root / plan / "detect.dat"
        if not detect_path.exists():
            continue
        outputs = parse_detect_outputs(detect_path)
        output_meta = outputs.get(block_name)
        if output_meta and 0 <= page_index < len(output_meta.pages):
            return output_meta, page_index
    return None, page_index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Plot SH12A vs OpenShieldHit for all matching .dat files in their results trees.")
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
    parser.add_argument(
        "--pdf-report",
        type=Path,
        default=Path("data/comparisons/sh12a_vs_osh_report.pdf"),
        help="Output PDF report path. Use an empty string to disable PDF generation.",
    )
    return parser.parse_args()


def collect_dat_files(root: Path) -> dict[Path, Path]:
    return {path.relative_to(root): path for path in sorted(root.rglob("*.dat")) if path.is_file()}


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


def centers_to_edges(x: np.ndarray) -> np.ndarray:
    if x.ndim != 1 or x.size == 0:
        raise ValueError("x must be a non-empty 1D array")
    if x.size == 1:
        width = max(abs(x[0]) * 0.1, 1.0)
        return np.array([x[0] - width / 2.0, x[0] + width / 2.0], dtype=float)

    midpoints = 0.5 * (x[:-1] + x[1:])
    left_edge = x[0] - (midpoints[0] - x[0])
    right_edge = x[-1] + (x[-1] - midpoints[-1])
    edges = np.concatenate(([left_edge], midpoints, [right_edge])).astype(float)
    return edges


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
) -> Figure:
    x_sh, y_sh = load_xy(sh12a_file)
    x_osh, y_osh = load_xy(osh_file)
    output_meta, page_index = lookup_output_metadata(rel_path, sh12a_input_root, osh_input_root)
    page_meta = output_meta.pages[page_index] if output_meta else None

    plan = rel_path.parts[0] if rel_path.parts else "unknown_plan"
    if page_meta:
        metric = format_page_title(page_meta)
    else:
        metric = normalize_metric_name(rel_path.name)
    hint = plan_input_hint(plan, sh12a_input_root, osh_input_root)
    geo_label = humanize_geo_label(output_meta.geo) if output_meta else None
    block_label = output_meta.name if output_meta else PAGE_RE.sub(r"\g<stem>", rel_path.stem)
    page_label = f"page {page_index + 1}" if page_meta and output_meta and len(output_meta.pages) > 1 else None

    title_top_parts = [plan]
    if geo_label:
        title_top_parts.append(geo_label)
    if block_label:
        title_top_parts.append(block_label)
    if page_label:
        title_top_parts.append(page_label)

    title_bottom_parts = [metric]
    if hint:
        title_bottom_parts.append(f"input: {hint}")

    use_loglog = is_diff_plot(rel_path, page_meta)
    if use_loglog:
        sh_mask = np.isfinite(x_sh) & np.isfinite(y_sh) & (x_sh > 0) & (y_sh > 0)
        osh_mask = np.isfinite(x_osh) & np.isfinite(y_osh) & (x_osh > 0) & (y_osh > 0)
    else:
        sh_mask = np.isfinite(x_sh) & np.isfinite(y_sh)
        osh_mask = np.isfinite(x_osh) & np.isfinite(y_osh)

    x_sh_plot = x_sh[sh_mask]
    y_sh_plot = y_sh[sh_mask]
    x_osh_plot = x_osh[osh_mask]
    y_osh_plot = y_osh[osh_mask]

    if x_sh_plot.size == 0 or x_osh_plot.size == 0:
        raise ValueError("no plottable samples after filtering")

    fig, ax = plt.subplots(figsize=(9, 5))
    if use_loglog:
        sh_pos_mask = y_sh_plot > 0
        osh_pos_mask = y_osh_plot > 0
        x_sh_plot = x_sh_plot[sh_pos_mask]
        y_sh_plot = y_sh_plot[sh_pos_mask]
        x_osh_plot = x_osh_plot[osh_pos_mask]
        y_osh_plot = y_osh_plot[osh_pos_mask]
        if x_sh_plot.size == 0 or x_osh_plot.size == 0:
            raise ValueError("no positive plottable samples for differential plot")

    if use_loglog:
        sh_edges = centers_to_edges(x_sh_plot)
        osh_edges = centers_to_edges(x_osh_plot)
        if sh_edges[0] <= 0:
            sh_edges[0] = max(np.nextafter(0.0, 1.0), x_sh_plot[0] / 2.0)
        if osh_edges[0] <= 0:
            osh_edges[0] = max(np.nextafter(0.0, 1.0), x_osh_plot[0] / 2.0)
        ax.stairs(y_sh_plot, sh_edges, lw=1.8, label="SH12A", baseline=None)
        ax.stairs(y_osh_plot, osh_edges, lw=1.5, ls="--", label="OpenShieldHit", baseline=None)
        ax.set_xscale("log")
        ax.set_yscale("log")
    else:
        ax.plot(x_sh_plot, y_sh_plot, lw=1.8, label="SH12A")
        ax.plot(x_osh_plot, y_osh_plot, lw=1.5, ls="--", label="OpenShieldHit")
    ax.set_title(" | ".join(title_top_parts) + "\n" + " | ".join(title_bottom_parts))
    ax.set_xlabel(infer_x_label(rel_path, page_meta))
    ax.set_ylabel(infer_y_label(page_meta))
    ax.grid(True, alpha=0.35)
    ax.legend()

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_file, dpi=dpi)
    return fig


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
    pdf_report = args.pdf_report if str(args.pdf_report).strip() else None
    if pdf_report is not None:
        pdf_report.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(pdf_report) if pdf_report is not None else nullcontext() as pdf:
        for rel_path in shared_keys:
            out_file = (args.out_dir / rel_path).with_suffix(".png")
            try:
                fig = make_plot(
                    rel_path,
                    sh12a_map[rel_path],
                    osh_map[rel_path],
                    out_file,
                    args.sh12a_input_root,
                    args.osh_input_root,
                    args.dpi,
                )
                if pdf is not None:
                    pdf.savefig(fig)
                plt.close(fig)
                made += 1
            except Exception as exc:  # noqa: BLE001
                skipped += 1
                print(f"[skip] {rel_path}: {exc}")

    print(f"Done. Wrote {made} plot(s) to: {args.out_dir}")
    if pdf_report is not None:
        print(f"Wrote PDF report to: {pdf_report}")
    if skipped:
        print(f"Skipped {skipped} pair(s) due to parse/plot errors.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
