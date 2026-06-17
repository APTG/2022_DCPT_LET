#!/usr/bin/env bash
set -euo pipefail

exe="$(command -v convertmc 2>/dev/null || command -v convertmc.exe 2>/dev/null || echo "$HOME/convertmc")"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$root/../.." && pwd)"
render_diff_script="$repo_root/tools/render_diff_results.py"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$root/.matplotlib}"
mkdir -p "$MPLCONFIGDIR"

shopt -s nullglob
had_errors=0
processed_plans=0
skipped_plans=0
moved_png=0
moved_dat=0

# Print each high-level command before running it. This keeps the script
# readable while still showing the convertmc and move operations.
run() {
    printf '  +'
    printf ' %q' "$@"
    printf '\n'
    "$@"
}

run_checked() {
    if ! run "$@"; then
        echo "  Command failed; continuing with remaining files and plans." >&2
        had_errors=1
    fi
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
    had_errors=1
}

input_dirs=()
if [[ $# -eq 0 ]]; then
    # Default: process every local OpenShieldHIT input directory.
    input_dirs=( "$root"/input/plan* )
else
    # Optional args may be plan names, paths relative to this directory, or
    # paths relative to the caller's current working directory.
    for arg in "$@"; do
        if [[ -d "$arg" ]]; then
            input_dirs+=( "$(cd "$arg" && pwd)" )
        elif [[ -d "$root/$arg" ]]; then
            input_dirs+=( "$(cd "$root/$arg" && pwd)" )
        elif [[ -d "$root/input/$arg" ]]; then
            input_dirs+=( "$(cd "$root/input/$arg" && pwd)" )
        else
            echo "No such input directory: $arg" >&2
            exit 1
        fi
    done
fi

for input_dir in "${input_dirs[@]}"; do
    [[ -d "$input_dir" ]] || continue

    plan="$(basename "$input_dir")"
    results_dir="$root/results/$plan"

    echo
    echo "== Processing: input/$plan =="

    bdo_files=( "$input_dir"/*.bdo )
    if [[ ${#bdo_files[@]} -eq 0 ]]; then
        echo "  No .bdo files found, skipping."
        ((skipped_plans += 1))
        continue
    fi
    ((processed_plans += 1))

    mkdir -p "$results_dir"

    cd "$input_dir"

    echo "  Generating images..."
    run_checked "$exe" image --many "*.bdo"

    # OpenShieldHIT currently does not support the large 2D ASCII plotdata
    # outputs well, so keep them as images only.
    echo "  Generating plotdata..."
    for bdo in ./*.bdo; do
        case "$(basename "$bdo")" in
            NB_XY*.bdo|NB_XZ_map*.bdo)
                ;;
            *)
                run_plotdata_checked "$bdo"
                ;;
        esac
    done

    # Extract per-page scalar text files for the target scorers.
    # "plotdata" produces a merged .dat unsuitable for the scalar comparison;
    # "txt" produces NB_target_p01.txt … NB_target_pNN.txt which match the
    # SH12A output format and are referenced in manifest output_type entries.
    echo "  Generating text output for target scorers..."
    for bdo in NB_target.bdo NB_target_water.bdo; do
        [[ -f "$bdo" ]] || continue
        run_checked "$exe" txt "$bdo"
    done

    png_files=( NB*.png )
    dat_files=( NB*.dat )
    txt_files=( NB_target_p*.txt NB_target_water_p*.txt )

    if [[ ${#png_files[@]} -gt 0 ]]; then
        ((moved_png += ${#png_files[@]}))
        run_checked mv -v "${png_files[@]}" "$results_dir"/
    fi

    if [[ ${#dat_files[@]} -gt 0 ]]; then
        ((moved_dat += ${#dat_files[@]}))
        run_checked mv -v "${dat_files[@]}" "$results_dir"/
    fi

    if [[ ${#txt_files[@]} -gt 0 ]]; then
        run_checked mv -v "${txt_files[@]}" "$results_dir"/
    fi

    if [[ -f "$render_diff_script" ]]; then
        run_checked python3 "$render_diff_script" \
            --results-dir "$results_dir" \
            --input-root "$root/input"
    fi
done

echo
echo "== Summary =="
echo "  Processed plans: $processed_plans"
echo "  Skipped plans:   $skipped_plans"
echo "  Moved PNG files: $moved_png"
echo "  Moved DAT files: $moved_dat"

exit "$had_errors"
