#!/usr/bin/env bash
set -euo pipefail

EXE="${SHIELDHIT_EXE:-${EXE:-shieldhit}}"
THREADS="${THREADS:-11}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_one() {
    local input_dir="$1"
    shift || true

    echo
    echo "== Running: ${input_dir#$root/} =="
    (
        cd "$root"
        "$EXE" "$input_dir" "$@"
    )
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

input_args=()
extra_args=()
seen_separator=0
for arg in "$@"; do
    if [[ "$arg" == "--" && "$seen_separator" -eq 0 ]]; then
        seen_separator=1
        continue
    fi
    if [[ "$seen_separator" -eq 0 ]]; then
        input_args+=( "$arg" )
    else
        extra_args+=( "$arg" )
    fi
done

input_dirs=()
if [[ ${#input_args[@]} -eq 0 ]]; then
    input_dirs=( "$root"/input/plan* )
else
    for arg in "${input_args[@]}"; do
        input_dirs+=( "$(resolve_input_dir "$arg")" )
    done
fi

if [[ ${#input_dirs[@]} -eq 0 ]]; then
    echo "No input directories found." >&2
    exit 1
fi

export EXE root
export -f run_one

has_parallel=0
if command -v parallel >/dev/null 2>&1; then
    has_parallel=1
fi

if [[ ${#input_args[@]} -eq 0 && ${#input_dirs[@]} -gt 1 && "$THREADS" -gt 1 && "$has_parallel" -eq 1 ]]; then
    printf "%s\n" "${input_dirs[@]}" | parallel -j"$THREADS" run_one {} "${extra_args[@]}"
else
    for input_dir in "${input_dirs[@]}"; do
        run_one "$input_dir" "${extra_args[@]}"
    done
fi
