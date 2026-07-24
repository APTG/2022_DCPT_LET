#!/usr/bin/env bash
#
# extract_tallies.sh — extract tally results from an MCNP output (outp/outu)
# file into separate, named result files, derive LET-based metrics, derive
# water-equivalent quantities, and parse the companion 2D mesh dump.
#
# REQUIRES these five companion scripts in the SAME DIRECTORY as this one:
#   compute_let_metrics.py, water_equivalent.py, parse_mdata.py,
#   make_png_maps.py, compute_differential_spectra.py
# (Steps 3-7 below just invoke them; nothing is embedded in this file
# anymore. If you move this script, take all six files together.)
#
#   - depth_Z.DOSE.*     and depth_Z.FLUENCE.* : reduced to "depth value error"
#     one line per depth cell (400-604), depth = cell centre in cm.
#   - target.DOSE.all.mat                      : reduced to a single
#     "value error" line (the cell-union total over cells 500-504).
#   - depth_Z.{DLET,TLET,DQEFF,TQEFF}.{all,primary,protons}.mat and
#     target.{DLET,TLET,DQEFF,TQEFF}.{all,primary,protons}.mat : derived from
#     the LET spectra (native cell material), with propagated errors. The raw
#     LET-spectrum tally dumps themselves (formerly LET_Spectra / Target_LET)
#     are intermediate-only now - kept in a temp dir, not left in output_dir.
#   - depth_Z.{DOSE,DLET,TLET,DQEFF,TQEFF}.{primary,protons}.H2O : water-
#     equivalent depth quantities via Bragg-Gray conversion (protons/primary
#     only - not physically meaningful for the mixed-species "all" tally).
#   - target.{DLET,TLET}.{primary,protons}.H2O : water-equivalent target LET
#     only (target DOSE/DQEFF/TQEFF-in-water intentionally not produced).
#   - xy_map.dat / xz_map.dat                  : lateral / longitudinal 2D
#     mesh maps, parsed from the companion ".d" mesh-dump file (see below).
#   - spectrum_target.FLUENCE.all.mat.vs_DEDX, .primary.mat.vs_LET,
#     .primary.Si.vs_DEDX, .protons.mat.vs_EKIN : target differential
#     fluence spectra (see compute_differential_spectra.py for which
#     NB_target_diff.bdo pages these correspond to, and why the rest of
#     that table isn't produced here).
#
# 2D-map input file convention: the mesh dump file is expected to share the
# basename of the MCNP output file, with extension ".d" instead of ".o".
# e.g. output file "run03.o" -> mesh dump "run03.d" (same directory). If no
# such file is found, the 2D-map step is skipped with a warning (not fatal).
#
# Locale: LC_ALL/LC_NUMERIC are forced to "C" so awk and python always print
# numbers with a decimal POINT, regardless of the system locale.
#
# Usage:
#   ./extract_tallies.sh <mcnp_output_file> [output_dir]
#
# output_dir defaults to ./extracted_tallies
#
set -euo pipefail
export LC_ALL=C
export LC_NUMERIC=C

INFILE="${1:?Usage: $0 <mcnp_output_file> [output_dir]}"
OUTDIR="${2:-extracted_tallies}"

if [[ ! -f "$INFILE" ]]; then
    echo "error: input file '$INFILE' not found" >&2
    exit 1
fi

# companion 2D mesh-dump file: same basename as INFILE, extension .d instead
# of whatever INFILE's extension is (normally .o).
MDATA="${INFILE%.*}.d"

mkdir -p "$OUTDIR"
WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

# ---------------------------------------------------------------------------
# Step 1: split the whole output file into one chunk per tally, using the
# "1tally NNNN   nps = ..." header lines as block boundaries. Each chunk
# runs up to (but not including) the next "1tally" line.
#
# A single output file can contain results from several dumps (e.g. a
# restarted/continued run keeps appending new "1tally" print tables at
# later nps values). When the same tally number's header is seen again,
# the previously written chunk for that tally is closed and reopened in
# truncate mode, so only the LAST (most-converged, highest nps) dump's
# block for each tally survives - earlier dumps are discarded.
# ---------------------------------------------------------------------------
awk -v workdir="$WORKDIR" '
    /^1tally/ {
        num = $2
        if (num ~ /^[0-9]+$/) {
            f = workdir "/tally_" num ".txt"
            if (opened[num]) {
                close(f)   # force the next print to reopen (truncate),
            }              # discarding the earlier dump for this tally
            opened[num] = 1
            cur = f
        } else {
            cur = ""
        }
        if (cur != "") print > cur
        next
    }
    { if (cur != "") print > cur }
' "$INFILE"

# ---------------------------------------------------------------------------
# Step 2: parser for reduced-format tallies.
#   mode=simple  -> depth-cell tallies with a single value/error per cell
#                   (all/protons/deuterons/tritons/He3/alphas)
#   mode=primary -> depth-cell tallies split by "ft tag" into user bins;
#                   the "10000000000.00000" bin is taken as primary
#   mode=target  -> single "cell union total" value/error (500-504 combined)
# depth is the cell centre: 10.2 - 0.1 * (cell_number - 400)
# NOTE: sign flipped from the naive cell-index mapping so MCNP's depth
# axis orientation matches OSH/SH12A's convention (was mirrored before).
# ---------------------------------------------------------------------------
parse_tally() {
    local src="$1" mode="$2"
    awk -v mode="$mode" '
        BEGIN { cellnum=""; want=0 }
        /cell union total/ {
            if (mode == "target") want = 1
            next
        }
        /^ cell +[0-9]+/ {
            match($0, /[0-9]+/); cellnum = substr($0, RSTART, RLENGTH)
            if (mode == "simple") want = 1
            next
        }
        /user bin +10000000000\.00000/ {
            if (mode == "primary") want = 1
            next
        }
        /user bin +-1\.00000/ { if (mode == "primary") want = 0; next }
        /user bin total/      { if (mode == "primary") want = 0; next }
        {
            if (want && match($0, /[+-]?[0-9]+\.[0-9]+E[+-][0-9]+[ \t]+[0-9]+\.[0-9]+/)) {
                line = $0
                gsub(/^ +/, "", line)
                split(line, a, " ")
                val = a[1]; err = a[2]
                if (mode == "simple" || mode == "primary") {
                    depth = 10.2 - 0.1 * (cellnum - 400)
                    printf "%g %s %s\n", depth, val, err
                } else if (mode == "target") {
                    printf "%s %s\n", val, err
                }
                want = 0
            }
        }
    ' "$src"
}

missing=()

extract_reduced() {
    local num="$1" dest="$2" mode="$3"
    local src="$WORKDIR/tally_${num}.txt"
    if [[ ! -s "$src" ]]; then
        missing+=("$num")
        return
    fi
    parse_tally "$src" "$mode" > "$OUTDIR/$dest"
}

extract_raw() {
    local num="$1" dest="$2" append="$3" destroot="${4:-$OUTDIR}"   # append: yes/no
    local src="$WORKDIR/tally_${num}.txt"
    if [[ ! -s "$src" ]]; then
        missing+=("$num")
        return
    fi
    if [[ "$append" == "no" ]]; then
        cat "$src" > "$destroot/$dest"
    else
        {
            echo ""
            echo "# ==================================================="
            echo "# tally $num"
            echo "# ==================================================="
            cat "$src"
        } >> "$destroot/$dest"
    fi
}

# --- depth dose (F16/26/36/46/56/66/76), reduced format --------------------
extract_reduced 16 depth_Z.DOSE.all.mat        simple
extract_reduced 26 depth_Z.DOSE.primary.mat    primary
extract_reduced 36 depth_Z.DOSE.protons.mat    simple
extract_reduced 46 depth_Z.DOSE.deuterons.mat  simple
extract_reduced 56 depth_Z.DOSE.tritons.mat    simple
extract_reduced 66 depth_Z.DOSE.he3.mat        simple
extract_reduced 76 depth_Z.DOSE.alphas.mat     simple

# --- depth fluence (F14/24/34/44/54/64/74), reduced format -----------------
extract_reduced 14 depth_Z.FLUENCE.all.mat        simple
extract_reduced 24 depth_Z.FLUENCE.primary.mat    primary
extract_reduced 34 depth_Z.FLUENCE.protons.mat    simple
extract_reduced 44 depth_Z.FLUENCE.deuterons.mat  simple
extract_reduced 54 depth_Z.FLUENCE.tritons.mat    simple
extract_reduced 64 depth_Z.FLUENCE.he3.mat        simple
extract_reduced 74 depth_Z.FLUENCE.alphas.mat     simple

# --- target dose (F116), reduced to a single value/error line --------------
extract_reduced 116 target.DOSE.all.mat target

# --- LET spectra, kept only as WORKDIR temp files (NOT copied to $OUTDIR) --
# These are intermediate raw MCNP tally dumps consumed by the LET-metrics and
# water-equivalent steps below; they are intentionally not left behind in the
# extracted-results directory (removed per request).
rm -f "$WORKDIR/LET_Spectra"
extract_raw 1004 LET_Spectra no "$WORKDIR"
extract_raw 8104 LET_Spectra yes "$WORKDIR"
extract_raw 8204 LET_Spectra yes "$WORKDIR"

rm -f "$WORKDIR/Target_LET"
extract_raw 8004 Target_LET no "$WORKDIR"
extract_raw 9104 Target_LET yes "$WORKDIR"
extract_raw 9204 Target_LET yes "$WORKDIR"

echo "Done with tally extraction. Files written to: $OUTDIR"
if [[ ${#missing[@]} -gt 0 ]]; then
    printf 'warning: tally block(s) not found in input (not printed / run did not reach them): %s\n' "${missing[*]}" >&2
fi

# ---------------------------------------------------------------------------
# Steps 3-6: LET metrics, water-equivalent metrics, 2D mesh parsing, and PNG
# map rendering are each a standalone script living alongside this one
# (compute_let_metrics.py, water_equivalent.py, parse_mdata.py,
# make_png_maps.py) rather than embedded here, to keep this file readable.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_step() {
    # run_step <description> <script> [args...]
    local desc="$1" script="$2"
    shift 2
    if ! command -v python3 >/dev/null 2>&1; then
        echo "error: python3 not found - skipping $desc" >&2
        return
    fi
    if [[ ! -f "$SCRIPT_DIR/$script" ]]; then
        echo "error: $SCRIPT_DIR/$script not found - skipping $desc" >&2
        return
    fi
    if python3 "$SCRIPT_DIR/$script" "$@"; then
        echo "Done with $desc. Files written to: $OUTDIR"
    else
        echo "warning: $desc failed (see above) - continuing" >&2
    fi
}

# Step 3: DLET/TLET/DQEFF/TQEFF, native medium
run_step "LET metrics (DLET/TLET/DQEFF/TQEFF)" compute_let_metrics.py \
    "$WORKDIR/LET_Spectra" "$WORKDIR/Target_LET" "$OUTDIR"

# Step 4: water-equivalent DOSE/DLET/TLET/DQEFF/TQEFF (protons/primary only;
# target DOSE/DQEFF/TQEFF-in-water intentionally not produced - see
# water_equivalent.py's process_target())
run_step "water-equivalent metrics" water_equivalent.py \
    "$WORKDIR/LET_Spectra" "$WORKDIR/Target_LET" "$OUTDIR"

# Step 5: parse the companion 2D mesh dump (xy_map.dat / xz_map.dat)
if [[ -f "$MDATA" ]]; then
    run_step "2D mesh parsing (xy_map.dat / xz_map.dat)" parse_mdata.py \
        "$MDATA" --outdir "$OUTDIR"
else
    echo "warning: no companion mesh dump file found at '$MDATA' (expected: same basename as '$INFILE' with extension .d) - skipping 2D mesh parsing" >&2
fi

# Step 6: render PNGs from the 2D maps (filenames must contain "XY"/"XZ" -
# see make_png_maps.py - so build_pages_site.py's preview-image grouping
# picks them up correctly)
if [[ -f "$OUTDIR/xy_map.dat" || -f "$OUTDIR/xz_map.dat" ]]; then
    run_step "PNG map generation" make_png_maps.py "$OUTDIR"
else
    echo "note: no xy_map.dat / xz_map.dat present - skipping PNG map generation" >&2
fi

# Step 7: target differential fluence spectra (subset of NB_target_diff.bdo
# that's physically derivable here - see compute_differential_spectra.py's
# docstring for exactly which pages and why the rest are excluded)
run_step "differential spectra" compute_differential_spectra.py \
    "$WORKDIR/Target_LET" "$OUTDIR"
