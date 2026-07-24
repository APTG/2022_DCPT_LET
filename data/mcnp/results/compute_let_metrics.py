#!/usr/bin/env python3
"""
compute_let_metrics.py

Computes DLET, TLET, DQEFF and TQEFF (with propagated errors) per depth
cell (and as a single target scalar) from the LET-spectrum fluence data
in LET_Spectra / Target_LET.

Bin representative value: each LET bin's printed value L_i is its UPPER
edge. The representative value actually used in the sums below is
    E_i = average(L_i, L_{i+1})
matching the spreadsheet convention (=AVERAGE(B_i:B_{i+1})): the mean of
the bin's own upper edge and the NEXT bin's upper edge. The last bin has
no "next" edge (the row after it is the non-numeric "total" line, which
AVERAGE() ignores), so it just uses its own edge.

    TLET  = sum(Phi_i * E_i)        / sum(Phi_i)
    DLET  = sum(D_i   * E_i)        / sum(D_i)          , D_i = Phi_i * E_i
    TQEFF = sum(Phi_i * Q(E_i))     / sum(Phi_i)
    DQEFF = sum(D_i   * Q(E_i))     / sum(D_i)

Q(L) is the ICRP-60 quality-factor function, L in keV/um (tally L is in
MeV/cm, converted x0.1 only for evaluating Q):
    Q(L) = 1                    , L < 10
    Q(L) = 0.32*L - 2.2         , 10 <= L <= 100
    Q(L) = 300 / sqrt(L)        , L > 100

Error propagation: each quantity is a weighted average X = sum(w_i*V_i)/sum(w_i)
(TLET/TQEFF weighted by Phi_i, DLET/DQEFF weighted by D_i; V_i = E_i or Q_i).
    dX/dw_i = (V_i - X) / sum(w_j)
    sigma_X^2 = sum_i [ (V_i - X) / sum(w_j) ]^2 * sigma_w_i^2
with sigma_Phi_i = relerr_i * Phi_i and sigma_D_i = E_i * sigma_Phi_i.
"""
import locale
import math
import re
import sys
from pathlib import Path

locale.setlocale(locale.LC_NUMERIC, "C")

CELL_RE = re.compile(r'^\s*cell\s+(\d+)\s*$')
CELL_UNION_RE = re.compile(r'cell union total')
USERBIN_RE = re.compile(r'user bin\s+([\-0-9.]+)')
HEADER_RE = re.compile(r's\(e\)')
BIN_RE = re.compile(r'^\s*([\d.]+E[+-]\d+)\s+([\d.]+E[+-]\d+)\s+([\d.]+)\s*$')
TOTAL_RE = re.compile(r'^\s*total\s+([\d.]+E[+-]\d+)\s+([\d.]+)')
TALLY_MARKER_RE = re.compile(r'^# tally (\d+)')
TALLY_HEADER_RE = re.compile(r'^1tally\s+(\d+)')

PRIMARY_TAG_VALUE = 1.0e10


def split_tally_blocks(text):
    blocks = {}
    cur_num = None
    cur_lines = []
    for line in text.splitlines():
        m = TALLY_MARKER_RE.match(line) or TALLY_HEADER_RE.match(line)
        if m:
            if cur_num is not None:
                blocks[cur_num] = "\n".join(cur_lines)
            cur_num = m.group(1)
            cur_lines = []
            continue
        if cur_num is not None:
            cur_lines.append(line)
    if cur_num is not None:
        blocks[cur_num] = "\n".join(cur_lines)
    return blocks


def parse_spectra(block_text, use_primary_tag):
    results = {}
    current_cell = None
    capture = not use_primary_tag
    bins = []

    for line in block_text.splitlines():
        m = CELL_UNION_RE.search(line)
        if m:
            current_cell = 'total'
            capture = not use_primary_tag
            bins = []
            continue
        m = CELL_RE.match(line)
        if m:
            current_cell = m.group(1)
            capture = not use_primary_tag
            bins = []
            continue
        m = USERBIN_RE.search(line)
        if m:
            val = float(m.group(1))
            if use_primary_tag:
                capture = abs(val - PRIMARY_TAG_VALUE) < 1.0
                bins = []
            continue
        if HEADER_RE.search(line):
            continue
        m = BIN_RE.match(line)
        if m and capture:
            L = float(m.group(1))
            phi = float(m.group(2))
            relerr = float(m.group(3))
            bins.append((L, phi, relerr))
            continue
        m = TOTAL_RE.match(line)
        if m:
            if capture and current_cell is not None:
                results[current_cell] = bins
            continue

    return results


def q_icrp60(L_kev_um):
    if L_kev_um < 10.0:
        return 1.0
    elif L_kev_um <= 100.0:
        return 0.32 * L_kev_um - 2.2
    else:
        return 300.0 / math.sqrt(L_kev_um)


def weighted_avg_and_error(weights, sigma_weights, values):
    sum_w = sum(weights)
    if sum_w <= 0:
        return 0.0, 0.0
    x = sum(w * v for w, v in zip(weights, values)) / sum_w
    var = sum(((v - x) / sum_w) ** 2 * sw * sw
              for w, sw, v in zip(weights, sigma_weights, values))
    return x, math.sqrt(var)


def bin_representative_values(bins):
    """
    E_i = average(L_i, L_{i+1}) - matches the spreadsheet convention
    (=AVERAGE(B_i:B_{i+1})): each bin's representative LET value is the
    mean of its own upper edge and the NEXT bin's upper edge. The last
    bin has no "next" edge (the following row is the non-numeric
    "total" line, which AVERAGE() ignores), so it just uses its own
    upper edge, same as AVERAGE() would with a single numeric cell.
    """
    n = len(bins)
    L = [b[0] for b in bins]
    E = []
    for i in range(n):
        if i + 1 < n:
            E.append((L[i] + L[i + 1]) / 2.0)
        else:
            E.append(L[i])
    return E


def compute_metrics(bins):
    if not bins:
        zero = (0.0, 0.0)
        return {'DLET': zero, 'TLET': zero, 'DQEFF': zero, 'TQEFF': zero}

    E = bin_representative_values(bins)
    phi = [b[1] for b in bins]
    relerr = [b[2] for b in bins]
    sigma_phi = [r * p for r, p in zip(relerr, phi)]

    D = [p * e for p, e in zip(phi, E)]
    sigma_D = [e * sp for e, sp in zip(E, sigma_phi)]

    Q = [q_icrp60(e * 0.1) for e in E]

    tlet, sigma_tlet = weighted_avg_and_error(phi, sigma_phi, E)
    dlet, sigma_dlet = weighted_avg_and_error(D, sigma_D, E)
    tqeff, sigma_tqeff = weighted_avg_and_error(phi, sigma_phi, Q)
    dqeff, sigma_dqeff = weighted_avg_and_error(D, sigma_D, Q)

    return {
        'DLET': (dlet, sigma_dlet),
        'TLET': (tlet, sigma_tlet),
        'DQEFF': (dqeff, sigma_dqeff),
        'TQEFF': (tqeff, sigma_tqeff),
    }



def cell_depth(cell_num):
    return 10.2 - 0.1 * (int(cell_num) - 400)


def write_depth_file(path, per_cell_metrics, quantity):
    cells = sorted((c for c in per_cell_metrics if c != 'total'), key=int)
    with open(path, 'w') as f:
        for c in cells:
            depth = cell_depth(c)
            value, sigma = per_cell_metrics[c][quantity]
            f.write("{:g} {:.6E} {:.6E}\n".format(depth, value, sigma))


def write_target_file(path, metrics, quantity):
    value, sigma = metrics[quantity]
    with open(path, 'w') as f:
        f.write("{:.6E} {:.6E}\n".format(value, sigma))


def process_depth(let_spectra_text, particle, use_primary_tag, tally_num, outdir):
    blocks = split_tally_blocks(let_spectra_text)
    if tally_num not in blocks:
        print(f"warning: tally {tally_num} not found in LET_Spectra, "
              f"skipping depth_Z.*.{particle}.mat", file=sys.stderr)
        return
    spectra = parse_spectra(blocks[tally_num], use_primary_tag)
    per_cell_metrics = {c: compute_metrics(b) for c, b in spectra.items()}

    for quantity in ('DLET', 'TLET', 'DQEFF', 'TQEFF'):
        write_depth_file(outdir / f"depth_Z.{quantity}.{particle}.mat",
                          per_cell_metrics, quantity)


def process_target(target_let_text, particle, use_primary_tag, tally_num, outdir):
    blocks = split_tally_blocks(target_let_text)
    if tally_num not in blocks:
        print(f"warning: tally {tally_num} not found in Target_LET, "
              f"skipping target.*.{particle}.mat", file=sys.stderr)
        return
    spectra = parse_spectra(blocks[tally_num], use_primary_tag)
    if 'total' not in spectra:
        print(f"warning: no 'cell union total' spectrum found for tally "
              f"{tally_num}, skipping target.*.{particle}.mat", file=sys.stderr)
        return
    metrics = compute_metrics(spectra['total'])

    for quantity in ('DLET', 'TLET', 'DQEFF', 'TQEFF'):
        write_target_file(outdir / f"target.{quantity}.{particle}.mat",
                           metrics, quantity)


def main():
    let_spectra_path = Path(sys.argv[1])
    target_let_path = Path(sys.argv[2])
    outdir = Path(sys.argv[3])
    outdir.mkdir(parents=True, exist_ok=True)

    if let_spectra_path.exists():
        text = let_spectra_path.read_text()
        process_depth(text, 'protons', False, '1004', outdir)
        process_depth(text, 'all', False, '8104', outdir)
        process_depth(text, 'primary', True, '8204', outdir)
    else:
        print(f"error: {let_spectra_path} not found", file=sys.stderr)

    if target_let_path.exists():
        text = target_let_path.read_text()
        process_target(text, 'protons', False, '8004', outdir)
        process_target(text, 'all', False, '9104', outdir)
        process_target(text, 'primary', True, '9204', outdir)
    else:
        print(f"error: {target_let_path} not found", file=sys.stderr)


if __name__ == '__main__':
    main()
