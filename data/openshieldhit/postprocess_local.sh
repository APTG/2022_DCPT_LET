#!/usr/bin/env bash
set -euo pipefail

exe="$(command -v convertmc 2>/dev/null || command -v convertmc.exe 2>/dev/null || echo "$HOME/convertmc")"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
                run_checked "$exe" plotdata --many "$bdo"
                ;;
        esac
    done

    png_files=( NB*.png )
    dat_files=( NB*.dat )

    if [[ ${#png_files[@]} -gt 0 ]]; then
        ((moved_png += ${#png_files[@]}))
        run_checked mv -v "${png_files[@]}" "$results_dir"/
    fi

    if [[ ${#dat_files[@]} -gt 0 ]]; then
        ((moved_dat += ${#dat_files[@]}))
        run_checked mv -v "${dat_files[@]}" "$results_dir"/
    fi
done

echo
echo "== Summary =="
echo "  Processed plans: $processed_plans"
echo "  Skipped plans:   $skipped_plans"
echo "  Moved PNG files: $moved_png"
echo "  Moved DAT files: $moved_dat"

exit "$had_errors"
