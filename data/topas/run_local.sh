#!/usr/bin/env bash
#
# Run TOPAS locally at (fairly low) statistics, mirroring data/sh12a/run_local.sh.
#
# TOPAS must be launched from the repository root, because each main_*.txt uses
# repo-root-relative includeFile paths (e.g. data/topas/input/<plan>/beam_*.txt).
# Statistics are controlled at beam-generation time via tools/make_topas.sh (-N /
# NSTAT, baked into the beam file's REQUESTED_HISTORIES); this runner does not
# override them.
#
# Usage:
#   data/topas/run_local.sh                       # run every main_*.txt under input/plan*
#   data/topas/run_local.sh plan02_field01_geoD_mono
#   TOPAS_EXE=/path/to/topas THREADS=4 data/topas/run_local.sh
#
set -euo pipefail

EXE="${TOPAS_EXE:-${EXE:-topas}}"
THREADS="${THREADS:-4}"
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
    echo
    echo "== Running: ${main#$repo_root/} =="
    ( cd "$repo_root" && "$EXE" "${main#$repo_root/}" )
}
export EXE repo_root
export -f run_one

# Collect main_*.txt files from the requested (or all) input dirs.
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
    for m in "$d"/main_*.txt; do mains+=( "$m" ); done
done

if [[ ${#mains[@]} -eq 0 ]]; then
    echo "No main_*.txt files found (TODO stubs are skipped)." >&2
    exit 1
fi

if command -v parallel >/dev/null 2>&1 && [[ ${#mains[@]} -gt 1 && "$THREADS" -gt 1 ]]; then
    printf '%s\n' "${mains[@]}" | parallel -j"$THREADS" run_one {}
else
    for m in "${mains[@]}"; do run_one "$m"; done
fi
