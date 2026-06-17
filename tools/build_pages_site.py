#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from plot_sh12a_vs_osh import (
    PAGE_RE,
    format_page_title,
    humanize_geo_label,
    infer_x_label,
    infer_y_label,
    is_diff_plot,
    lookup_output_metadata,
    normalize_metric_name,
    plan_input_hint,
)


@dataclass(frozen=True)
class DownloadLink:
    label: str
    href: str


@dataclass(frozen=True)
class GalleryItem:
    plan: str
    title: str
    subtitle: str
    details: tuple[str, ...]
    image_href: str
    thumb_href: str
    downloads: tuple[DownloadLink, ...] = ()


@dataclass
class PlanSection:
    title: str
    intro: str
    items: list[GalleryItem] = field(default_factory=list)


@dataclass
class PlanPage:
    plan: str
    summary: tuple[str, ...]
    sections: list[PlanSection]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a static GitHub Pages gallery for OpenShieldHit results and "
            "SH12A-vs-OpenShieldHit comparison plots."
        )
    )
    parser.add_argument(
        "--osh-results-root",
        type=Path,
        default=Path("data/openshieldhit/results"),
        help="Root directory with tracked OpenShieldHit result PNG/DAT files.",
    )
    parser.add_argument(
        "--comparison-root",
        type=Path,
        default=Path("data/comparisons/sh12a_vs_osh"),
        help="Root directory with comparison PNG files.",
    )
    parser.add_argument(
        "--pdf-root",
        action="append",
        type=Path,
        default=[],
        help="Directory scanned recursively for PDF reports. Repeat as needed.",
    )
    parser.add_argument(
        "--osh-input-root",
        type=Path,
        default=Path("data/openshieldhit/input"),
        help="OpenShieldHit input root used for plot metadata.",
    )
    parser.add_argument(
        "--sh12a-input-root",
        type=Path,
        default=Path("data/sh12a/input"),
        help="SH12A input root used for plot metadata.",
    )
    parser.add_argument(
        "--sh12a-results-root",
        type=Path,
        default=Path("data/sh12a/results"),
        help="SH12A results root used for downloadable ASCII source links.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("_pages"),
        help="Output directory for the generated static site.",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def relative_href(from_file: Path, to_file: Path) -> str:
    return os.path.relpath(to_file, start=from_file.parent).replace(os.sep, "/")


def html_page(title: str, body: str, *, root_prefix: str = ".") -> str:
    escaped_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <link rel="stylesheet" href="{root_prefix}/assets/site.css">
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <a class="brand" href="{root_prefix}/index.html">2022 DCPT LET</a>
      <nav class="nav">
        <a href="{root_prefix}/index.html#plans">Plans</a>
        <a href="{root_prefix}/index.html#reports">Reports</a>
      </nav>
    </header>
    {body}
  </div>
</body>
</html>
"""


def css_text() -> str:
    return """
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
  --shadow: 0 14px 34px rgba(27, 34, 38, 0.08);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(238, 155, 0, 0.12), transparent 28rem),
    linear-gradient(180deg, #fbfaf6 0%, var(--bg) 100%);
}

a {
  color: var(--accent);
}

.shell {
  width: min(1200px, calc(100vw - 2rem));
  margin: 0 auto;
  padding: 1rem 0 3rem;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
}

.brand {
  font-size: 1.15rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--text);
}

.nav {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.nav a {
  text-decoration: none;
}

.hero,
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.hero {
  padding: 2rem;
  margin-bottom: 2rem;
}

.hero h1 {
  margin: 0 0 0.75rem;
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1.05;
}

.hero p,
.panel p,
.plan-meta,
.card-copy,
.eyebrow,
.download-list,
.empty-state,
.footer-note {
  color: var(--muted);
}

.hero-grid,
.plan-grid,
.gallery {
  display: grid;
  gap: 1rem;
}

.hero-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin-top: 1.5rem;
}

.stat {
  background: var(--panel-strong);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1rem;
}

.stat strong {
  display: block;
  font-size: 1.6rem;
  color: var(--text);
}

.section-title {
  margin: 0 0 0.4rem;
  font-size: 1.6rem;
}

.panel {
  padding: 1.4rem;
  margin-bottom: 1.6rem;
}

.plan-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.plan-card,
.gallery-card {
  background: var(--panel-strong);
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
}

.plan-card {
  padding: 1rem;
}

.plan-card h3,
.gallery-card h3 {
  margin: 0 0 0.5rem;
}

.pill-row,
.download-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill,
.download-row a,
.back-link {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.35rem 0.8rem;
  text-decoration: none;
}

.pill {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}

.download-row a,
.back-link {
  border: 1px solid var(--border);
  color: var(--text);
  background: #fff;
}

.gallery {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.gallery-card img {
  display: block;
  width: 100%;
  height: 200px;
  object-fit: cover;
  background: #f1f1f1;
}

.card-body {
  padding: 1rem;
}

.card-copy {
  margin: 0.3rem 0 0.7rem;
}

.detail-list {
  margin: 0 0 0.9rem;
  padding-left: 1rem;
  color: var(--muted);
}

.detail-list li {
  margin: 0.2rem 0;
}

.footer-note {
  margin-top: 2rem;
  font-size: 0.95rem;
}

@media (max-width: 640px) {
  .shell {
    width: min(100vw - 1rem, 100%);
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero,
  .panel {
    padding: 1rem;
  }
}
"""


def render_gallery(items: list[GalleryItem]) -> str:
    if not items:
        return '<p class="empty-state">No figures available in this section.</p>'

    cards: list[str] = []
    for item in items:
        details = "".join(f"<li>{html.escape(line)}</li>" for line in item.details)
        downloads = "".join(
            f'<a href="{html.escape(link.href)}">{html.escape(link.label)}</a>'
            for link in item.downloads
        )
        cards.append(
            f"""
<article class="gallery-card">
  <a href="{html.escape(item.image_href)}">
    <img loading="lazy" src="{html.escape(item.thumb_href)}" alt="{html.escape(item.title)}">
  </a>
  <div class="card-body">
    <h3>{html.escape(item.title)}</h3>
    <p class="card-copy">{html.escape(item.subtitle)}</p>
    <ul class="detail-list">{details}</ul>
    <div class="download-row">{downloads}</div>
  </div>
</article>
"""
        )
    return f'<div class="gallery">{"".join(cards)}</div>'


def plot_title_parts(
    rel_path: Path,
    sh12a_input_root: Path,
    osh_input_root: Path,
) -> tuple[str, str, tuple[str, ...]]:
    output_meta, page_index = lookup_output_metadata(rel_path, sh12a_input_root, osh_input_root)
    page_meta = output_meta.pages[page_index] if output_meta else None
    geo_label = humanize_geo_label(output_meta.geo) if output_meta else None
    block_label = output_meta.name if output_meta else PAGE_RE.sub(r"\g<stem>", rel_path.stem)
    metric = format_page_title(page_meta) if page_meta else normalize_metric_name(rel_path.name)
    page_label = ""
    if page_meta and output_meta and len(output_meta.pages) > 1:
        page_label = f"page {page_index + 1}"
    hint = plan_input_hint(rel_path.parts[0], sh12a_input_root, osh_input_root)
    kind = "Differential" if is_diff_plot(rel_path, page_meta) else "Profile / map"
    x_label = infer_x_label(rel_path, page_meta)
    y_label = infer_y_label(page_meta)

    subtitle_parts = [part for part in (geo_label, block_label, page_label) if part]
    if hint:
        subtitle_parts.append(f"input: {hint}")

    details = [kind, f"x: {x_label}", f"y: {y_label}"]
    return metric, " | ".join(subtitle_parts) if subtitle_parts else rel_path.parts[0], tuple(details)


def collect_results_items(
    site_root: Path,
    osh_results_root: Path,
    osh_input_root: Path,
) -> dict[str, list[GalleryItem]]:
    items_by_plan: dict[str, list[GalleryItem]] = {}
    for image_source in sorted(osh_results_root.rglob("*.png")):
        rel_from_root = image_source.relative_to(osh_results_root)
        if len(rel_from_root.parts) != 2:
            continue
        plan = rel_from_root.parts[0]
        site_image = Path("assets/openshieldhit") / rel_from_root
        copy_file(image_source, site_root / site_image)

        downloads = [DownloadLink("PNG", relative_href(site_root / f"plans/{plan}.html", site_root / site_image))]

        dat_source = image_source.with_suffix(".dat")
        if dat_source.exists():
            site_dat = Path("assets/openshieldhit-data") / dat_source.relative_to(osh_results_root)
            copy_file(dat_source, site_root / site_dat)
            downloads.append(
                DownloadLink(
                    "DAT",
                    relative_href(site_root / f"plans/{plan}.html", site_root / site_dat),
                )
            )

        metric, subtitle, details = plot_title_parts(
            rel_from_root,
            osh_input_root,
            osh_input_root,
        )
        item = GalleryItem(
            plan=plan,
            title=metric,
            subtitle=subtitle,
            details=details,
            image_href=relative_href(site_root / f"plans/{plan}.html", site_root / site_image),
            thumb_href=relative_href(site_root / f"plans/{plan}.html", site_root / site_image),
            downloads=tuple(downloads),
        )
        items_by_plan.setdefault(plan, []).append(item)
    return items_by_plan


def collect_comparison_items(
    site_root: Path,
    comparison_root: Path,
    sh12a_results_root: Path,
    osh_results_root: Path,
    sh12a_input_root: Path,
    osh_input_root: Path,
) -> dict[str, list[GalleryItem]]:
    items_by_plan: dict[str, list[GalleryItem]] = {}
    for image_source in sorted(comparison_root.rglob("*.png")):
        rel_from_root = image_source.relative_to(comparison_root)
        if len(rel_from_root.parts) != 2:
            continue
        plan = rel_from_root.parts[0]
        site_image = Path("assets/comparisons") / rel_from_root
        copy_file(image_source, site_root / site_image)

        downloads = [DownloadLink("PNG", relative_href(site_root / f"plans/{plan}.html", site_root / site_image))]
        shared_dat_rel = rel_from_root.with_suffix(".dat")
        sh12a_dat = sh12a_results_root / shared_dat_rel
        osh_dat = osh_results_root / shared_dat_rel
        if sh12a_dat.exists():
            site_dat = Path("assets/comparison-data/sh12a") / shared_dat_rel
            copy_file(sh12a_dat, site_root / site_dat)
            downloads.append(
                DownloadLink(
                    "SH12A DAT",
                    relative_href(site_root / f"plans/{plan}.html", site_root / site_dat),
                )
            )
        if osh_dat.exists():
            site_dat = Path("assets/comparison-data/openshieldhit") / shared_dat_rel
            copy_file(osh_dat, site_root / site_dat)
            downloads.append(
                DownloadLink(
                    "OpenShieldHit DAT",
                    relative_href(site_root / f"plans/{plan}.html", site_root / site_dat),
                )
            )

        metric, subtitle, details = plot_title_parts(
            rel_from_root,
            sh12a_input_root,
            osh_input_root,
        )
        item = GalleryItem(
            plan=plan,
            title=metric,
            subtitle=subtitle,
            details=details,
            image_href=relative_href(site_root / f"plans/{plan}.html", site_root / site_image),
            thumb_href=relative_href(site_root / f"plans/{plan}.html", site_root / site_image),
            downloads=tuple(downloads),
        )
        items_by_plan.setdefault(plan, []).append(item)
    return items_by_plan


def collect_report_links(site_root: Path, page_file: Path, pdf_roots: list[Path]) -> list[DownloadLink]:
    links: list[DownloadLink] = []
    for pdf_root in pdf_roots:
        if not pdf_root.exists():
            continue
        for pdf_source in sorted(pdf_root.rglob("*.pdf")):
            site_pdf = Path("assets/reports") / pdf_source.name
            copy_file(pdf_source, site_root / site_pdf)
            links.append(
                DownloadLink(
                    pdf_source.name,
                    relative_href(page_file, site_root / site_pdf),
                )
            )
    return links


def render_home_page(
    site_root: Path,
    plan_pages: list[PlanPage],
    report_links: list[DownloadLink],
) -> str:
    total_result_figures = sum(len(section.items) for page in plan_pages for section in page.sections[:1])
    total_comparison_figures = sum(
        len(section.items) for page in plan_pages for section in page.sections[1:]
    )

    plan_cards = []
    for page in plan_pages:
        plan_href = relative_href(site_root / "index.html", site_root / f"plans/{page.plan}.html")
        plan_cards.append(
            f"""
<article class="plan-card">
  <div class="pill-row"><span class="pill">{html.escape(page.plan)}</span></div>
  <h3><a href="{html.escape(plan_href)}">{html.escape(page.plan)}</a></h3>
  <p class="plan-meta">{html.escape(" | ".join(page.summary))}</p>
</article>
"""
        )

    report_html = "".join(
        f'<a href="{html.escape(link.href)}">{html.escape(link.label)}</a>' for link in report_links
    )
    report_panel = (
        f'<div class="download-row">{report_html}</div>'
        if report_links
        else '<p class="empty-state">No PDF reports were generated for this build.</p>'
    )

    body = f"""
<main>
  <section class="hero">
    <p class="eyebrow">Static browser built from committed simulation data and CI-generated comparisons.</p>
    <h1>OpenShieldHit and SH12A comparison gallery</h1>
    <p>
      This site publishes tracked OpenShieldHit result figures directly from the repository and
      overlays them with CI-generated SH12A-vs-OpenShieldHit comparison figures built from the
      corresponding ASCII <code>.dat</code> files.
    </p>
    <div class="hero-grid">
      <div class="stat"><strong>{len(plan_pages)}</strong><span>plans covered</span></div>
      <div class="stat"><strong>{total_result_figures}</strong><span>OpenShieldHit figures</span></div>
      <div class="stat"><strong>{total_comparison_figures}</strong><span>comparison figures</span></div>
      <div class="stat"><strong>{len(report_links)}</strong><span>downloadable PDF reports</span></div>
    </div>
  </section>

  <section class="panel" id="reports">
    <h2 class="section-title">Reports</h2>
    <p>
      PDF reports are built in CI from the current repository state so casual visitors can inspect
      the latest comparison bundle without running simulations locally.
    </p>
    {report_panel}
  </section>

  <section class="panel" id="plans">
    <h2 class="section-title">Plans</h2>
    <p>Select a plan to browse tracked OpenShieldHit figures, generated comparison PNGs, and linked ASCII data.</p>
    <div class="plan-grid">{"".join(plan_cards)}</div>
  </section>

  <p class="footer-note">
    The authoritative simulation data remains in the repository. This static site is a presentation
    layer generated from those files.
  </p>
</main>
"""
    return html_page("2022 DCPT LET gallery", body, root_prefix=".")


def render_plan_page(site_root: Path, page: PlanPage) -> str:
    section_html = []
    for section in page.sections:
        section_html.append(
            f"""
<section class="panel">
  <h2 class="section-title">{html.escape(section.title)}</h2>
  <p>{html.escape(section.intro)}</p>
  {render_gallery(section.items)}
</section>
"""
        )

    body = f"""
<main>
  <p><a class="back-link" href="../index.html">Back to overview</a></p>
  <section class="hero">
    <p class="eyebrow">Plan browser</p>
    <h1>{html.escape(page.plan)}</h1>
    <p>{html.escape(" | ".join(page.summary))}</p>
  </section>
  {"".join(section_html)}
</main>
"""
    return html_page(page.plan, body, root_prefix="..")


def build_plan_pages(
    results_items: dict[str, list[GalleryItem]],
    comparison_items: dict[str, list[GalleryItem]],
    sh12a_input_root: Path,
    osh_input_root: Path,
) -> list[PlanPage]:
    plans = sorted(set(results_items).union(comparison_items))
    plan_pages: list[PlanPage] = []
    for plan in plans:
        hint = plan_input_hint(plan, sh12a_input_root, osh_input_root)
        summary = [f"input hint: {hint}" if hint else "input hint unavailable"]
        sections = [
            PlanSection(
                title="OpenShieldHit results",
                intro=(
                    "Tracked PNG figures from the repository. When available, the matching ASCII "
                    "plot data is linked alongside each image."
                ),
                items=results_items.get(plan, []),
            ),
            PlanSection(
                title="SH12A vs OpenShieldHit comparisons",
                intro=(
                    "Generated in CI from paired SH12A and OpenShieldHit .dat files. Differential "
                    "comparisons keep the stair-step representation and log scaling introduced in "
                    "the local plotting workflow."
                ),
                items=comparison_items.get(plan, []),
            ),
        ]
        plan_pages.append(PlanPage(plan=plan, summary=tuple(summary), sections=sections))
    return plan_pages


def write_manifest(site_root: Path, plan_pages: list[PlanPage], report_links: list[DownloadLink]) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "plans": [
            {
                "plan": page.plan,
                "result_figures": len(page.sections[0].items),
                "comparison_figures": len(page.sections[1].items),
                "summary": list(page.summary),
            }
            for page in plan_pages
        ],
        "reports": [{"label": link.label, "href": link.href} for link in report_links],
    }
    write_text(site_root / "site-manifest.json", json.dumps(payload, indent=2) + "\n")


def main() -> int:
    args = parse_args()

    site_root = args.out_dir.resolve()
    if site_root.exists():
        shutil.rmtree(site_root)
    site_root.mkdir(parents=True, exist_ok=True)

    write_text(site_root / ".nojekyll", "")
    write_text(site_root / "assets/site.css", css_text())

    results_items = collect_results_items(
        site_root,
        args.osh_results_root.resolve(),
        args.osh_input_root.resolve(),
    )
    comparison_items = collect_comparison_items(
        site_root,
        args.comparison_root.resolve(),
        args.sh12a_results_root.resolve(),
        args.osh_results_root.resolve(),
        args.sh12a_input_root.resolve(),
        args.osh_input_root.resolve(),
    )
    plan_pages = build_plan_pages(
        results_items,
        comparison_items,
        args.sh12a_input_root.resolve(),
        args.osh_input_root.resolve(),
    )

    report_links = collect_report_links(
        site_root,
        site_root / "index.html",
        [path.resolve() for path in args.pdf_root],
    )

    write_text(site_root / "index.html", render_home_page(site_root, plan_pages, report_links))
    for page in plan_pages:
        write_text(site_root / f"plans/{page.plan}.html", render_plan_page(site_root, page))

    write_manifest(site_root, plan_pages, report_links)

    print(f"Wrote static site to: {site_root}")
    print(f"Plans indexed: {len(plan_pages)}")
    print(f"PDF reports indexed: {len(report_links)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
