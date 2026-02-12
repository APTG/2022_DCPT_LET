#!/usr/bin/env bash
set -u -o pipefail  # no -e: don't abort whole script on one failing conversion

# Enable shell tracing if you run: DEBUG=1 ./postprocess.sh
if [[ "${DEBUG:-0}" == "1" ]]; then
  set -x
fi

exe="$HOME/convertmc"

# basenames for 1-d plots
bplot="NB_Z_narrow_dose NB_Z_narrow_dose_water NB_Z_narrow_LET NB_Z_narrow_LET_water NB_Z_narrow_QEFF"
# basenames for images (2-d and 1-d)
bimg="NB_XY NB_XZ ${bplot}"
# basenames for text
btxt="NB_target"

td="$(pwd)"  # directory where command was started from

# Print a useful message if something *does* go wrong unexpectedly
trap 'echo "ERROR: command failed (exit $?): $BASH_COMMAND" >&2' ERR

# helper: check if any files match <basename>*.bdo in the current dir
have_bdo() {
  compgen -G "$1" >/dev/null
}

run_many() {
  local mode="$1"      # image | plotdata | txt
  local base="$2"      # e.g. NB_XY
  local pat="${base}*.bdo"

  if ! have_bdo "$pat"; then
    echo "  skip: no files match \"$pat\""
    return 0
  fi

  echo "  convert \"${base}*bdo\" -> ${mode}"
  # IMPORTANT: pass the glob pattern as ONE argument (convertmc handles it)
  if ! "$exe" "$mode" --many "${base}*bdo"; then
    echo "  WARN: convertmc failed for mode=$mode base=$base (continuing)" >&2
    return 0
  fi
}

for dir in input/plan*; do
  [[ -d "$dir" ]] || continue
  echo
  echo "== Plan dir: $dir =="

  # Latest run_* directory (lexicographic; works well for run_YYYYMMDD_HHMMSS)
  runs=( "$dir"/run_* )
  if [[ ${#runs[@]} -eq 0 ]]; then
    echo "  No run_* directories found (skipping)"
    continue
  fi
  ed="${runs[-1]}"

  od="$ed/output"
  rdd="$(basename "$dir")"
  rd="results/$rdd"

  echo "  Latest run: $ed"
  echo "  Output dir: $od"
  echo "  Result dir: $rd"

  if [[ ! -d "$od" ]]; then
    echo "  Missing output dir (skipping)"
    continue
  fi

  mkdir -p "$rd"

  pushd "$od" >/dev/null

  # images
  for b in $bimg; do
    run_many image "$b"
  done

  # plotdata
  for b in $bplot; do
    run_many plotdata "$b"
  done

  # text
  for b in $btxt; do
    run_many txt "$b"
  done

  # copy results into results/<plan...>/
  # (copy only if matches exist; no errors if none)
  shopt -s nullglob
  pngs=( NB*.png )
  dats=( NB*.dat )
  txts=( NB*.txt )
  shopt -u nullglob

  echo "  Copying: ${#pngs[@]} png, ${#dats[@]} dat, ${#txts[@]} txt -> $td/$rd/"
  ((${#pngs[@]})) && cp -v "${pngs[@]}" "$td/$rd/"
  ((${#dats[@]})) && cp -v "${dats[@]}" "$td/$rd/"
  ((${#txts[@]})) && cp -v "${txts[@]}" "$td/$rd/"

  popd >/dev/null
done

echo
echo "Done."
