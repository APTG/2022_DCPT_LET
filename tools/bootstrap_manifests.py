#!/usr/bin/env python3
"""Bootstrap manifest.json stubs for plan directories that lack one.

Reads the existing hand-written manifests as templates (plan01_geoA for
sh12a and osh), generates manifests for all other plan directories, and
filters each output group to only include files that actually exist in
the target directory.  Existing manifests are never overwritten.

Usage:
    python tools/bootstrap_manifests.py           # write new manifests
    python tools/bootstrap_manifests.py --dry-run # only print what would be written
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


DATA_ROOT = Path("data")


def filter_outputs(outputs: list[dict], result_dir: Path) -> list[dict]:
    """Return a copy of the outputs list with missing files removed.
    Groups where no file survives are dropped entirely."""
    filtered = []
    for group in outputs:
        files = [
            f for f in group.get("files", [])
            if (result_dir / f["path"]).exists()
        ]
        if not files:
            continue
        g = copy.deepcopy(group)
        g["files"] = files
        filtered.append(g)
    return filtered


def make_manifest(template: dict, plan: str, result_dir: Path) -> dict:
    m = copy.deepcopy(template)
    m["plan"] = plan
    m["provenance"] = {
        "date": None,
        "input_path": f"data/{template['code']['short']}/input/{plan}",
    }
    m["statistics"] = {"normalization": "per_primary"}
    m["outputs"] = filter_outputs(template["outputs"], result_dir)
    return m


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without writing anything.")
    args = parser.parse_args()

    templates: dict[str, dict] = {}
    for manifest_path in sorted(DATA_ROOT.rglob("manifest.json")):
        m = json.loads(manifest_path.read_text())
        short = m["code"]["short"]
        if short not in templates:
            templates[short] = m

    written = skipped = 0
    for results_dir in sorted(DATA_ROOT.glob("*/results/*/")):
        code_dir = results_dir.parent.parent
        code_yaml = code_dir / "code.yaml"
        if not code_yaml.exists():
            continue

        import yaml
        code_info = yaml.safe_load(code_yaml.read_text())
        short = code_info["short"]

        if short not in templates:
            continue  # no template for this code yet

        manifest_path = results_dir / "manifest.json"
        if manifest_path.exists():
            skipped += 1
            continue

        # Check if the directory has any real data (not just a TODO placeholder)
        real_files = [
            f for f in results_dir.iterdir()
            if f.suffix in (".dat", ".txt", ".csv") and f.stem.lower() != "todo"
        ]
        if not real_files:
            print(f"  skip  {results_dir.relative_to(DATA_ROOT)}  (no data files)")
            skipped += 1
            continue

        plan = results_dir.name
        m = make_manifest(templates[short], plan, results_dir)

        if not m["outputs"]:
            print(f"  skip  {results_dir.relative_to(DATA_ROOT)}  (no outputs survived file filter)")
            skipped += 1
            continue

        rel = manifest_path.relative_to(DATA_ROOT)
        if args.dry_run:
            n_groups = len(m["outputs"])
            n_files = sum(len(g["files"]) for g in m["outputs"])
            print(f"  would write  {rel}  ({n_groups} groups, {n_files} files)")
        else:
            manifest_path.write_text(
                json.dumps(m, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            n_groups = len(m["outputs"])
            n_files = sum(len(g["files"]) for g in m["outputs"])
            print(f"  wrote  {rel}  ({n_groups} groups, {n_files} files)")
        written += 1

    action = "Would write" if args.dry_run else "Wrote"
    print(f"\n{action} {written} manifest(s), skipped {skipped}.")


if __name__ == "__main__":
    main()
