#!/usr/bin/env python3
"""Generate VERSION.txt provenance from one or more FLUKA output files."""

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import List


VERSION_RE = re.compile(r"FLUKA Version\s+(\S+)")
PRIMARIES_RE = re.compile(
    r"Total number of primaries run:\s*([0-9]+)"
)


def read_metadata(path: Path):
    text = path.read_text(errors="replace")

    version_match = VERSION_RE.search(text)
    if version_match is None:
        raise RuntimeError(f"Could not find FLUKA version in {path}")

    primaries_match = PRIMARIES_RE.search(text)
    if primaries_match is None:
        raise RuntimeError(f"Could not find primary count in {path}")

    return version_match.group(1), int(primaries_match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fluka_outputs",
        nargs="+",
        type=Path,
        help="FLUKA .out files contributing to the exported results.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination VERSION.txt path.",
    )
    args = parser.parse_args()

    output_files: List[Path] = args.fluka_outputs

    missing = [path for path in output_files if not path.is_file()]
    if missing:
        for path in missing:
            print(f"Missing FLUKA output: {path}")
        return 1

    versions = set()
    total_primaries = 0

    for path in output_files:
        version, primaries = read_metadata(path)
        versions.add(version)
        total_primaries += primaries

    if len(versions) != 1:
        raise RuntimeError(
            "FLUKA outputs contain inconsistent versions: "
            + ", ".join(sorted(versions))
        )

    version = next(iter(versions))

    latest_mtime = max(path.stat().st_mtime for path in output_files)
    filedate = dt.datetime.fromtimestamp(latest_mtime).astimezone()

    version_text = (
        f"filedate: {filedate:%a, %d %b %Y %H:%M:%S %z}\n"
        f"mc_code_version: {version}\n"
        f"number_of_primaries: {total_primaries}\n"
        "normalization: per_primary\n"
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(version_text)

    print(f"Wrote: {args.output}")
    print(f"FLUKA version: {version}")
    print(f"Output files: {len(output_files)}")
    print(f"Total primaries: {total_primaries}")
    print()
    print(version_text, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
