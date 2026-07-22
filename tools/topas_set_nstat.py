#!/usr/bin/env python3
"""Create a TOPAS main.txt with an optional runtime NSTAT override.

dicomexportplan writes spot-wise histories into Tf/spotWeight/Values. To change
the run statistics after export, rescale that vector and update the header used
by post-processing for dose/fluence normalization.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path


SPOT_WEIGHT_RE = re.compile(
    r"^(?P<prefix>\s*uv:Tf/spotWeight/Values\s*=\s*)"
    r"(?P<count>\d+)"
    r"(?P<values>(?:\s+[-+0-9.eE]+)+)"
    r"(?P<suffix>\s*)$",
    re.MULTILINE,
)


def requested_histories(text: str) -> int:
    match = re.search(r"REQUESTED_HISTORIES:\s*(\d+)", text)
    if not match:
        raise SystemExit("Could not find REQUESTED_HISTORIES in TOPAS main")
    return int(match.group(1))


def rescale_integer_weights(values: list[int], target_sum: int) -> list[int]:
    current_sum = sum(values)
    if current_sum <= 0:
        raise SystemExit("Tf/spotWeight/Values has zero total histories")

    scaled = [value * target_sum / current_sum for value in values]
    floored = [math.floor(value) for value in scaled]
    remainder = target_sum - sum(floored)

    if remainder > 0:
        order = sorted(
            range(len(values)),
            key=lambda i: (scaled[i] - floored[i], values[i]),
            reverse=True,
        )
        for i in order[:remainder]:
            floored[i] += 1
    elif remainder < 0:
        order = sorted(range(len(values)), key=lambda i: (scaled[i] - floored[i], values[i]))
        need = -remainder
        for i in order:
            if need == 0:
                break
            if floored[i] > 0:
                floored[i] -= 1
                need -= 1
        if need:
            raise SystemExit("Could not reduce spot weights to requested NSTAT")

    return floored


def patch_text(text: str, nstat: int | None) -> tuple[str, int]:
    effective_nstat = requested_histories(text) if nstat is None else nstat
    if effective_nstat <= 0:
        raise SystemExit("NSTAT must be a positive integer")

    match = SPOT_WEIGHT_RE.search(text)
    if not match:
        raise SystemExit("Could not find uv:Tf/spotWeight/Values in TOPAS main")

    count = int(match.group("count"))
    values = [int(float(value)) for value in match.group("values").split()]
    if count != len(values):
        print(
            f"warning: spotWeight count says {count}, but found {len(values)} values",
            file=sys.stderr,
        )

    new_values = values if nstat is None else rescale_integer_weights(values, effective_nstat)
    replacement = f"{match.group('prefix')}{len(new_values)} {' '.join(str(v) for v in new_values)}{match.group('suffix')}"
    text = text[: match.start()] + replacement + text[match.end() :]

    text = re.sub(
        r"(REQUESTED_HISTORIES:\s*)\d+",
        rf"\g<1>{effective_nstat}",
        text,
        count=1,
    )

    total_match = re.search(r"TOTAL_NUMBER_OF_PARTICLES:\s*(\d+)", text)
    if total_match:
        particle_scaling = int(total_match.group(1)) / effective_nstat
        text = re.sub(
            r"(PARTICLE_SCALING:\s*)[-+0-9.eE]+",
            rf"\g<1>{particle_scaling:.12g}",
            text,
            count=1,
        )

    return text, effective_nstat


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source TOPAS main.txt")
    parser.add_argument("output", type=Path, help="Patched TOPAS main.txt to write")
    parser.add_argument("--nstat", type=int, help="Target total histories for this run")
    parser.add_argument("--history-file", type=Path, help="Write effective history count here")
    args = parser.parse_args()

    text, effective_nstat = patch_text(args.input.read_text(), args.nstat)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    if args.history_file:
        args.history_file.parent.mkdir(parents=True, exist_ok=True)
        args.history_file.write_text(f"{effective_nstat}\n")

    if args.nstat is not None:
        zero_count = 0
        match = SPOT_WEIGHT_RE.search(text)
        if match:
            zero_count = sum(1 for value in match.group("values").split() if int(float(value)) == 0)
        message = f"  runtime NSTAT: {effective_nstat}"
        if zero_count:
            message += f" ({zero_count} spots rounded to zero histories)"
        print(message)


if __name__ == "__main__":
    main()
