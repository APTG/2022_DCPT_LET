#!/usr/bin/env bash
set -u -o pipefail

# Cluster postprocessing for OpenShieldHIT, fully analogous to
# data/sh12a/postprocess.sh. It assumes the same run layout as SH12A:
# each plan has input/<plan>/run_*/output/ holding the raw .bdo files.
# (OpenShieldHIT's HPC submission path is not finalised yet; adjust the
# run_*/output assumption here once the generatemc-based path exists.)

exe="$HOME/convertmc"

# basenames for 1-d plots
bplot="NB_Z_narrow_dose_ NB_Z_narrow_fluence_ NB_Z_narrow_dose_water_ NB_Z_narrow_LET_ NB_Z_narrow_LET_water_ NB_Z_narrow_QEFF_ NB_target_diff_ NB_target_water_diff_"
# basenames for images (2-d maps only; 1-d plots are handled online)
bimg="NB_XY_ NB_XZ_map_"
# basenames for text
btxt="NB_target_ NB_target_water_"

td="$(pwd)"  # directory where command was started from

# allow cp globs to expand to nothing without error
shopt -s nullglob

# Use command-line arguments if provided, otherwise default to input/plan*
if [ $# -gt 0 ]; then
    dirs=("$@")
else
    dirs=(input/plan*)
fi

for dir in "${dirs[@]}"; do
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

    # generate PNG images for 2D maps only
    for b in $bimg; do
        echo "  convert \"${b}????.bdo\" to image files"
        "$exe" image --many "${b}????.bdo"
    done
    cd "$td"
    cp -v "$od"/NB_XY*.png "$od"/NB_XZ_map*.png "$rd"/

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

    # Record provenance straight from the .bdo header (MC code version, primary
    # count, simulation date) plus the convertmc version used for extraction.
    # Mirrors the VERSION.txt writer in postprocess_local.sh so cluster runs
    # carry the same provenance consumed by manifest generation and plots.
    ref_bdo="$(ls -1 "$od"/*.bdo 2>/dev/null | head -1)"
    if [[ -n "$ref_bdo" ]]; then
        {
            "$exe" inspect "$ref_bdo" 2>/dev/null \
                | grep -E '^(mc_code_version|number_of_primaries|filedate)' \
                | sed 's/[[:space:]]*:[[:space:]]*/: /'
            printf 'convertmc_version: %s\n' "$("$exe" --version 2>/dev/null | head -1)"
        } > "$rd/VERSION.txt"
        echo "  Wrote $rd/VERSION.txt"
    fi
done
