#!/usr/bin/env python3
"""Validate all manifest.json files found under data/ against the manifest schema.

Checks performed for each manifest:
  1. Valid JSON
  2. Schema conformance (jsonschema draft-07)
  3. 'plan' field matches the manifest's parent directory name
  4. Every file listed in outputs[*].files[*].path exists relative to the manifest
  5. Every output_type referenced in outputs[*].files[*].output_type is a known catalog key
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data"),
        help="Root directory to search for manifest.json files (default: data).",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parent / "manifest.schema.json",
        help="Path to manifest.schema.json (default: tools/manifest.schema.json).",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("data") / "output_catalog.json",
        help="Path to output_catalog.json (default: data/output_catalog.json).",
    )
    return parser.parse_args()


def load_catalog(catalog_path: Path) -> set[str] | None:
    if not catalog_path.exists():
        return None
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return set(data.get("output_types", {}).keys())


def validate_manifest(
    manifest_path: Path,
    schema: dict,
    catalog_keys: set[str] | None,
) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        print("jsonschema is not installed. Run: pip install jsonschema", file=sys.stderr)
        sys.exit(1)

    errors: list[str] = []

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON: {exc}"]

    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: str(e.absolute_path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"schema [{path}]: {err.message}")

    plan_dir = manifest_path.parent
    declared_plan = data.get("plan")
    if declared_plan != plan_dir.name:
        errors.append(
            f"'plan' value '{declared_plan!r}' does not match directory name '{plan_dir.name}'"
        )

    for i, entry in enumerate(data.get("outputs", [])):
        entry_label = entry.get("description") or f"outputs[{i}]"
        for j, f in enumerate(entry.get("files", [])):
            path = f.get("path", "") if isinstance(f, dict) else str(f)
            if not path:
                errors.append(f"empty path at outputs[{i}].files[{j}]")
                continue
            if not (plan_dir / path).is_file():
                errors.append(f"missing file '{path}' (output: {entry_label})")
            output_type = f.get("output_type") if isinstance(f, dict) else None
            if output_type and catalog_keys is not None and output_type not in catalog_keys:
                errors.append(
                    f"unknown output_type '{output_type}' in '{path}' (output: {entry_label})"
                )

    return errors


def main() -> int:
    args = parse_args()

    schema_path = args.schema.resolve()
    if not schema_path.exists():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        return 1
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    catalog_keys = load_catalog(args.catalog)
    if catalog_keys is None:
        print(f"Warning: catalog not found at '{args.catalog}', skipping output_type checks.", file=sys.stderr)

    data_root = args.data_root
    manifests = sorted(data_root.rglob("manifest.json"))
    if not manifests:
        print(f"No manifest.json files found under '{data_root}'.")
        return 0

    total_errors = 0
    for manifest_path in manifests:
        errors = validate_manifest(manifest_path, schema, catalog_keys)
        label = manifest_path
        if errors:
            print(f"FAIL  {label}")
            for err in errors:
                print(f"      - {err}")
            total_errors += len(errors)
        else:
            print(f"ok    {label}")

    print(f"\n{len(manifests)} manifest(s) checked, {total_errors} error(s).")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
