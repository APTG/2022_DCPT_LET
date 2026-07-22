#!/usr/bin/env bash
#
# Run TOPAS locally at (fairly low) statistics, mirroring data/sh12a/run_local.sh.
#
# TOPAS must be launched from the repository root, because main.txt files use
# repo-root-relative output paths and legacy mains may still use repo-root-relative
# includeFile paths. Runnable mains should be generated at high statistics to
# preserve spot-weight precision. By default this runner downscales to 1M
# histories for local checks. Set NSTAT to choose another runtime total; the
# runner rescales Tf/spotWeight/Values in a temporary main and writes the
# effective history count next to the scratch CSVs for post-processing.
#
# Usage:
#   data/topas/run_local.sh                       # run every main.txt under input/plan*
#   data/topas/run_local.sh plan02_field01_geoD_mono
#   NSTAT=10000000 TOPAS_EXE=/path/to/topas THREADS=4 data/topas/run_local.sh
#
set -euo pipefail

EXE="${TOPAS_EXE:-${EXE:-topas}}"
THREADS="${THREADS:-4}"
NSTAT="${NSTAT:-1000000}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # data/topas
repo_root="$(cd "$root/../.." && pwd)"

command -v "$EXE" >/dev/null 2>&1 || { echo "Error: TOPAS executable '$EXE' not found (set TOPAS_EXE)." >&2; exit 1; }

resolve_input_dir() {
    local arg="$1"
    if [[ -d "$arg" ]]; then cd "$arg" && pwd
    elif [[ -d "$root/input/$arg" ]]; then cd "$root/input/$arg" && pwd
    elif [[ -d "$root/$arg" ]]; then cd "$root/$arg" && pwd
    else echo "No such input directory: $arg" >&2; return 1; fi
}

run_one() {
    local main="$1"
    local plan; plan="$(basename "$(dirname "$main")")"
    # TOPAS does not create output directories; the main.txt writes its scorer CSVs
    # to data/topas/results/output/<plan>/ (untracked scratch, see .gitignore).
    mkdir -p "$repo_root/data/topas/results/output/$plan"
    local effective_main="$main"
    local history_file="$repo_root/data/topas/results/output/$plan/REQUESTED_HISTORIES"
    local runtime_dir="$repo_root/data/topas/results/output/$plan/.runtime"
    local runtime_main="$runtime_dir/main.txt"
    "$repo_root/tools/topas_set_nstat.py" "$main" "$runtime_main" --nstat "$NSTAT" --history-file "$history_file"
    effective_main="$runtime_main"
    echo
    echo "== Running: ${main#$repo_root/} =="
    ( cd "$repo_root" && "$EXE" "${effective_main#$repo_root/}" )
}
export EXE repo_root NSTAT
export -f run_one

# Collect main.txt files from the requested (or all) input dirs.
input_dirs=()
if [[ $# -eq 0 ]]; then
    shopt -s nullglob
    input_dirs=( "$root"/input/plan*_field*_geo* )
else
    for arg in "$@"; do input_dirs+=( "$(resolve_input_dir "$arg")" ); done
fi

mains=()
for d in "${input_dirs[@]}"; do
    [[ -d "$d" ]] || continue
    shopt -s nullglob
    for m in "$d"/main*.txt; do mains+=( "$m" ); done
done

if [[ ${#mains[@]} -eq 0 ]]; then
    echo "No main.txt files found (TODO stubs are skipped)." >&2
    exit 1
fi

if command -v parallel >/dev/null 2>&1 && [[ ${#mains[@]} -gt 1 && "$THREADS" -gt 1 ]]; then
    printf '%s\n' "${mains[@]}" | parallel -j"$THREADS" run_one {}
else
    for m in "${mains[@]}"; do run_one "$m"; done
fi
