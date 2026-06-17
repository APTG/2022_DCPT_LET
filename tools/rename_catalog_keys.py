#!/usr/bin/env python3
"""One-off migration: rename *.Si catalog keys to *.mat for non-spectrum entries.

The .Si suffix was incorrectly used for outputs where detect.dat has no
material specifier (scored to the actual transport medium = solid water +
PMMA).  After this rename:

  .mat  →  no material override; dose/LET to the actual transport medium
  .Si   →  explicit in_Si stopping-power setting  (spectrum_target only)
  .H2O  →  explicit in_Water stopping-power setting

Affected geometry prefixes: depth_Z, target, map_XZ, map_XY
Left unchanged: spectrum_target (already uses .Si correctly for in_Si spectra)

Modifies in-place:
  data/output_catalog.json
  data/**/manifest.json  (output_type values)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DATA_ROOT = Path("data")
CATALOG_PATH = DATA_ROOT / "output_catalog.json"

# Geometry prefixes where .Si means "no override" → rename to .mat
RENAME_GEOMETRIES = {"depth_Z", "target", "map_XZ", "map_XY"}


def build_rename_map(catalog: dict) -> dict[str, str]:
    """Return {old_key: new_key} for all keys that need renaming."""
    renames: dict[str, str] = {}
    for key in catalog["output_types"]:
        parts = key.split(".")
        geom = parts[0]
        if geom not in RENAME_GEOMETRIES:
            continue
        # key ends with .Si (possibly before .vs_*)
        # e.g. depth_Z.DOSE.all.Si  or  target.DLET.primary.Si
        if parts[-1] == "Si":
            new_key = ".".join(parts[:-1]) + ".mat"
            renames[key] = new_key
    return renames


def migrate_catalog(path: Path, renames: dict[str, str]) -> None:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    ot = catalog["output_types"]

    # Rebuild the output_types dict with renamed keys, preserving order
    new_ot: dict = {}
    for key, entry in ot.items():
        new_key = renames.get(key, key)
        new_entry = dict(entry)
        if key != new_key:
            new_entry["medium"] = "mat"
        new_ot[new_key] = new_entry

    # Update the description to reflect the new naming
    catalog["description"] = (
        "Canonical catalog of all physical output types in this benchmark. "
        "Key format: {geometry}.{QUANTITY}.{filter}.{medium}[.vs_{diff_axis}]. "
        "Medium suffix: 'mat' = no material override, scored to the actual transport "
        "medium (solid water + PMMA in this geometry); "
        "'Si' = explicit in_Si stopping-power setting (spectrum_target only); "
        "'H2O' = explicit in_Water stopping-power setting."
    )
    catalog["output_types"] = new_ot
    path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  updated catalog: {len(renames)} keys renamed")


def migrate_manifests(data_root: Path, renames: dict[str, str]) -> None:
    for mpath in sorted(data_root.rglob("manifest.json")):
        text = mpath.read_text(encoding="utf-8")
        original = text
        for old, new in renames.items():
            text = text.replace(f'"output_type": "{old}"', f'"output_type": "{new}"')
        if text != original:
            mpath.write_text(text, encoding="utf-8")
            # count replacements
            n = sum(
                original.count(f'"output_type": "{old}"')
                for old in renames
            )
            print(f"  updated {mpath.relative_to(data_root)}  ({n} references)")


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    renames = build_rename_map(catalog)
    print(f"Keys to rename: {len(renames)}")
    for old, new in sorted(renames.items()):
        print(f"  {old}  →  {new}")
    print()

    migrate_catalog(CATALOG_PATH, renames)
    migrate_manifests(DATA_ROOT, renames)
    print("\nDone. Run tools/validate_manifests.py to verify.")


if __name__ == "__main__":
    main()
