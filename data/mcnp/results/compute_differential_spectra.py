#!/usr/bin/env python3
"""
compute_differential_spectra.py

Writes target differential fluence spectra, matching the subset of
docs/detector_reference.md's NB_target_diff.bdo table that is actually
derivable from what MCNP scores here:

    p1  spectrum_target.FLUENCE.all.mat.vs_DEDX      <- tally 9104 (all)
    p2  spectrum_target.FLUENCE.primary.mat.vs_LET   <- tally 9204 (primary)
    p4  spectrum_target.FLUENCE.primary.Si.vs_DEDX   <- p2's spectrum,
                                                         LET recomputed in Si
                                                         via Bragg-Gray
    p6  spectrum_target.FLUENCE.protons.mat.vs_EKIN  <- tally 8004 (protons),
                                                         LET axis converted to
                                                         recovered kinetic
                                                         energy

NOT produced here (see the conversation this script came out of for the
full reasoning), matching the same table:

    p3  spectrum_target.FLUENCE.all.Si.vs_DEDX   - mixed-species LET bins
                                                    have no single energy to
                                                    invert to a Si stopping
                                                    power (same reason the
                                                    depth "all".H2O
                                                    conversion is skipped in
                                                    water_equivalent.py).
    p5  spectrum_target.FLUENCE.all.mat.vs_EKIN  - same mixed-species
                                                    problem.
    p7-p11 (deuterons/tritons/he3/alphas/heavy_recoils vs EKIN)
                                                  - MCNP deck only scores
                                                    LET spectra for
                                                    protons/primary/all at
                                                    the target; there is no
                                                    per-species spectrum on
                                                    disk to convert. Adding
                                                    these needs new MCNP
                                                    tallies, not a
                                                    postprocessing change.

p1/p2 are the raw tally spectrum, reformatted (no physics beyond what MCNP
already computed). p4/p6 reuse water_equivalent.py's Bragg-Gray machinery
(imported from it directly, not duplicated) - same accuracy caveats apply:
plain Bethe-Bloch, least reliable at the low-energy/high-LET end of the
spectrum. p1's catalog "Differential: DEDX" and p2's "Differential: LET"
are the same physical quantity (stopping power) under two historical
names in this project's catalog - both are written directly from the
tally's own LET bins, just under the differential axis name the catalog
already assigns to that page.

Output format: one row per spectrum bin, "x_value fluence fluence_error",
where x_value is LET [MeV/cm] for the .vs_DEDX/.vs_LET files or recovered
kinetic energy [MeV] for the .vs_EKIN file - same three-column convention
as the rest of this pipeline's depth/target files.
"""
import sys
from pathlib import Path

# Reuse water_equivalent.py's physics/parsing functions rather than
# duplicating them - must live in the same directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from water_equivalent import (  # noqa: E402
    split_tally_blocks, parse_spectra, bin_representative_values,
    energy_from_L, linear_stopping_power, PROTON,
)


def write_spectrum_file(path, bins, x_values):
    """bins: list of (L, phi, relerr) as returned by parse_spectra.
       x_values: the x-axis value to pair with each bin (LET or EKIN)."""
    with open(path, 'w') as f:
        for (L, phi, relerr), x in zip(bins, x_values):
            sigma_phi = relerr * phi
            f.write("{:.6E} {:.6E} {:.6E}\n".format(x, phi, sigma_phi))


def get_target_spectrum(text, tally_num, use_primary_tag):
    blocks = split_tally_blocks(text)
    if tally_num not in blocks:
        print(f"warning: tally {tally_num} not found, skipping", file=sys.stderr)
        return None
    spectra = parse_spectra(blocks[tally_num], use_primary_tag)
    if 'total' not in spectra:
        print(f"warning: no 'cell union total' spectrum found for tally "
              f"{tally_num}, skipping", file=sys.stderr)
        return None
    return spectra['total']


def main():
    target_let_path = Path(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)

    if not target_let_path.exists():
        print(f"error: {target_let_path} not found", file=sys.stderr)
        return

    text = target_let_path.read_text()

    # p1: all-species fluence vs LET (reported under the catalog's "DEDX"
    # differential axis name for this page - same underlying quantity).
    bins_all = get_target_spectrum(text, '9104', False)
    if bins_all:
        L_all = [b[0] for b in bins_all]
        write_spectrum_file(
            outdir / "spectrum_target.FLUENCE.all.mat.vs_DEDX", bins_all, L_all)

    # p2: primary-only fluence vs LET.
    bins_primary = get_target_spectrum(text, '9204', True)
    if bins_primary:
        L_primary = [b[0] for b in bins_primary]
        write_spectrum_file(
            outdir / "spectrum_target.FLUENCE.primary.mat.vs_LET", bins_primary, L_primary)

        # p4: same primary spectrum, LET axis recomputed in silicon via
        # Bragg-Gray (invert PMMA's stopping power to recover E, then
        # evaluate silicon's stopping power at that E). Bins that fall
        # outside the Bethe-Bloch validity window are dropped.
        E_primary = bin_representative_values(bins_primary)
        z, Mc2 = PROTON
        si_bins = []
        si_L = []
        n_dropped = 0
        for (L_med, phi, relerr), L_rep in zip(bins_primary, E_primary):
            if phi <= 0:
                continue
            E = energy_from_L(L_rep, z, Mc2, 'pmma')
            if E is None:
                n_dropped += 1
                continue
            L_si = linear_stopping_power(E, z, Mc2, 'silicon')
            si_bins.append((L_si, phi, relerr))
            si_L.append(L_si)
        if n_dropped:
            print(f"note: {n_dropped} bin(s) could not be inverted to an "
                  f"energy (outside Bethe-Bloch validity) and were skipped "
                  f"for the Si-converted spectrum", file=sys.stderr)
        if si_bins:
            write_spectrum_file(
                outdir / "spectrum_target.FLUENCE.primary.Si.vs_DEDX", si_bins, si_L)

    # p6: protons fluence vs recovered kinetic energy (PMMA medium).
    bins_protons = get_target_spectrum(text, '8004', False)
    if bins_protons:
        E_protons = bin_representative_values(bins_protons)
        z, Mc2 = PROTON
        ekin_bins = []
        ekin_x = []
        n_dropped = 0
        for (L_med, phi, relerr), L_rep in zip(bins_protons, E_protons):
            if phi <= 0:
                continue
            E = energy_from_L(L_rep, z, Mc2, 'pmma')
            if E is None:
                n_dropped += 1
                continue
            ekin_bins.append((L_med, phi, relerr))
            ekin_x.append(E)
        if n_dropped:
            print(f"note: {n_dropped} bin(s) could not be inverted to an "
                  f"energy (outside Bethe-Bloch validity) and were skipped "
                  f"for the vs_EKIN spectrum", file=sys.stderr)
        if ekin_bins:
            # sort by increasing energy for a sane plot/monotonic x-axis
            order = sorted(range(len(ekin_x)), key=lambda i: ekin_x[i])
            ekin_bins = [ekin_bins[i] for i in order]
            ekin_x = [ekin_x[i] for i in order]
            write_spectrum_file(
                outdir / "spectrum_target.FLUENCE.protons.mat.vs_EKIN", ekin_bins, ekin_x)


if __name__ == '__main__':
    main()
