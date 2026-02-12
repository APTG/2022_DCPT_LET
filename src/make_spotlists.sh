#!/usr/bin/env bash
set -euo pipefail

exe="dicomexportplan"
path_bm="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
dir_plan="data/resources/plans"
manifest="src/plan_manifest.txt"

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" || "$rel" =~ ^[[:space:]]*# ]] && continue

  fin="${dir_plan}/${rel}"
  outdir="$(dirname "$fin")"

  set -o xtrace
  "$exe" -b "$path_bm" --export-fmt spotlist -nc 7  "$fin" "${outdir}/spotlist_c7.dat"
  "$exe" -b "$path_bm" --export-fmt spotlist -nc 11 "$fin" "${outdir}/spotlist_c11.dat"
  { set +o xtrace; } 2>/dev/null
done < "$manifest"
