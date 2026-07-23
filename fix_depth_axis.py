#!/usr/bin/env python3
"""
fix_depth_axis.py

One-off correction for the depth column (1st column) of already-extracted
depth_Z.*.mat / depth_Z.*.H2O files, for plans whose result files were
generated using the wrong-direction/wrong-offset shared formula. Verified
against the actual MCNP input decks (surface 400 position + trcl direction)
for plan01/plan02/plan03 - see conversation this came from for the derivation.

Does NOT touch extract_tallies.sh or any of the other pipeline scripts, and
does NOT re-run any extraction - it transforms the depth values already
written to disk, in place.

Usage:
    python3 fix_depth_axis.py <result_dir> negate
    python3 fix_depth_axis.py <result_dir> affine <constant>

    negate:          new_depth = -old_depth              (plan01)
    affine <const>:  new_depth = <const> - old_depth      (plan02, const=8.0)

Only touches files matching depth_Z.*.mat / depth_Z.*.H2O (3 columns:
depth value error) in <result_dir>. target.*, xy_map.dat/xz_map.dat, and
spectrum_target.* files have no depth column and are left untouched.
"""
import glob
import sys
from pathlib import Path


def fix_file(path, transform):
    lines_out = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 3:
                print(f"warning: {path}: unexpected line format, left as-is: {line!r}",
                      file=sys.stderr)
                lines_out.append(line)
                continue
            depth, val, err = parts
            new_depth = transform(float(depth))
            lines_out.append(f"{new_depth:g} {val} {err}")
    with open(path, "w") as f:
        f.write("\n".join(lines_out) + "\n")
    print(f"fixed: {path}")


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    result_dir = Path(sys.argv[1])
    mode = sys.argv[2]

    if mode == "negate":
        transform = lambda d: -d
    elif mode == "affine":
        if len(sys.argv) < 4:
            print("error: affine mode requires a constant argument", file=sys.stderr)
            sys.exit(1)
        const = float(sys.argv[3])
        transform = lambda d: const - d
    else:
        print(f"error: unknown mode '{mode}' - use 'negate' or 'affine'", file=sys.stderr)
        sys.exit(1)

    targets = sorted(
        glob.glob(str(result_dir / "depth_Z.*.mat")) +
        glob.glob(str(result_dir / "depth_Z.*.H2O"))
    )
    if not targets:
        print(f"error: no depth_Z.*.mat / depth_Z.*.H2O files found in {result_dir}",
              file=sys.stderr)
        sys.exit(1)

    for path in targets:
        fix_file(path, transform)

    print(f"\nDone. Fixed {len(targets)} file(s) in {result_dir}.")


if __name__ == "__main__":
    main()
