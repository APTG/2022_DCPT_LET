#!/usr/bin/env bash
set -u -o pipefail

exe="$HOME/convertmc"

# basenames for 1-d plots
bplot="NB_Z_narrow_dose_ NB_Z_narrow_dose_water_ NB_Z_narrow_LET_ NB_Z_narrow_LET_water_ NB_Z_narrow_QEFF_ NB_target_diff_ NB_target_water_diff_"
# basenames for images (2-d and 1-d)
bimg="NB_XY_ NB_XZ_map_ ${bplot}"
# basenames for text
btxt="NB_target_ NB_target_water_"

td="$(pwd)"  # directory where command was started from

# allow cp globs to expand to nothing without error
shopt -s nullglob

for dir in input/plan*; do
    [[ -d "$dir" ]] || continue
    echo
    echo "== Processing: $dir =="

    ed="$(ls -1 -d "$dir"/run_* 2>/dev/null | tail -1)"  # latest run dir only
    if [[ -z "${ed}" ]]; then
        echo "  No run_* directories found, skipping."
        continue
    fi

    od="$ed/output"
    rdd="$(basename "$dir")"
    rd="results/$rdd"

    mkdir -p "$rd"

    echo "  Run dir:    $ed"
    echo "  Output dir: $od"
    echo "  Results:    $rd"

    if [[ ! -d "$od" ]]; then
        echo "  Output directory missing, skipping."
        continue
    fi

    cd "$od"

    # generate PNG images
    for b in $bimg; do
        echo "  convert \"${b}????.bdo\" to image files"
        "$exe" image --many "${b}????.bdo"
    done
    cd "$td"
    cp -v "$od"/NB*.png "$rd"/

    cd "$od"
    # generate plotdata (.dat)
    for b in $bplot; do
        echo "  convert \"${b}????.bdo\" to plotdata files"
        "$exe" plotdata --many "${b}????.bdo"
    done
    cd "$td"
    cp -v "$od"/NB*.dat "$rd"/

    cd "$od"
    # generate text results (.txt) for VOIs
    for b in $btxt; do
        echo "  convert \"${b}????.bdo\" to text files"
        "$exe" txt --many "${b}????.bdo"
    done
    cd "$td"
    cp -v "$od"/NB*.txt "$rd"/
done
