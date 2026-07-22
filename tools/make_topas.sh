#!/usr/bin/env bash
#
# Generate TOPAS beam input files for ALL plans directly from the DICOM plans,
# using dicomexport. Manifest-driven, exactly like tools/make_spotlists.sh.
#
# The generated file is BEAM-ONLY (source + spot time features, in the DICOM->IEC
# "nozzle" frame). It is geometry-independent, so it is written once per
# plan+field+beam-model into data/topas/input/beam/ and shared by every geometry
# variant's main.txt (which includeFile's it) -- the same "one source per plan"
# arrangement used for the SH12A/OSH spotlists.
#
# Coordinate convention: exported with --nozzle-side neg-z, the verified
# patient-correct IEC convention (source on the anterior side, beam travelling
# toward isocenter). See docs/coordinates.md. Never use pos-z for patient runs.
#
# Beam model per plan: v2 (50 cm upstream) for plans 01-04, v5 (60 cm) for 05-07.
#
# Requires dicomexport >= 1.4.4.
#
# Usage:
#   tools/make_topas.sh                 # regenerate beam files for all plans
#   NSTAT=1000000 tools/make_topas.sh   # override target protons (low-stat local default)
#
set -euo pipefail

exe="dicomexportplan"
required_version="1.4.4"
path_bm_v2="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
path_bm_v5="data/resources/dcpt_beam_model/DCPT_beam_model__v5.csv"
dir_plan="data/resources/plans"
plan_manifest="tools/plan_manifest.txt"
beam_out="data/topas/input/beam"

# Target protons for the (local, low-stat) simulation. Baked into the beam file's
# REQUESTED_HISTORIES / PARTICLE_SCALING. Bump for production runs.
NSTAT="${NSTAT:-1000000}"

command -v "$exe" >/dev/null 2>&1 || { echo "Error: '$exe' not found. Install dicomexport >= ${required_version}." >&2; exit 1; }

ver="$($exe --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"
if [[ -n "$ver" ]]; then
  lowest="$(printf '%s\n%s\n' "$required_version" "$ver" | sort -V | head -1)"
  [[ "$lowest" == "$required_version" ]] || echo "Warning: dicomexport $ver < required ${required_version}; regenerate with a newer version." >&2
fi

mkdir -p "$beam_out"

generated=0
while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" || "$rel" =~ ^[[:space:]]*# ]] && continue

  fin="${dir_plan}/${rel}"
  if [[ ! -f "$fin" ]]; then
    echo "skip: DICOM plan not found: $fin" >&2
    continue
  fi

  # Plan number from the manifest slug directory (e.g. plan03_ramp_full -> 03).
  slug="$(dirname "$rel")"
  nn="$(echo "$slug" | grep -oE '[0-9]+' | head -1)"
  [[ -n "$nn" ]] || { echo "skip: cannot parse plan number from '$slug'" >&2; continue; }

  # Beam model(s) + upstream plane per plan number. Plans 05-07 are v5-only.
  # Plans 01-04 use v2 for the committed mains/results, but we ALSO export v5 so
  # users can run the v5 variant themselves without regenerating from DICOM.
  models=()
  if (( 10#$nn >= 5 )); then
    models+=("v5 $path_bm_v5 600.0")
  else
    models+=("v2 $path_bm_v2 500.0")
    models+=("v5 $path_bm_v5 600.0")
  fi

  for m in "${models[@]}"; do
    read -r bm_label bm_csv bm_plane <<<"$m"
    # dicomexport exports every field and appends _field0N.txt to the base name.
    out_base="${beam_out}/plan${nn}_${bm_label}"

    set -o xtrace
    "$exe" -b "$bm_csv" -p="$bm_plane" -N "$NSTAT" \
        --export-fmt topas --nozzle-side neg-z \
        "$fin" "${out_base}.txt"
    { set +o xtrace; } 2>/dev/null
    generated=$((generated + 1))
  done
done < "$plan_manifest"

echo
echo "make_topas.sh: exported beam files for ${generated} plan(s) into ${beam_out}/."
echo "Each main.txt must includeFile the matching ${beam_out}/plan<NN>_<model>_field0N.txt."
