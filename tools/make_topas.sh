#!/usr/bin/env bash
#
# Generate TOPAS beam input files from the DICOM plans using dicomexport.
#
# Mirrors tools/make_spotlists.sh, but exports the TOPAS beam format
# (--export-fmt topas). The generated file is BEAM-ONLY (source + spot time
# features, in the DICOM->IEC "nozzle" frame); the phantom geometry and scoring
# live in the hand-maintained main_*.txt, which includeFile's the beam file.
#
# Coordinate convention: we export with --nozzle-side neg-z, the verified
# patient-correct IEC convention (source on the anterior side, beam travelling
# toward isocenter). See docs/coordinates.md. Do NOT use pos-z here: that mirror
# is only for non-patient research setups and would silently flip anthropomorphic
# anatomy.
#
# Requires dicomexport >= 1.4.4.
#
# Usage:
#   tools/make_topas.sh                 # regenerate beam files for all plans with a main_*.txt
#   NSTAT=1000000 tools/make_topas.sh   # override target protons (low-stat local default)
#
set -euo pipefail

exe="dicomexportplan"
required_version="1.4.4"
path_bm_v2="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
path_bm_v5="data/resources/dcpt_beam_model/DCPT_beam_model__v5.csv"
dir_plan="data/resources/plans"
plan_manifest="tools/plan_manifest.txt"
topas_input="data/topas/input"

# Target protons for the (local, low-stat) simulation. The beam file bakes this
# into REQUESTED_HISTORIES / PARTICLE_SCALING. Bump for production runs.
NSTAT="${NSTAT:-1000000}"

command -v "$exe" >/dev/null 2>&1 || { echo "Error: '$exe' not found. Install dicomexport >= ${required_version}." >&2; exit 1; }

# Soft version check (informational): dicomexport prints e.g. "1.4.4" or "1.4.3.post1+g...".
ver="$($exe --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"
if [[ -n "$ver" ]]; then
  lowest="$(printf '%s\n%s\n' "$required_version" "$ver" | sort -V | head -1)"
  [[ "$lowest" == "$required_version" ]] || echo "Warning: dicomexport $ver < required ${required_version}; regenerate with a newer version." >&2
fi

# Map plan number (NN) -> DICOM plan file, parsed from the plan manifest.
declare -A dcm_for_plan
while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" || "$rel" =~ ^[[:space:]]*# ]] && continue
  nn="$(basename "$rel" | grep -oE '^plan[0-9]+' | grep -oE '[0-9]+' || true)"
  # slug directory carries the plan number (plan01_sobp/RN....dcm)
  slug="$(dirname "$rel")"
  nn="$(echo "$slug" | grep -oE '[0-9]+' | head -1)"
  [[ -n "$nn" ]] && dcm_for_plan["$nn"]="${dir_plan}/${rel}"
done < "$plan_manifest"

# Beam model + upstream plane per plan number: v2 (50 cm) for plans 01-04,
# v5 (60 cm) for plans 05-07. See docs/coordinates.md and the beam-model README.
beam_model_for_plan() {  # -> "<label> <csv> <plane_mm>"
  local nn=$((10#$1))
  if (( nn >= 5 )); then
    echo "v5 ${path_bm_v5} 600.0"
  else
    echo "v2 ${path_bm_v2} 500.0"
  fi
}

shopt -s nullglob
generated=0
for main in "$topas_input"/plan*_field*_geo*/main_*.txt; do
  in_dir="$(dirname "$main")"
  dir_name="$(basename "$in_dir")"

  nn="$(echo "$dir_name" | grep -oE '^plan[0-9]+' | grep -oE '[0-9]+')"
  field="$(echo "$dir_name" | grep -oE 'field[0-9]+' | grep -oE '[0-9]+')"
  field="${field:-1}"

  dcm="${dcm_for_plan[$nn]:-}"
  if [[ -z "$dcm" || ! -f "$dcm" ]]; then
    echo "skip $dir_name: no DICOM plan for plan number $nn in $plan_manifest" >&2
    continue
  fi

  read -r bm_label bm_csv bm_plane <<<"$(beam_model_for_plan "$nn")"
  out_base="${in_dir}/beam_${bm_label}"   # dicomexport appends _field0N.txt

  set -o xtrace
  "$exe" -b "$bm_csv" -p="$bm_plane" -f "$field" -N "$NSTAT" \
      --export-fmt topas --nozzle-side neg-z \
      "$dcm" "${out_base}.txt"
  { set +o xtrace; } 2>/dev/null
  generated=$((generated + 1))
done

echo
echo "make_topas.sh: generated beam files for ${generated} main file(s)."
echo "Remember: main_*.txt must includeFile the generated beam_<model>_field0N.txt."
