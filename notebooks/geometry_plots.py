import numpy as np
import os
import matplotlib.pyplot as plt

ddc_files = ["data/sh12a/results/plan_1a/NB_Z_narrow_dose_water__p2.dat",
             "data/sh12a/results/plan_1b/NB_Z_narrow_dose_water__p2.dat",
             "data/sh12a/results/plan_1c/NB_Z_narrow_dose_water__p2.dat",
             "data/sh12a/results/plan_2/NB_Z_narrow_dose_water__p2.dat"]

plan_labels = ["Plan 1a - Center SOBP", "Plan 1b - d$_{95}$", "Plan 1c - d$_{74}$", "Plan 2 - 160 MeV"]

isoz = [0.0, 0.0, 0.0, 0.0]  # location of isocenter [cm]
meaz = [0.0, 5.0, 5.2, 0.0]  # location of measurement point relative to isocenter [cm]
pzmin = [-10.25, -10.25, -10.25, -2.25]  # location of phantom surface [cm]
pzmax = [+10.25, +10.25, +10.25, +17.75]  # location of phantom surface [cm]
holdz = 0.5  # thickness of the PMMA holder [cm]


def plot_ddc(fn, label, isoz, meaz, pzmin, pzmax):
    fig, ax = plt.subplots()
    data = np.loadtxt(fn)
    x = data[:, 0]
    y = data[:, 1]
    yerr = data[:, 2]
    xnorm_idx = np.argmin(np.abs(x - isoz))
    ynorm = y[xnorm_idx]
    y = y / ynorm * 100
    yerr = yerr / ynorm * 100
    ymax = np.max(y + yerr) * 1.1
    ax.errorbar(x, y, yerr, label=label)
    ax.set_xlabel("Depth rel. to isocenter [cm]")
    ax.set_ylabel("Dose [%]")
    ax.legend()
    ax.grid()
    ax.fill_between([pzmin, pzmax], 0, ymax, color='blue', alpha=0.08)
    ax.fill_between([meaz - holdz/2.0, meaz + holdz/2.0], 0, ymax, color='grey', alpha=0.3)
    ax.plot([isoz, isoz], [0, ymax], 'k:', label="Isocenter", color='green')
    ax.plot([meaz, meaz], [0, ymax], 'k--', label="Measurement point", color='red')
    plt.savefig(f"geo_plot_{i}.png")
    # plt.show()


for i, fn in enumerate(ddc_files):
    plot_ddc(fn, plan_labels[i], isoz[i], meaz[i], pzmin[i], pzmax[i])
