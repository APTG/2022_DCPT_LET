#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(".")

plans = ("data/sh12a/results/plan01_field01_geoA_SOBPcent",
         "data/sh12a/results/plan01_field01_geoB_SOBP95",
         "data/sh12a/results/plan01_field01_geoC_SOBP74",
         "data/sh12a/results/plan02_field01_geoD_mono",
         "data/sh12a/results/plan03_field01_geoA_rampFull",
         #         "data/sh12a/results/plan03_field02_geoA_rampFull",
         "data/sh12a/results/plan04_field01_geoA_rampMiddle",
         #         "data/sh12a/results/plan04_field02_geoA_rampMiddle",

         )

fn_tw = ("NB_target_water_p1.txt",
         "NB_target_water_p2.txt",
         "NB_target_water_p3.txt",
         "NB_target_water_p4.txt",
         "NB_target_water_p5.txt",
         "NB_target_water_p6.txt",
         "NB_target_water_p7.txt")

lb_tw = ("Dose/prim.",
         "dLET_all", "dLET_prim_prot", "dLET_all_prot",
         "tLET_all", "tLET_prim_prot", "tLET_all_prot")

fn_t = ("NB_target_p01.txt",
        "NB_target_p02.txt",
        "NB_target_p03.txt",
        "NB_target_p04.txt",
        "NB_target_p05.txt",
        "NB_target_p06.txt",
        "NB_target_p07.txt",
        "NB_target_p08.txt",
        "NB_target_p09.txt",
        "NB_target_p10.txt",
        "NB_target_p11.txt",
        "NB_target_p12.txt",
        "NB_target_p13.txt",
        "NB_target_p14.txt")

lb_t = ("Fluence", "Dose/prim.",
        "dLET_all", "dLET_prim_prot", "dLET_all_prot",
        "tLET_all", "tLET_prim_prot", "tLET_all_prot",
        "tQeff_all", "tQeff_prim_prot", "tQeff_all_prot",
        "tQeff_all", "tQeff_prim_prot", "tQeff_all_prot")

fn_tdiff = ("NB_target_diff_p1.dat",
            "NB_target_diff_p2.dat",
            "NB_target_diff_p3.dat",
            "NB_target_diff_p4.dat",
            )

lb_tdiff = ("LET PMMA all", "LET PMMA prim. protons",
            "LET Si all", "LET Si prim. protons")


fn_twdiff = ("NB_target_water_diff_p1.dat",
             "NB_target_water_diff_p2.dat",
             )

lb_twdiff = ("LET Water all", "LET Water prim. protons")


fn_ndw = ("NB_Z_narrow_dose_water_p1.dat",
          "NB_Z_narrow_dose_water_p2.dat",
          "NB_Z_narrow_dose_water_p3.dat")
lb_ndw = ("Fluence", "Dose", "Dose prot. only")


fn_nlw = ("NB_Z_narrow_LET_water_p1.dat",
          "NB_Z_narrow_LET_water_p2.dat",
          "NB_Z_narrow_LET_water_p3.dat",
          "NB_Z_narrow_LET_water_p4.dat",
          "NB_Z_narrow_LET_water_p5.dat",
          "NB_Z_narrow_LET_water_p6.dat")
lb_nlw = lb_tw[1:]

fn_nqf = ("NB_Z_narrow_QEFF_p1.dat",
          "NB_Z_narrow_QEFF_p2.dat",
          "NB_Z_narrow_QEFF_p3.dat",
          "NB_Z_narrow_QEFF_p4.dat",
          "NB_Z_narrow_QEFF_p5.dat",
          "NB_Z_narrow_QEFF_p6.dat")
lb_nqf = ("dQeff all", "dQeff prim. protons", "dQeff prim. & sec. prot.",
          "tQeff all", "tQeff prim. protons", "tQeff prim. & sec. prot.")

# print all LET values
print(" ------- Dose and LET in WATER -------")
pstr = 21 * ' '
for j, p in enumerate(plans):
    _s = p.split('/')[-1].upper()
    pstr += f'{_s:>15}'
print(pstr)

for j, f in enumerate(fn_tw):
    pstr = f'{lb_tw[j]:<20}:'
    for i, p in enumerate(plans):
        d = np.loadtxt(BASE / p / f)
        if j > 0:  # 1st array has dose, all others are LET in MeV/cm. Convert these to keV/um
            d *= 0.1
        pstr += f'{d[3]:15.4}'
    if j > 0:
        pstr += 4*" " + "keV/um"
    else:
        pstr += 4*" " + "MeV/g/primary"
    print(pstr)

print("\n")
print(" ------- Dose and LET in MEDIUM -------")
pstr = 21 * ' '
for j, p in enumerate(plans):
    _s = p.split('/')[-1].upper()
    pstr += f'{_s:>15}'
print(pstr)

for j, f in enumerate(fn_t):
    pstr = f'{lb_t[j]:<20}:'
    for i, p in enumerate(plans):
        d = np.loadtxt(BASE / p / f)
        if j > 1 and j < 7:
            d *= 0.1
        pstr += f'{d[3]:15.4}'
    if j > 1 and j < 7:
        pstr += 4*" " + "keV/um"
    elif j == 0:
        pstr += 4*" " + "/cm2/primary"
    elif j == 1:
        pstr += 4*" " + "MeV/g/primary"
    else:
        pstr += 4*" " + "(nil)"
    print(pstr)

#
zshift = 10.25
zrange = (-1, 17)
ydrange = (0, 130)
ptv = (-5.0 + zshift, 5.0 + zshift)  # size of PTV along z axis
p1a = plans[0]

d_tw = []
for i, f in enumerate(fn_tw):
    d_tw.append(np.loadtxt(BASE / p1a / f))

d_ndw = []
for i, f in enumerate(fn_ndw):
    d_ndw.append(np.loadtxt(BASE / p1a / f))

d_nlw = []
ddlet = []
for i, f in enumerate(fn_nlw):
    d_nlw.append(np.loadtxt(BASE / p1a / f))
    ddlet.append(d_nlw[-1][:, 1])

d_nqf = []
ddqf = []
for i, f in enumerate(fn_nqf):
    d_nqf.append(np.loadtxt(BASE / p1a / f))
    ddqf.append(d_nqf[-1][:, 1])

dd = d_ndw[1]
dz = dd[:, 0]
z0 = np.where(dz == 0.0)[0]

dz += zshift

# normalise center dose to 100 %.
dnorm = dd[z0, 1]
ddose = dd[:, 1] / dnorm * 100.0

let_mask = (ddose > 1.0)
z_lim = dz[let_mask]

fig, ax1 = plt.subplots()
color = 'k'
plt.grid(True)
ax1.set_ylim(ydrange)
ax1.set_ylabel('Relative dose [%]', color=color)
ax1.set_xlabel('Depth from phantom surface [cm]', color=color)
ax1.plot(dz, ddose, color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.fill_between(ptv, ydrange[0], ydrange[1], alpha=.1, color='b')

color = 'tab:blue'
ax2 = ax1.twinx()
plt.yscale('log')
ax2.set_ylabel('LET [keV/um]', color=color)
for i, let in enumerate(ddlet):
    ax2.plot(z_lim, let[let_mask] * 0.1, label=lb_nlw[i])
ax2.tick_params(axis='y', labelcolor=color)
ax2.legend(loc=2, fontsize=8)
ax2.set_xlim(zrange)
plt.savefig("foo.png")

fig, ax1 = plt.subplots()
color = 'k'
plt.grid(True)
ax1.set_ylim(ydrange)
ax1.set_ylabel('Relative dose [%]', color=color)
ax1.set_xlabel('Depth from phantom surface [cm]', color=color)
ax1.plot(dz, ddose, color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.fill_between(ptv, ydrange[0], ydrange[1], alpha=.1, color='b')

color = 'tab:blue'
ax2 = ax1.twinx()
plt.yscale('log')
ax2.set_ylabel('Qeff [nil]', color=color)
for i, qf in enumerate(ddqf):
    ax2.plot(z_lim, qf[let_mask], label=lb_nqf[i])
ax2.tick_params(axis='y', labelcolor=color)
ax2.legend(loc=2, fontsize=8)
ax2.set_xlim(zrange)
plt.savefig("foo2.png")


# Now treat the differental LET plots
# first load the data
# Define the 6 spectra (keep your existing tuples)
diff_files = list(fn_tdiff) + list(fn_twdiff)
diff_labels = list(lb_tdiff) + list(lb_twdiff)   # length should be 6

# spec[plan_i][spec_i] is Nx2: [LET, dPhi/dLET]
spec = []
for p in plans:
    per_plan = []
    for f in diff_files:
        per_plan.append(np.loadtxt(BASE / p / f))
    spec.append(per_plan)

# Optional: convenience views (assumes same LET grid for all 6 within each plan)
spec_x = []
spec_y = []
for plan_i, per_plan in enumerate(spec):
    x0 = per_plan[0][:, 0]
    spec_x.append(x0)
    spec_y.append([arr[:, 1] for arr in per_plan])

    # sanity check (can remove later)
    for spec_i, arr in enumerate(per_plan[1:], start=1):
        if arr.shape[0] != x0.shape[0] or not np.allclose(arr[:, 0], x0):
            raise ValueError(f"LET grid differs: plan={plans[plan_i]}, spectrum={diff_labels[spec_i]}")

plan_names = [p.split("/")[-1] for p in plans]

# one figure per spectrum type (6 figures total)
fill_alpha = 0.1
for spec_i, spec_label in enumerate(diff_labels):
    plt.figure()
    plt.grid(True)
    plt.xlabel("LET [keV/um]")           # add units if you want
    plt.ylabel("dPhi/dLET [(/cm) / (keV/um) / primary]")     # add units if you want
    plt.title(spec_label)

    plt.xlim(0.4, 200)
    plt.ylim(1e-8, 1e-1)
    plt.xscale('log')  # if needed, adjust limits accordingly
    plt.yscale('log')  # if needed, adjust limits accordingly

    # plot this spectrum type for all plans
    for plan_i, p in enumerate(plans):
        arr = spec[plan_i][spec_i]
        x = arr[:, 0] * 0.1  # LET [keV/um]
        y = arr[:, 1] * 10.0  # dPhi/dLET [(/cm) / (keV/um) / primary]
        if "ramp" in plan_names[plan_i].lower():
            plt.step(x, y, where='mid', label=plan_names[plan_i], linestyle='--')
            plt.fill_between(x, y, step="mid", alpha=fill_alpha)
        else:
            plt.step(x, y, where='mid', label=plan_names[plan_i])
            plt.fill_between(x, y, step="mid", alpha=fill_alpha)

    plt.legend(fontsize=8)
    plt.savefig(f"spec_{spec_i+1:02d}_{spec_label.replace(' ', '_')}.png", dpi=200)
    plt.close()

# find spectrum indices by label content
idx_all = [i for i, lab in enumerate(diff_labels) if "all" in lab.lower()]
idx_prim = [i for i, lab in enumerate(diff_labels) if "prim" in lab.lower()]


# one ifgure per plan "all" spectra
for plan_i, plan_name in enumerate(plan_names):
    plt.figure()
    plt.grid(True)
    plt.xlabel("LET [keV/um]")
    plt.ylabel("dPhi/dLET [(/cm) / (keV/um) / primary]")
    plt.title(f"{plan_name} – all particles")

    plt.xlim(0.4, 200)
    plt.ylim(1e-8, 1e-1)
    plt.xscale('log')
    plt.yscale('log')

    for spec_i in idx_all:
        arr = spec[plan_i][spec_i]
        x = arr[:, 0] * 0.1
        y = arr[:, 1] * 10.0
        plt.step(x, y, where='mid', label=diff_labels[spec_i])
        plt.fill_between(x, y, step="mid", alpha=fill_alpha)

    plt.legend(fontsize=8)
    plt.savefig(f"{plan_name}_spectra_all.png", dpi=200)
    plt.close()


# one figure per plan "prim. proton" spectra
for plan_i, plan_name in enumerate(plan_names):
    plt.figure()
    plt.grid(True)
    plt.xlabel("LET [keV/um]")
    plt.ylabel("dPhi/dLET [(/cm) / (keV/um) / primary]")
    plt.title(f"{plan_name} – primary protons")

    plt.xlim(0.4, 200)
    plt.ylim(1e-8, 1e-1)
    plt.xscale('log')
    plt.yscale('log')

    for spec_i in idx_prim:
        arr = spec[plan_i][spec_i]
        x = arr[:, 0] * 0.1
        y = arr[:, 1] * 10.0
        plt.step(x, y, where='mid', label=diff_labels[spec_i])
        plt.fill_between(x, y, step="mid", alpha=fill_alpha)

    plt.legend(fontsize=8)
    plt.savefig(f"{plan_name}_spectra_prim.png", dpi=200)
    plt.close()

# Last plots are the secondaries only, so we need to match them by material
# name (e.g. PMMA, Si, Water) and create new labels like "LET PMMA secondary"

pairs_sec = []   # list of (all_index, prim_index, new_label)

for i_all in idx_all:
    lab_all = diff_labels[i_all].lower()

    # find matching prim spectrum (same material name)
    for i_prim in idx_prim:
        lab_prim = diff_labels[i_prim].lower()

        # crude but effective: match by first word (PMMA / Si / Water)
        if lab_all.split()[1] == lab_prim.split()[1]:
            material = diff_labels[i_all].split()[1]
            pairs_sec.append((i_all, i_prim, f"LET {material} secondary"))
            break

# one figure per plan "secondary" spectra
for plan_i, plan_name in enumerate(plan_names):
    plt.figure()
    plt.grid(True)
    plt.xlabel("LET [keV/um]")
    plt.ylabel("dPhi/dLET [(/cm) / (keV/um) / primary]")
    plt.title(f"{plan_name} – secondary particles")

    plt.xlim(0.4, 200)
    plt.ylim(1e-8, 1e-1)
    plt.xscale('log')
    plt.yscale('log')

    for i_all, i_prim, label in pairs_sec:
        arr_all = spec[plan_i][i_all]
        arr_prim = spec[plan_i][i_prim]

        x = arr_all[:, 0] * 0.1
        y_sec = (arr_all[:, 1] - arr_prim[:, 1]) * 10.0

        plt.step(x, y_sec, where='mid', label=label)
        plt.fill_between(x, y_sec, step="mid", alpha=fill_alpha)

    plt.legend(fontsize=8)
    plt.savefig(f"{plan_name}_spectra_secondary.png", dpi=200)
    plt.close()


# Ramped fields: combine field01 + flipped(field02)
#   - Dose/fluence/etc.: sum
#   - LET/Qeff: dose-weighted average using fn_ndw[1] as weight

narrow_files = list(fn_ndw) + list(fn_nlw) + list(fn_nqf)
dose_weight_file = fn_ndw[1]  # "NB_Z_narrow_dose_water_p2.dat" (Dose)


def _sorted_xy(arr):
    x = arr[:, 0].astype(float)
    y = arr[:, 1].astype(float)
    order = np.argsort(x)
    return x[order], y[order]


def _load_sorted_xy(path):
    return _sorted_xy(np.loadtxt(path))


# field01 plan02 is possibly wrong need to check, using plan01 since they are identical anyway.
plan_defs = [
    ("plan03", "data/sh12a/results/plan03_field01_geoA_rampFull",   "data/sh12a/results/plan03_field02_geoA_rampFull"),
    ("plan04", "data/sh12a/results/plan04_field01_geoA_rampMiddle", "data/sh12a/results/plan04_field01_geoA_rampMiddle"),
]

for plan_id, p_field01, p_field02 in plan_defs:
    for fname in narrow_files:
        f1 = BASE / p_field01 / fname
        f2 = BASE / p_field02 / fname

        if not f1.exists() or not f2.exists():
            continue

        print(f"[combine] {plan_id}: {fname}")
        print(f"  field01: {f1}")
        print(f"  field02: {f2}")

        # field01 signal
        x1, y1 = _load_sorted_xy(f1)

        # field02 signal (flipped x)
        x2_raw, y2_raw = _load_sorted_xy(f2)

        # Convert LET/Qeff from MeV/cm to keV/um BEFORE interpolation (affects both fields)
        is_letq = (fname in fn_nlw) or (fname in fn_nqf)
        if is_letq:
            y1 *= 0.1
            y2_raw *= 0.1

        x2 = -x2_raw
        order2 = np.argsort(x2)
        x2 = x2[order2]
        y2 = y2_raw[order2]

        # interpolate field02 onto field01 x-grid
        y2i = np.interp(x1, x2, y2, left=np.nan, right=np.nan)

        # --- Decide how to combine ---
        if is_letq:
            # Dose-weighted average: need dose for field01 + flipped(field02)
            d1_path = BASE / p_field01 / dose_weight_file
            d2_path = BASE / p_field02 / dose_weight_file

            if not d1_path.exists() or not d2_path.exists():
                print(f"  WARNING: missing dose weights for {fname}, skipping")
                continue

            xd1, d1 = _load_sorted_xy(d1_path)

            xd2_raw, d2_raw = _load_sorted_xy(d2_path)
            xd2 = -xd2_raw
            orderd2 = np.argsort(xd2)
            xd2 = xd2[orderd2]
            d2 = d2_raw[orderd2]

            # interpolate dose arrays onto x1 grid
            d1i = np.interp(x1, xd1, d1, left=np.nan, right=np.nan)
            d2i = np.interp(x1, xd2, d2, left=np.nan, right=np.nan)

            denom = d1i + d2i

            # only where everything is valid and denom > 0
            m = np.isfinite(y1) & np.isfinite(y2i) & np.isfinite(denom) & (denom > 0.0)

            y_comb = np.full_like(y1, np.nan, dtype=float)
            y_comb[m] = (y1[m] * d1i[m] + y2i[m] * d2i[m]) / denom[m]

            y_label = "LET [keV/um]"
            comb_label = "LET"
        else:
            # Dose / fluence etc.: simple sum
            m = np.isfinite(y1) & np.isfinite(y2i)
            y_comb = y1 + y2i
            y_label = "Dose [MeV/g/primary]" if "dose" in fname.lower() else "Fluence [/cm2/primary]"
            comb_label = "Total dose"

        # --- Plot ---
        plt.figure()
        plt.grid(True)
        plt.xlabel("z [cm]")
        plt.ylabel(y_label)
        plt.title(f"{plan_id} – {fname} (field01 + field02)")

        plt.plot(x1, y1, label="field01")
        plt.plot(x1, y2i, label="field02")
        plt.plot(x1[m], y_comb[m], label=comb_label, linewidth=2.5)

        # cap LET plots at 10 keV/um
        if is_letq:
            plt.ylim(top=20.0)

        plt.legend(fontsize=8)
        out_name = f"{plan_id}_fieldcombine_{Path(fname).stem}.png"
        plt.savefig(out_name, dpi=200)
        plt.close()
