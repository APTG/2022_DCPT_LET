#!/usr/bin/env bash
set -u -o pipefail

exe="$(command -v convertmc 2>/dev/null || command -v convertmc.exe 2>/dev/null || echo $HOME/convertmc)"

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
        files=( ${b}????.bdo )
        if [[ ${#files[@]} -eq 0 ]]; then
            # try non-suffixed filename (e.g. NB_XZ_map.bdo instead of NB_XZ_map_0001.bdo)
            nosuffix="${b%_}.bdo"
            [[ -f "$nosuffix" ]] && files=( "$nosuffix" )
        fi
        if [[ ${#files[@]} -gt 0 ]]; then
            echo "  convert \"${files[*]}\" to image files"
            "$exe" image --many "${files[@]}"
        fi
    done
    cd "$td"
    cp -v "$od"/NB*.png "$rd"/

    cd "$od"
    # generate plotdata (.dat)
    for b in $bplot; do
        files=( ${b}????.bdo )
        if [[ ${#files[@]} -eq 0 ]]; then
            nosuffix="${b%_}.bdo"
            [[ -f "$nosuffix" ]] && files=( "$nosuffix" )
        fi
        if [[ ${#files[@]} -gt 0 ]]; then
            echo "  convert \"${files[*]}\" to plotdata files"
            "$exe" plotdata --many "${files[@]}"
        fi
    done
    cd "$td"
    cp -v "$od"/NB*.dat "$rd"/

    cd "$od"
    # generate text results (.txt) for VOIs
    for b in $btxt; do
        files=( ${b}????.bdo )
        if [[ ${#files[@]} -eq 0 ]]; then
            nosuffix="${b%_}.bdo"
            [[ -f "$nosuffix" ]] && files=( "$nosuffix" )
        fi
        if [[ ${#files[@]} -gt 0 ]]; then
            echo "  convert \"${files[*]}\" to text files"
            "$exe" txt --many "${files[@]}"
        fi
    done
    cd "$td"
    cp -v "$od"/NB*.txt "$rd"/
done
