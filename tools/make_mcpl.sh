#!/usr/bin/env bash
set -euo pipefail

exe="dicomexportplan"
path_bm="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
dir_plan="data/resources/plans"
manifest="src/plan_manifest.txt"

outdir="mcpl"
mkdir -p "$outdir"

NSTAT=100000000

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" || "$rel" =~ ^[[:space:]]*# ]] && continue

  fin="${dir_plan}/${rel}"

  # use directory name as basename
  basedir="$(dirname "$rel")"
  base="${basedir//\//_}"

  fout="${outdir}/${base}.mcpl"

  set -o xtrace
  "$exe" "$fin" "$fout" \
      -b "$path_bm" \
      --export-fmt mcpl \
      -N "$NSTAT" \
      -v
  { set +o xtrace; } 2>/dev/null

done < "$manifest"
