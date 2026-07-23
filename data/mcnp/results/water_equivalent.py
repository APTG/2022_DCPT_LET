#!/usr/bin/env python3
"""
water_equivalent.py

Converts the proton LET-spectrum data in LET_Spectra / Target_LET into
water-equivalent quantities: Dose-to-water and LET-in-water, per depth
cell (and as a single target scalar), using Bragg-Gray cavity theory.

WHY THIS NEEDS A REAL PHYSICS MODEL (read before trusting the numbers)
-----------------------------------------------------------------------
MCNP's "ft LET" tally reports the LET actually deposited in the REAL cell
material (GRAMMX/PMMA), not water. There is no MCNP card that swaps the
stopping-power medium for a charged-particle tally on the fly (unlike
photon/neutron KERMA, where an FM multiplier referencing a different
material works). To get "as if this were water" you need, for every LET
bin, the proton's kinetic energy E, then:

    L_water(E) = S_water(E)           [mass stopping power * water density]
    Dose_water_bin = Phi_i * L_water(E_i)

Since the tally only stores L_medium_i = S_medium(E_i) (not E_i itself),
E_i is recovered by numerically inverting the medium's own stopping-power
curve S_medium(E) = L_medium_i, then L_water(E_i) is evaluated directly.
S(E) here is the Bethe formula (mean-excitation-energy / Bragg additivity
rule), built from the exact element mass fractions and densities already
used in the MCNP deck (m101 GRAMMX, m103 water, m104 PMMA) - not fetched
from NIST PSTAR.

ACCURACY CAVEAT: plain Bethe-Bloch (no shell, Barkas or Bloch
corrections) matches NIST PSTAR water values to about 1-2% for protons
from roughly 5-250 MeV (checked against published PSTAR points here), but
degrades below a few MeV - i.e. exactly the Bragg-peak region, which is
usually the most clinically relevant part of the curve. Treat low-energy
bins (large LET, end of range) as the least reliable. If you need
NIST-grade accuracy there, real PSTAR tables should replace
`mass_stopping_power()`.

SCOPE: this conversion is only physically well-defined for a SINGLE
particle species (fixed mass/charge), because a given LET value can come
from different particles at very different energies. It is applied here
to the "protons" and "primary" (proton-tagged) tallies. It is NOT applied
to the "all particles" tally (1004->8104 mix of p/n/e/h/d/t/s/a) since
inverting a mixed-species LET spectrum to a single energy is not
meaningful.
"""
import argparse
import locale
import math
import re
import sys
from pathlib import Path

locale.setlocale(locale.LC_NUMERIC, "C")

# ---------------------------------------------------------------------------
# Physics constants
# ---------------------------------------------------------------------------
K = 0.307075          # MeV cm^2 / mol  (Bethe formula constant)
ME_C2 = 0.510998950   # MeV, electron rest energy
MP_C2 = 938.27208816  # MeV, proton rest energy

# Standard ICRU-37 mean excitation energies (eV) for the elements present
# in this deck's materials.
I_EV = {
    'H': 19.2, 'C': 78.0, 'N': 82.0, 'O': 95.0, 'Cl': 173.0, 'Ca': 191.0,
    'Si': 173.0,
}
Z_OF = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'Cl': 17, 'Ca': 20, 'Si': 14}
A_OF = {'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 16.00, 'Cl': 35.45, 'Ca': 40.08,
        'Si': 28.085}

# Materials, exactly matching the m101/m103/m104 cards in the MCNP deck
# (element -> mass fraction), plus density in g/cm3. 'silicon' added for the
# vs_DEDX-in-Si differential spectrum (compute_differential_spectra.py) -
# ICRU-37 I-value 173 eV, standard crystalline-Si density.
MATERIALS = {
    'grammx': {'density': 1.032,
               'comp': {'H': 0.08, 'C': 0.6730, 'N': 0.0239, 'O': 0.1986,
                         'Cl': 0.0014, 'Ca': 0.0231}},
    'water':  {'density': 0.998,
               'comp': {'H': 0.111894, 'O': 0.888106}},
    'pmma':   {'density': 1.18,
               'comp': {'H': 0.08054, 'C': 0.59985, 'O': 0.31962}},
    'silicon': {'density': 2.33,
                'comp': {'Si': 1.0}},
}


def mixture_I_and_ZA(comp):
    """Bragg additivity rule -> (mean excitation energy [eV], sum(w*Z/A))."""
    num = 0.0
    den = 0.0
    for el, w in comp.items():
        za = w * (Z_OF[el] / A_OF[el])
        num += za * math.log(I_EV[el])
        den += za
    return math.exp(num / den), den


for name, mat in MATERIALS.items():
    mat['I_eV'], mat['ZA'] = mixture_I_and_ZA(mat['comp'])


def mass_stopping_power(E_MeV, z, M_c2_MeV, I_eV, ZA_eff):
    """Bethe formula, mass collision stopping power [MeV cm^2/g]."""
    if E_MeV <= 0:
        return 0.0
    I_MeV = I_eV * 1e-6
    gamma = 1.0 + E_MeV / M_c2_MeV
    beta2 = 1.0 - 1.0 / (gamma * gamma)
    if beta2 <= 0:
        return 0.0
    Wmax = (2 * ME_C2 * beta2 * gamma * gamma) / \
           (1 + 2 * gamma * ME_C2 / M_c2_MeV + (ME_C2 / M_c2_MeV) ** 2)
    if Wmax <= 0:
        return 0.0
    term = 0.5 * math.log(2 * ME_C2 * beta2 * gamma * gamma * Wmax / (I_MeV * I_MeV)) - beta2
    if term <= 0:
        return 0.0
    return K * z * z * ZA_eff * (1.0 / beta2) * term


def linear_stopping_power(E_MeV, z, M_c2_MeV, material):
    mat = MATERIALS[material]
    return mass_stopping_power(E_MeV, z, M_c2_MeV, mat['I_eV'], mat['ZA']) * mat['density']


def energy_from_L(L_target_MeV_per_cm, z, M_c2_MeV, material,
                   e_lo=0.05, e_hi=1000.0, tol=1e-4, max_iter=100):
    """
    Invert L(E) = L_target for E, given L(E) is monotonically decreasing
    with E over [e_lo, e_hi] (true for protons above ~50 keV, the Bragg
    formula's region of validity). Bisection.
    """
    if L_target_MeV_per_cm <= 0:
        return None
    f_lo = linear_stopping_power(e_lo, z, M_c2_MeV, material) - L_target_MeV_per_cm
    f_hi = linear_stopping_power(e_hi, z, M_c2_MeV, material) - L_target_MeV_per_cm
    if f_lo < 0 or f_hi > 0:
        # L_target outside the range Bethe-Bloch can represent here
        # (either far below the Bragg-peak stopping limit, or an
        # unrealistically low LET for this energy window).
        return None
    lo, hi = e_lo, e_hi
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = linear_stopping_power(mid, z, M_c2_MeV, material) - L_target_MeV_per_cm
        if abs(f_mid) < tol * L_target_MeV_per_cm:
            return mid
        if f_mid > 0:   # L(mid) > target -> need higher E (L decreases with E)
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Parsing (same format as extract_tallies.sh / compute_let_metrics.py)
# ---------------------------------------------------------------------------
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
    cur_num, cur_lines = None, []
    for line in text.splitlines():
        m = TALLY_MARKER_RE.match(line) or TALLY_HEADER_RE.match(line)
        if m:
            if cur_num is not None:
                blocks[cur_num] = "\n".join(cur_lines)
            cur_num, cur_lines = m.group(1), []
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
        if CELL_UNION_RE.search(line):
            current_cell, capture, bins = 'total', not use_primary_tag, []
            continue
        m = CELL_RE.match(line)
        if m:
            current_cell, capture, bins = m.group(1), not use_primary_tag, []
            continue
        m = USERBIN_RE.search(line)
        if m:
            if use_primary_tag:
                capture = abs(float(m.group(1)) - PRIMARY_TAG_VALUE) < 1.0
                bins = []
            continue
        if HEADER_RE.search(line):
            continue
        m = BIN_RE.match(line)
        if m and capture:
            bins.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
            continue
        m = TOTAL_RE.match(line)
        if m:
            if capture and current_cell is not None:
                results[current_cell] = bins
            continue
    return results


def bin_representative_values(bins):
    """E_i = average(L_i, L_{i+1}), matching the established convention."""
    n = len(bins)
    L = [b[0] for b in bins]
    return [((L[i] + L[i + 1]) / 2.0 if i + 1 < n else L[i]) for i in range(n)]


def q_icrp60(L_kev_um):
    if L_kev_um < 10.0:
        return 1.0
    elif L_kev_um <= 100.0:
        return 0.32 * L_kev_um - 2.2
    return 300.0 / math.sqrt(L_kev_um)


def weighted_avg_and_error(weights, sigma_weights, values):
    sum_w = sum(weights)
    if sum_w <= 0:
        return 0.0, 0.0
    x = sum(w * v for w, v in zip(weights, values)) / sum_w
    var = sum(((v - x) / sum_w) ** 2 * sw * sw
              for w, sw, v in zip(weights, sigma_weights, values))
    return x, math.sqrt(var)


def cell_depth(cell_num):
    return 10.2 - 0.1 * (int(cell_num) - 400)


def cell_material(cell_num):
    """400-499 and 505-604 are GRAMMX (m101); 500-504 are PMMA (m104)."""
    n = int(cell_num)
    return 'pmma' if 500 <= n <= 504 else 'grammx'


PROTON = (1, MP_C2)  # (z, rest energy)


def water_convert_cell(bins, material):
    """
    For one cell's LET spectrum (in `material`), return per-bin:
    (Phi_i, sigma_Phi_i, L_water_i) using Bragg-Gray conversion.
    Bins whose LET can't be inverted (outside the Bethe-Bloch validity
    window) are dropped and counted in `n_dropped`.
    """
    E_bins = bin_representative_values(bins)
    z, Mc2 = PROTON
    out = []
    n_dropped = 0
    for (L_med, phi, relerr), L_med_rep in zip(bins, E_bins):
        if phi <= 0:
            continue
        E = energy_from_L(L_med_rep, z, Mc2, material)
        if E is None:
            n_dropped += 1
            continue
        L_water = linear_stopping_power(E, z, Mc2, 'water')
        sigma_phi = relerr * phi
        out.append((phi, sigma_phi, L_water))
    return out, n_dropped


def compute_water_metrics(converted):
    """converted: list of (Phi_i, sigma_Phi_i, L_water_i) -> dict of (value, sigma)."""
    if not converted:
        z = (0.0, 0.0)
        return {'DOSE': z, 'DLET': z, 'TLET': z, 'DQEFF': z, 'TQEFF': z}

    phi = [c[0] for c in converted]
    sigma_phi = [c[1] for c in converted]
    Lw = [c[2] for c in converted]
    D = [p * l for p, l in zip(phi, Lw)]
    sigma_D = [l * sp for l, sp in zip(Lw, sigma_phi)]
    Q = [q_icrp60(l * 0.1) for l in Lw]

    dose, sigma_dose = sum(D), math.sqrt(sum(sd * sd for sd in sigma_D))
    tlet, sigma_tlet = weighted_avg_and_error(phi, sigma_phi, Lw)
    dlet, sigma_dlet = weighted_avg_and_error(D, sigma_D, Lw)
    tqeff, sigma_tqeff = weighted_avg_and_error(phi, sigma_phi, Q)
    dqeff, sigma_dqeff = weighted_avg_and_error(D, sigma_D, Q)

    return {
        'DOSE': (dose, sigma_dose),
        'DLET': (dlet, sigma_dlet),
        'TLET': (tlet, sigma_tlet),
        'DQEFF': (dqeff, sigma_dqeff),
        'TQEFF': (tqeff, sigma_tqeff),
    }


def write_depth_file(path, per_cell_metrics, quantity):
    cells = sorted((c for c in per_cell_metrics if c != 'total'), key=int)
    with open(path, 'w') as f:
        for c in cells:
            value, sigma = per_cell_metrics[c][quantity]
            f.write("{:g} {:.6E} {:.6E}\n".format(cell_depth(c), value, sigma))


def write_target_file(path, metrics, quantity):
    value, sigma = metrics[quantity]
    with open(path, 'w') as f:
        f.write("{:.6E} {:.6E}\n".format(value, sigma))


def process_depth(text, particle, use_primary_tag, tally_num, outdir):
    blocks = split_tally_blocks(text)
    if tally_num not in blocks:
        print(f"warning: tally {tally_num} not found, skipping depth_Z.*.{particle}.H2O",
              file=sys.stderr)
        return
    spectra = parse_spectra(blocks[tally_num], use_primary_tag)
    per_cell_metrics = {}
    total_dropped = 0
    for cell, bins in spectra.items():
        if cell == 'total':
            continue
        converted, n_dropped = water_convert_cell(bins, cell_material(cell))
        total_dropped += n_dropped
        per_cell_metrics[cell] = compute_water_metrics(converted)
    if total_dropped:
        print(f"note: tally {tally_num}: {total_dropped} bin(s) could not be "
              f"inverted to an energy (outside Bethe-Bloch validity) and were "
              f"skipped", file=sys.stderr)
    for quantity, fname in [('DOSE', f"depth_Z.DOSE.{particle}.H2O"),
                             ('DLET', f"depth_Z.DLET.{particle}.H2O"),
                             ('TLET', f"depth_Z.TLET.{particle}.H2O"),
                             ('DQEFF', f"depth_Z.DQEFF.{particle}.H2O"),
                             ('TQEFF', f"depth_Z.TQEFF.{particle}.H2O")]:
        write_depth_file(outdir / fname, per_cell_metrics, quantity)


def process_target(text, particle, use_primary_tag, tally_num, outdir, material='pmma'):
    """Target cells (500-504) are all PMMA."""
    blocks = split_tally_blocks(text)
    if tally_num not in blocks:
        print(f"warning: tally {tally_num} not found, skipping target.*.{particle}.H2O",
              file=sys.stderr)
        return
    spectra = parse_spectra(blocks[tally_num], use_primary_tag)
    if 'total' not in spectra:
        print(f"warning: no 'cell union total' spectrum for tally {tally_num}, "
              f"skipping target.*.{particle}.H2O", file=sys.stderr)
        return
    converted, n_dropped = water_convert_cell(spectra['total'], material)
    if n_dropped:
        print(f"note: tally {tally_num}: {n_dropped} bin(s) skipped (outside "
              f"Bethe-Bloch validity)", file=sys.stderr)
    metrics = compute_water_metrics(converted)
    # NOTE: target.{DOSE,DQEFF,TQEFF}.{particle}.H2O intentionally NOT written
    # (removed per request) - only DLET/TLET are produced for the target.
    for quantity, fname in [('DLET', f"target.DLET.{particle}.H2O"),
                             ('TLET', f"target.TLET.{particle}.H2O")]:
        write_target_file(outdir / fname, metrics, quantity)


def main():
    let_spectra_path = Path(sys.argv[1])
    target_let_path = Path(sys.argv[2])
    outdir = Path(sys.argv[3])
    outdir.mkdir(parents=True, exist_ok=True)

    if let_spectra_path.exists():
        text = let_spectra_path.read_text()
        process_depth(text, 'protons', False, '1004', outdir)
        process_depth(text, 'primary', True, '8204', outdir)
    else:
        print(f"error: {let_spectra_path} not found", file=sys.stderr)

    if target_let_path.exists():
        text = target_let_path.read_text()
        process_target(text, 'protons', False, '8004', outdir)
        process_target(text, 'primary', True, '9204', outdir)
    else:
        print(f"error: {target_let_path} not found", file=sys.stderr)


if __name__ == '__main__':
    main()
