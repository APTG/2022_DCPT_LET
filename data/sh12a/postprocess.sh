#!/usr/bin/env bash
set -euo pipefail

exe="$HOME/convertmc"

# basenames for 1-d plots
bplot="NB_Z_narrow_dose NB_Z_narrow_dose_water NB_Z_narrow_LET NB_Z_narrow_LET_water NB_Z_narrow_QEFF"
# basenames for images (2-d and 1-d)
bimg="NB_XY NB_XZ ${bplot}"
# basenames for text
btxt="NB_target"

td="$(pwd)"  # directory where command was started from

# If globs don't match, expand to nothing (prevents cp errors)
shopt -s nullglob

for dir in input/plan*; do
    [[ -d "$dir" ]] || continue
    echo

    # Latest run_* directory (lexicographically sorted)
    runs=( "$dir"/run_* )
    [[ ${#runs[@]} -gt 0 ]] || { echo "No run_* directories in: $dir (skipping)"; continue; }
    ed="${runs[-1]}"

    od="$ed/output"
    rdd="$(basename "$dir")"
    rd="results/$rdd"

    mkdir -p "$rd"

    echo "$od"
    [[ -d "$od" ]] || { echo "Missing output dir: $od (skipping)"; continue; }

    pushd "$od" >/dev/null

    # IMPORTANT: keep the glob INSIDE the quotes so convertmc receives ONE pattern argument
    for b in $bimg; do
        echo "  convert \"${b}*bdo\" to image files"
        "$exe" image --many "${b}*bdo"
    done

    for b in $bplot; do
        echo "  convert \"${b}*bdo\" to plotdata files"
        "$exe" plotdata --many "${b}*bdo"
    done

    for b in $btxt; do
        echo "  convert \"${b}*bdo\" to text files"
        "$exe" txt --many "${b}*bdo"
    done

    # copy results into results/<plan...>/
    cp -v NB*.png NB*.dat NB*.txt "$td/$rd/" 2>/dev/null || true

    popd >/dev/null
done
