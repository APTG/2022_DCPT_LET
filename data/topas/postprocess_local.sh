#!/usr/bin/env bash
#
# Thin wrapper around postprocess_local.py, matching the sh12a/osh entry-point
# convention. Converts local TOPAS CSV output into the shared depth-profile .dat
# files and writes VERSION.txt. See postprocess_local.py for details.
#
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$root/postprocess_local.py" "$@"
