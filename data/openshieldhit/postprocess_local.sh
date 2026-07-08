#!/usr/bin/env bash
set -euo pipefail

exe="$(command -v convertmc 2>/dev/null || command -v convertmc.exe 2>/dev/null || echo "$HOME/convertmc")"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$root/../.." && pwd)"
render_diff_script="$repo_root/tools/render_diff_results.py"
THREADS="${THREADS:-11}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$root/.matplotlib}"
mkdir -p "$MPLCONFIGDIR"

shopt -s nullglob
summary_file="$(mktemp)"
trap 'rm -f "$summary_file"' EXIT

run() {
    printf '  +'
    printf ' %q' "$@"
    printf '\n'
    "$@"
}

run_checked() {
    if ! run "$@"; then
        echo "  Command failed; continuing with remaining files and plans." >&2
        return 1
    fi
    return 0
}

run_plotdata_checked() {
    local bdo="$1"
    local stem before_snapshot after_snapshot

    stem="$(basename "$bdo" .bdo)"
    before_snapshot="$(
        find . -maxdepth 1 -type f -name "${stem}*.dat" -printf '%f %TY%Tm%Td%TH%TM%TS %s\n' 2>/dev/null | sort
    )"

    if run "$exe" plotdata --many "$bdo"; then
        return 0
    fi

    after_snapshot="$(
        find . -maxdepth 1 -type f -name "${stem}*.dat" -printf '%f %TY%Tm%Td%TH%TM%TS %s\n' 2>/dev/null | sort
    )"

    # Current pymchelper plotdata writes files successfully but still exits
    # non-zero for multi-page outputs. Treat changed output files as success.
    if [[ -n "$after_snapshot" && "$after_snapshot" != "$before_snapshot" ]]; then
        echo "  plotdata returned non-zero but produced updated .dat files; continuing." >&2
        return 0
    fi

    echo "  Command failed; continuing with remaining files and plans." >&2
    return 1
}

resolve_input_dir() {
    local arg="$1"
    if [[ -d "$arg" ]]; then
        cd "$arg" && pwd
    elif [[ -d "$root/$arg" ]]; then
        cd "$root/$arg" && pwd
    elif [[ -d "$root/input/$arg" ]]; then
        cd "$root/input/$arg" && pwd
    else
        echo "No such input directory: $arg" >&2
        return 1
    fi
}

process_one() {
    local input_dir="$1"
    local plan results_dir
    local local_errors=0 processed=0 skipped=0 moved_png=0 moved_dat=0
    shopt -s nullglob

    [[ -d "$input_dir" ]] || return 0

    plan="$(basename "$input_dir")"
    results_dir="$root/results/$plan"

    echo
    echo "== Processing: input/$plan =="

    local bdo_files=( "$input_dir"/*.bdo )
    if [[ ${#bdo_files[@]} -eq 0 ]]; then
        echo "  No .bdo files found, skipping."
        skipped=1
        printf '%s %s %s %s %s\n' "$local_errors" "$processed" "$skipped" "$moved_png" "$moved_dat" >> "$summary_file"
        return 0
    fi
    processed=1

    mkdir -p "$results_dir"
    cd "$input_dir"

    echo "  Generating images..."
    run_checked "$exe" image --many "*.bdo" || local_errors=1

    # OpenShieldHIT currently does not support the large 2D ASCII plotdata
    # outputs well, so keep them as images only.
    echo "  Generating plotdata..."
    for bdo in ./*.bdo; do
        case "$(basename "$bdo")" in
            NB_XY*.bdo|NB_XZ_map*.bdo|NB_target.bdo|NB_target_water.bdo)
                # 2D maps: kept as images only (too large for ASCII plotdata)
                # target scalars: handled below by convertmc txt
                ;;
            *)
                run_plotdata_checked "$bdo" || local_errors=1
                ;;
        esac
    done

    # Extract per-page scalar text files for the target scorers.
    # "plotdata" produces a merged .dat unsuitable for the scalar comparison;
    # "txt" produces NB_target_p*.txt files (page numbering depends on the
    # convertmc version) which match the SH12A output format and are
    # referenced in manifest output_type entries.
    echo "  Generating text output for target scorers..."
    for bdo in NB_target.bdo NB_target_water.bdo; do
        [[ -f "$bdo" ]] || continue
        run_checked "$exe" txt "$bdo" || local_errors=1
    done

    local png_files=( NB*.png )
    local dat_files=( NB*.dat )
    local txt_files=( NB_target_p*.txt NB_target_water_p*.txt )

    if [[ ${#png_files[@]} -gt 0 ]]; then
        moved_png=${#png_files[@]}
        run_checked mv -v "${png_files[@]}" "$results_dir"/ || local_errors=1
    fi

    if [[ ${#dat_files[@]} -gt 0 ]]; then
        moved_dat=${#dat_files[@]}
        run_checked mv -v "${dat_files[@]}" "$results_dir"/ || local_errors=1
    fi

    if [[ ${#txt_files[@]} -gt 0 ]]; then
        run_checked mv -v "${txt_files[@]}" "$results_dir"/ || local_errors=1
    fi

    if [[ -f "$render_diff_script" ]]; then
        run_checked python3 "$render_diff_script" \
            --results-dir "$results_dir" \
            --input-root "$root/input" || local_errors=1
    fi

    printf '%s %s %s %s %s\n' "$local_errors" "$processed" "$skipped" "$moved_png" "$moved_dat" >> "$summary_file"
}

input_dirs=()
if [[ $# -eq 0 ]]; then
    # Default: process every local OpenShieldHIT input directory.
    input_dirs=( "$root"/input/plan* )
else
    # Optional args may be plan names, paths relative to this directory, or
    # paths relative to the caller's current working directory.
    for arg in "$@"; do
        input_dirs+=( "$(resolve_input_dir "$arg")" )
    done
fi

has_parallel=0
if command -v parallel >/dev/null 2>&1; then
    has_parallel=1
fi

export exe root render_diff_script summary_file
export -f run run_checked run_plotdata_checked process_one

if [[ ${#input_dirs[@]} -gt 1 && "$THREADS" -gt 1 && "$has_parallel" -eq 1 ]]; then
    printf "%s\n" "${input_dirs[@]}" | parallel -j"$THREADS" process_one {}
else
    for input_dir in "${input_dirs[@]}"; do
        process_one "$input_dir"
    done
fi

read -r had_errors processed_plans skipped_plans moved_png moved_dat < <(
    awk '{e+=($1>0); p+=$2; s+=$3; png+=$4; dat+=$5} END {print e+0, p+0, s+0, png+0, dat+0}' "$summary_file"
)

echo
echo "== Summary =="
echo "  Processed plans: $processed_plans"
echo "  Skipped plans:   $skipped_plans"
echo "  Moved PNG files: $moved_png"
echo "  Moved DAT files: $moved_dat"

exit "$had_errors"
