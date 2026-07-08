#!/usr/bin/env python3
"""Build a static GitHub Pages site from manifest-driven comparison plots.

Discovery flow:
  data/*/code.yaml            → registered MC codes (name, colour, url)
  data/output_catalog.json    → canonical output type labels and geometry
  data/**/manifest.json       → per-code, per-plan output file index
  {plots_dir}/{plan}/*.html   → interactive Plotly plots already generated
                                by tools/generate_comparison_plots.py

Site layout:
  {out_dir}/
    index.html                → landing page with code list and plan cards
    plans/{plan}.html         → per-plan page with grouped plot cards
    assets/site.css

Usage:
    python tools/build_pages_site.py
    python tools/build_pages_site.py --out-dir pages-site --plots-dir pages-site/plots
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_catalog(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "output_types": data.get("output_types", {}),
        "geometry_classes": data.get("geometry_classes", {}),
    }


def load_code_styles(data_root: Path) -> dict[str, dict]:
    styles: dict[str, dict] = {}
    for p in sorted(data_root.glob("*/code.yaml")):
        info = yaml.safe_load(p.read_text(encoding="utf-8"))
        styles[info["short"]] = info
    return styles


def load_manifests(data_root: Path) -> list[dict]:
    manifests = []
    for p in sorted(data_root.rglob("manifest.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        data["_dir"] = p.parent
        manifests.append(data)
    return manifests


def build_availability(
    manifests: list[dict],
) -> dict[str, dict[str, set[str]]]:
    """
    Returns {plan: {output_type: {code_short, ...}}}.
    Only includes primary_data and derived entries with an output_type.
    """
    avail: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for m in manifests:
        plan = m["plan"]
        code_short = m["code"]["short"]
        for entry in m.get("outputs", []):
            if entry.get("role") not in ("primary_data", "derived"):
                continue
            for f in entry.get("files", []):
                ot = f.get("output_type")
                if ot:
                    avail[plan][ot].add(code_short)
    return {p: dict(d) for p, d in avail.items()}


def codes_per_plan(manifests: list[dict]) -> dict[str, set[str]]:
    """Which codes have any result for each plan."""
    cpp: dict[str, set[str]] = defaultdict(set)
    for m in manifests:
        cpp[m["plan"]].add(m["code"]["short"])
    return dict(cpp)


def collect_preview_images(
    manifests: list[dict],
) -> dict[str, dict[str, list[str]]]:
    """
    {plan: {code_short: [rel_paths_to_preview_pngs, ...]}}.
    Used to show 2D map previews on plan pages.
    """
    previews: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for m in manifests:
        plan = m["plan"]
        code_short = m["code"]["short"]
        result_dir = m["_dir"]
        for entry in m.get("outputs", []):
            if entry.get("role") != "preview_image":
                continue
            for f in entry.get("files", []):
                path = result_dir / f["path"]
                if path.exists():
                    previews[plan][code_short].append(str(path))
    return dict(previews)


def build_download_index(
    manifests: list[dict],
) -> dict[tuple[str, str], list[dict]]:
    """
    Returns {(plan, output_type): [{code_short, src_path, filename}, ...]}.
    Only primary_data and derived files that carry an output_type.
    """
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
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
                src = result_dir / f["path"]
                if src.exists():
                    index[(plan, ot)].append({
                        "code_short": code_short,
                        "src_path": src,
                        "filename": src.name,
                    })
    return dict(index)


def copy_data_files(
    download_index: dict[tuple[str, str], list[dict]],
    site_root: Path,
) -> dict[tuple[str, str], list[dict]]:
    """
    Copy data files into {site_root}/data/{plan}/{code}/{filename}.
    Returns the same index enriched with a 'dest_rel' key (relative to site_root).
    """
    enriched: dict[tuple[str, str], list[dict]] = {}
    for (plan, ot), files in download_index.items():
        enriched[(plan, ot)] = []
        seen: set[Path] = set()
        for item in files:
            src = item["src_path"]
            if src in seen:
                continue
            seen.add(src)
            dest = site_root / "data" / plan / item["code_short"] / item["filename"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            enriched[(plan, ot)].append({
                **item,
                "dest_rel": f"data/{plan}/{item['code_short']}/{item['filename']}",
            })
    return enriched




# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def text_on_bg(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 140 else "#1b2226"


def code_pill(code_short: str, code_styles: dict[str, dict], *, size: str = "normal") -> str:
    style = code_styles.get(code_short, {})
    color = style.get("display_color", "#888888")
    fg = text_on_bg(color)
    name = html.escape(style.get("name", code_short))
    font_size = "0.75rem" if size == "small" else "0.85rem"
    padding = "0.2rem 0.55rem" if size == "small" else "0.3rem 0.75rem"
    return (
        f'<span class="code-pill" '
        f'style="background:{color};color:{fg};font-size:{font_size};padding:{padding};">'
        f"{name}</span>"
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def html_page(title: str, body: str, *, root_prefix: str = ".") -> str:
    escaped = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped}</title>
  <link rel="stylesheet" href="{root_prefix}/assets/site.css">
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <a class="brand" href="{root_prefix}/index.html">2022 DCPT LET</a>
      <nav class="nav">
        <a href="{root_prefix}/index.html#plans">Plans</a>
        <a href="{root_prefix}/index.html#codes">Codes</a>
      </nav>
    </header>
    {body}
  </div>
</body>
</html>
"""


def css_text() -> str:
    return """\
:root {
  color-scheme: light;
  --bg: #f6f4ef;
  --panel: #fffdf8;
  --panel-strong: #ffffff;
  --text: #1b2226;
  --muted: #58656d;
  --border: #d8d2c6;
  --accent: #005f73;
  --accent-soft: #d8eef1;
  --shadow: 0 14px 34px rgba(27,34,38,.08);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(238,155,0,.12), transparent 28rem),
    linear-gradient(180deg, #fbfaf6 0%, var(--bg) 100%);
}
a { color: var(--accent); }
.shell {
  width: min(1200px, calc(100vw - 2rem));
  margin: 0 auto;
  padding: 1rem 0 3rem;
}
.topbar {
  display: flex; align-items: center;
  justify-content: space-between; gap: 1rem;
  margin-bottom: 2rem;
}
.brand { font-size: 1.15rem; font-weight: 700; text-decoration: none; color: var(--text); }
.nav { display: flex; flex-wrap: wrap; gap: 1rem; }
.nav a { text-decoration: none; }

.hero, .panel {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 20px; box-shadow: var(--shadow);
}
.hero { padding: 2rem; margin-bottom: 2rem; }
.hero h1 { margin: 0 0 .75rem; font-size: clamp(1.8rem, 4vw, 2.8rem); line-height: 1.05; }
.panel { padding: 1.4rem; margin-bottom: 1.6rem; }
.section-title { margin: 0 0 .3rem; font-size: 1.4rem; }
.section-desc { color: var(--muted); margin: 0 0 1rem; font-size: .95rem; }

.hero p, .panel p, .plan-meta, .eyebrow, .empty-state, .footer-note { color: var(--muted); }

/* stat strip */
.hero-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); margin-top: 1.5rem; }
.stat { background: var(--panel-strong); border: 1px solid var(--border); border-radius: 16px; padding: 1rem; }
.stat strong { display: block; font-size: 1.5rem; color: var(--text); }
.stat span { font-size: .85rem; color: var(--muted); }

/* code pill */
.code-pill {
  display: inline-flex; align-items: center;
  border-radius: 999px; font-weight: 600;
  padding: .3rem .75rem; font-size: .85rem;
}
.pill-row { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; }

/* plan grid */
.plan-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-top: 1rem; }
.plan-card {
  background: var(--panel-strong); border: 1px solid var(--border);
  border-radius: 18px; padding: 1rem;
}
.plan-card h3 { margin: 0 0 .5rem; }
.plan-card .plan-meta { font-size: .85rem; }

/* code registry cards */
.code-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin-top: 1rem; }
.code-card {
  background: var(--panel-strong); border: 1px solid var(--border);
  border-radius: 16px; padding: 1rem;
  border-top: 4px solid var(--accent);
}
.code-card h3 { margin: 0 0 .3rem; font-size: 1rem; }
.code-card .muted { color: var(--muted); font-size: .85rem; }

/* plot card grid */
.plot-grid { display: grid; gap: .8rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.plot-card {
  background: var(--panel-strong); border: 1px solid var(--border);
  border-radius: 14px; padding: .9rem 1rem;
  display: flex; flex-direction: column; gap: .6rem;
}
.plot-card h3 { margin: 0; font-size: .95rem; font-weight: 600; }
.plot-card .plot-link {
  display: inline-flex; align-items: center; gap: .35rem;
  border: 1px solid var(--border); border-radius: 999px;
  padding: .3rem .8rem; font-size: .85rem;
  color: var(--accent); text-decoration: none; background: #fff;
  width: fit-content;
}
.plot-card .plot-link:hover { background: var(--accent-soft); }
.plot-card .missing { color: var(--muted); font-size: .8rem; font-style: italic; }

/* PDF download button */
.btn-pdf {
  display: inline-flex; align-items: center; gap: .4rem;
  background: var(--accent); color: #fff; border-radius: 6px;
  padding: .45rem 1rem; font-size: .9rem; font-weight: 600;
  text-decoration: none; margin-top: 1rem;
}
.btn-pdf:hover { opacity: .85; }

/* download links */
.dl-row { display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; margin-top: .1rem; }
.dl-label { font-size: .75rem; color: var(--muted); margin-right: .2rem; white-space: nowrap; }
.dl-link {
  display: inline-flex; align-items: center; gap: .2rem;
  border: 1px solid var(--border); border-radius: 999px;
  padding: .15rem .55rem; font-size: .75rem;
  color: var(--muted); text-decoration: none; background: #fff;
  white-space: nowrap;
}
.dl-link:hover { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }

/* back link */
.back-link {
  display: inline-flex; align-items: center;
  border: 1px solid var(--border); border-radius: 999px;
  padding: .3rem .8rem; font-size: .85rem;
  color: var(--text); text-decoration: none; background: #fff;
  margin-bottom: 1rem;
}

/* preview images (2D maps) */
.preview-grid { display: grid; gap: .8rem; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.preview-card {
  background: var(--panel-strong); border: 1px solid var(--border);
  border-radius: 14px; overflow: hidden;
}
.preview-card img { display: block; width: 100%; object-fit: cover; background: #f1f1f1; }
.preview-card .preview-label { padding: .5rem .8rem; font-size: .85rem; color: var(--muted); }

.footer-note { margin-top: 2rem; font-size: .9rem; }

@media (max-width: 640px) {
  .shell { width: min(100vw - 1rem, 100%); }
  .topbar { flex-direction: column; align-items: flex-start; }
  .hero, .panel { padding: 1rem; }
}
"""


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------

# Ordered sections: (geometry class, section title, description)
GEOMETRY_SECTIONS = [
    (
        "depth_Z",
        "Depth profiles",
        "1D profiles along the beam (Z) axis, narrow lateral acceptance. "
        "One plot per quantity × medium × particle filter. All available codes overlaid.",
    ),
    (
        "spectrum_target",
        "Target spectra",
        "Differential LET, dE/dx, and kinetic-energy spectra in the target volume. "
        "Log-log scale with stair-step bins.",
    ),
    (
        "target",
        "Target scalars",
        "Single integrated values in the target detector volume (5×5×2 mm³). "
        "Shown as a grouped bar chart per code.",
    ),
    (
        "map_XZ",
        "Longitudinal dose maps (XZ)",
        "2D dose maps in the longitudinal plane. Preview images only.",
    ),
    (
        "map_XY",
        "Transverse dose maps (XY)",
        "2D dose maps in the transverse plane. Preview images only.",
    ),
]


def render_plot_card(
    output_type: str,
    codes: set[str],
    code_styles: dict[str, dict],
    plot_rel: str,
    plot_exists: bool,
    catalog_meta: dict,
    download_files: list[dict],
) -> str:
    label = html.escape(catalog_meta.get("label", output_type))
    pills = " ".join(code_pill(c, code_styles, size="small") for c in sorted(codes))
    if plot_exists:
        link_html = (
            f'<a class="plot-link" href="{html.escape(plot_rel)}" target="_blank">'
            f"Open interactive plot ↗</a>"
        )
    else:
        link_html = '<span class="missing">Plot not yet generated</span>'

    dl_html = ""
    if download_files:
        links: list[str] = []
        for item in download_files:
            cs = code_styles.get(item["code_short"], {})
            code_name = html.escape(cs.get("name", item["code_short"]))
            fname = html.escape(item["filename"])
            dest = html.escape(f"../{item['dest_rel']}")
            links.append(
                f'<a class="dl-link" href="{dest}" download title="{code_name}">'
                f"↓ {code_name} · {fname}</a>"
            )
        dl_html = (
            '<div class="dl-row"><span class="dl-label">Data:</span>'
            + "".join(links)
            + "</div>"
        )

    return f"""
<article class="plot-card">
  <h3>{label}</h3>
  <div class="pill-row">{pills}</div>
  {link_html}
  {dl_html}
</article>"""


def render_plan_page(
    plan: str,
    plan_codes: set[str],
    availability: dict[str, set[str]],
    catalog: dict,
    code_styles: dict[str, dict],
    plots_rel_from_plan: str,
    plots_dir: Path,
    preview_images: dict[str, list[str]],
    download_index: dict[tuple[str, str], list[dict]],
) -> str:
    output_types = catalog["output_types"]
    pills = " ".join(code_pill(c, code_styles) for c in sorted(plan_codes))

    # Group available output types by geometry class
    by_geometry: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for ot, codes in sorted(availability.items()):
        meta = output_types.get(ot, {})
        geom = meta.get("geometry", ot.split(".")[0])
        by_geometry[geom][ot] = codes

    sections_html: list[str] = []
    for geom_class, title, desc in GEOMETRY_SECTIONS:
        if geom_class in ("map_XZ", "map_XY"):
            # Show preview images instead of plot links
            imgs: list[str] = []
            for code_short, paths in preview_images.items():
                for img_path in paths:
                    img_name = Path(img_path).name
                    # Only show maps that match this geometry
                    if geom_class == "map_XZ" and "XZ" not in img_name:
                        continue
                    if geom_class == "map_XY" and "XY" not in img_name:
                        continue
                    cs = code_styles.get(code_short, {})
                    code_name = html.escape(cs.get("name", code_short))
                    alt = html.escape(f"{code_name} – {img_name}")
                    imgs.append(
                        f'<div class="preview-card">'
                        f'<img loading="lazy" src="{html.escape(img_path)}" alt="{alt}">'
                        f'<div class="preview-label">{code_name} – {html.escape(img_name)}</div>'
                        f'</div>'
                    )
            if not imgs:
                continue
            inner = f'<div class="preview-grid">{"".join(imgs)}</div>'
        else:
            ots = by_geometry.get(geom_class, {})
            if not ots:
                continue
            cards: list[str] = []
            for ot, codes in sorted(ots.items()):
                plot_file = plots_dir / plan / f"{ot}.html"
                plot_rel = f"{plots_rel_from_plan}/{plan}/{ot}.html"
                cards.append(
                    render_plot_card(
                        ot, codes, code_styles,
                        plot_rel, plot_file.exists(),
                        output_types.get(ot, {}),
                        download_index.get((plan, ot), []),
                    )
                )
            inner = f'<div class="plot-grid">{"".join(cards)}</div>'

        sections_html.append(f"""
<section class="panel">
  <h2 class="section-title">{html.escape(title)}</h2>
  <p class="section-desc">{html.escape(desc)}</p>
  {inner}
</section>""")

    body = f"""
<main>
  <a class="back-link" href="../index.html">← Back to overview</a>
  <section class="hero">
    <p class="eyebrow">Plan browser</p>
    <h1>{html.escape(plan)}</h1>
    <div class="pill-row" style="margin-top:.8rem">{pills}</div>
    <a class="btn-pdf" href="{html.escape(plan)}.pdf" download>⬇ Download PDF (all plots for this plan)</a>
  </section>
  {"".join(sections_html)}
</main>"""
    return html_page(plan, body, root_prefix="..")


def render_index(
    plans: list[str],
    plan_codes: dict[str, set[str]],
    plan_availability: dict[str, dict[str, set[str]]],
    code_styles: dict[str, dict],
    catalog: dict,
    generated_at: str,
) -> str:
    total_plots = sum(len(ots) for ots in plan_availability.values())

    plan_cards: list[str] = []
    for plan in plans:
        codes = plan_codes.get(plan, set())
        pills = " ".join(code_pill(c, code_styles, size="small") for c in sorted(codes))
        n_ots = len(plan_availability.get(plan, {}))
        plan_cards.append(f"""
<article class="plan-card">
  <div class="pill-row" style="margin-bottom:.5rem">{pills}</div>
  <h3><a href="plans/{html.escape(plan)}.html">{html.escape(plan)}</a></h3>
  <p class="plan-meta">{n_ots} output type(s) catalogued</p>
</article>""")

    code_cards: list[str] = []
    for short, info in sorted(code_styles.items(), key=lambda x: x[1].get("name", x[0])):
        color = info.get("display_color", "#888")
        name = html.escape(info.get("name", short))
        url = info.get("url", "")
        link = f'<a href="{html.escape(url)}" target="_blank">{name}</a>' if url else name
        code_cards.append(f"""
<article class="code-card" style="border-top-color:{color}">
  <h3>{link}</h3>
  <p class="muted">short: <code>{html.escape(short)}</code></p>
</article>""")

    body = f"""
<main>
  <section class="hero">
    <p class="eyebrow">Interactive MC code comparison gallery · built {generated_at}</p>
    <h1>2022 DCPT LET benchmark</h1>
    <p>
      Comparison of Monte Carlo codes for LET-weighted quantities in a silicon
      detector benchmark at DCPT. Each plot overlays all available codes for a
      given scorer, quantity, medium, and particle filter.
      <strong>Click any plot to open an interactive view</strong> — hover for exact values,
      click the legend to toggle codes.
    </p>
    <div class="hero-grid">
      <div class="stat"><strong>{len(plans)}</strong><span>plans</span></div>
      <div class="stat"><strong>{len(code_styles)}</strong><span>MC codes</span></div>
      <div class="stat"><strong>{total_plots}</strong><span>comparison plots</span></div>
    </div>
  </section>

  <section class="panel" id="plans">
    <h2 class="section-title">Plans</h2>
    <p>Select a plan to browse all available comparison plots.</p>
    <div class="plan-grid">{"".join(plan_cards)}</div>
  </section>

  <section class="panel" id="codes">
    <h2 class="section-title">Registered codes</h2>
    <div class="code-grid">{"".join(code_cards)}</div>
  </section>

  <p class="footer-note">
    Data lives in the repository under <code>data/</code>. This site is regenerated in CI
    from <code>data/**/manifest.json</code> and <code>data/output_catalog.json</code>.
  </p>
</main>"""
    return html_page("2022 DCPT LET – MC code comparison gallery", body, root_prefix=".")


# ---------------------------------------------------------------------------
# Main
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
        "--plots-dir", type=Path, default=Path("_pages/plots"),
        help="Directory where generate_comparison_plots.py wrote HTML files (default: _pages/plots).",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("_pages"),
        help="Output directory for the generated site (default: _pages).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    site_root = args.out_dir.resolve()
    plots_dir = args.plots_dir.resolve()

    catalog = load_catalog(args.catalog)
    code_styles = load_code_styles(args.data_root)
    manifests = load_manifests(args.data_root)
    availability = build_availability(manifests)
    plan_codes = codes_per_plan(manifests)
    preview_images = collect_preview_images(manifests)
    raw_download_index = build_download_index(manifests)

    plans = sorted(availability)
    print(
        f"Codes: {len(code_styles)}  |  Plans: {len(plans)}  |  "
        f"Output type groups: {sum(len(v) for v in availability.values())}"
    )

    # Re-create site root (except plots dir if it lives inside)
    if site_root.exists():
        for child in site_root.iterdir():
            if child.resolve() == plots_dir:
                continue  # don't wipe plots we just generated
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    site_root.mkdir(parents=True, exist_ok=True)

    download_index = copy_data_files(raw_download_index, site_root)

    write_text(site_root / ".nojekyll", "")
    write_text(site_root / "assets/site.css", css_text())

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Index page
    write_text(
        site_root / "index.html",
        render_index(plans, plan_codes, availability, code_styles, catalog, generated_at),
    )

    # Relative path from a plan page (plans/{plan}.html) back to the plots dir
    # If plots_dir is at site_root/plots, this is "../plots"
    try:
        plots_rel = plots_dir.relative_to(site_root)
        plots_rel_from_plan = f"../{plots_rel.as_posix()}"
    except ValueError:
        # plots_dir is outside site_root — use absolute path (won't work on Pages)
        plots_rel_from_plan = str(plots_dir)

    # Per-plan pages
    for plan in plans:
        write_text(
            site_root / f"plans/{plan}.html",
            render_plan_page(
                plan=plan,
                plan_codes=plan_codes.get(plan, set()),
                availability=availability.get(plan, {}),
                catalog=catalog,
                code_styles=code_styles,
                plots_rel_from_plan=plots_rel_from_plan,
                plots_dir=plots_dir,
                preview_images=preview_images.get(plan, {}),
                download_index=download_index,
            ),
        )
        print(f"  wrote plans/{plan}.html")

    print(f"\nSite written to: {site_root}")

    # Generate per-plan PDF reports (parallel) so the download links work
    print("\nGenerating per-plan PDF reports...")
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from generate_pdf_report import generate as _gen_pdf
    _gen_pdf(args.data_root, args.catalog, site_root / "plans")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
