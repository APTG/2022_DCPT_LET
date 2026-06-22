#!/usr/bin/env bash
set -euo pipefail

exe="dicomexportplan"
path_bm_v2="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
path_bm_v5="data/resources/dcpt_beam_model/DCPT_beam_model__v5.csv"
dir_plan="data/resources/plans"
manifest="tools/plan_manifest.txt"

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" || "$rel" =~ ^[[:space:]]*# ]] && continue

  fin="${dir_plan}/${rel}"
  outdir="$(dirname "$fin")"

  set -o xtrace
  "$exe" -b "$path_bm_v2" -p=500.0 --export-fmt spotlist -nc 7  "$fin" "${outdir}/spotlist_BMv2_c7.dat"
  "$exe" -b "$path_bm_v2" -p=500.0 --export-fmt spotlist -nc 11 "$fin" "${outdir}/spotlist_BMv2_c11.dat"
  "$exe" -b "$path_bm_v5" -p=600.0 --export-fmt spotlist -nc 7  "$fin" "${outdir}/spotlist_BMv5_c7.dat"
  "$exe" -b "$path_bm_v5" -p=600.0 --export-fmt spotlist -nc 11 "$fin" "${outdir}/spotlist_BMv5_c11.dat"
  { set +o xtrace; } 2>/dev/null
done < "$manifest"
