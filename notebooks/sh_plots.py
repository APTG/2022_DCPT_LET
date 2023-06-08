#!/env/python

import numpy as np
import os
import matplotlib.pyplot as plt

plans = ("data/sh12a/results/plan_1a",
         "data/sh12a/results/plan_1b",
         "data/sh12a/results/plan_1c",
         "data/sh12a/results/plan_2"
         # "data/sh12a/results/plan_3i",
         # "data/sh12a/results/plan_3j",
         # "data/sh12a/results/plan_3k"
         )

fn_tw = ("NB_target_water__p1.txt",
         "NB_target_water__p2.txt",
         "NB_target_water__p3.txt",
         "NB_target_water__p4.txt",
         "NB_target_water__p5.txt",
         "NB_target_water__p6.txt",
         "NB_target_water__p7.txt")
lb_tw = ("Dose/prim.",
         "dLET_all", "dLET_prim_prot", "dLET_all_prot",
         "tLET_all", "tLET_prim_prot", "tLET_all_prot")

fn_t = ("NB_target__p01.txt",
        "NB_target__p02.txt",
        "NB_target__p03.txt",
        "NB_target__p04.txt",
        "NB_target__p05.txt",
        "NB_target__p06.txt",
        "NB_target__p07.txt",
        "NB_target__p08.txt",
        "NB_target__p09.txt",
        "NB_target__p10.txt",
        "NB_target__p11.txt",
        "NB_target__p12.txt",
        "NB_target__p13.txt",
        "NB_target__p14.txt")
lb_t = ("Fluence", "Dose/prim.",
        "dLET_all", "dLET_prim_prot", "dLET_all_prot",
        "tLET_all", "tLET_prim_prot", "tLET_all_prot",
        "tQeff_all", "tQeff_prim_prot", "tQeff_all_prot",
        "tQeff_all", "tQeff_prim_prot", "tQeff_all_prot")


fn_ndw = ("NB_Z_narrow_dose_water__p1.dat",
          "NB_Z_narrow_dose_water__p2.dat",
          "NB_Z_narrow_dose_water__p3.dat")
lb_ndw = ("Fluence", "Dose", "Dose prot. only")


fn_nlw = ("NB_Z_narrow_LET_water__p1.dat",
          "NB_Z_narrow_LET_water__p2.dat",
          "NB_Z_narrow_LET_water__p3.dat",
          "NB_Z_narrow_LET_water__p4.dat",
          "NB_Z_narrow_LET_water__p5.dat",
          "NB_Z_narrow_LET_water__p6.dat")
lb_nlw = lb_tw[1:]

fn_nqf = ("NB_Z_narrow_QEFF__p1.dat",
          "NB_Z_narrow_QEFF__p2.dat",
          "NB_Z_narrow_QEFF__p3.dat",
          "NB_Z_narrow_QEFF__p4.dat",
          "NB_Z_narrow_QEFF__p5.dat",
          "NB_Z_narrow_QEFF__p6.dat")
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
        d = np.loadtxt(os.path.join(p, f))
        if j > 0:  # 1st array has dose, all others are LET in MeV/cm. Convert these to keV/um
            d *= 0.1
        pstr += f'{d[3]:15.4}'
    if j > 0:
        pstr += 4*" " + "keV/um"
    else:
        pstr += 4*" " + "MeV/g/primary"
    print(pstr)

# sys.exit()

# print all Qeff (z2/beta2) values:
# print all LET values
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
        d = np.loadtxt(os.path.join(p, f))
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
    d_tw.append(np.loadtxt(os.path.join(p1a, f)))

d_ndw = []
for i, f in enumerate(fn_ndw):
    d_ndw.append(np.loadtxt(os.path.join(p1a, f)))

d_nlw = []
ddlet = []
for i, f in enumerate(fn_nlw):
    d_nlw.append(np.loadtxt(os.path.join(p1a, f)))
    ddlet.append(d_nlw[-1][:, 1])

d_nqf = []
ddqf = []
for i, f in enumerate(fn_nqf):
    d_nqf.append(np.loadtxt(os.path.join(p1a, f)))
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


# output tables:
# plt.imshow(d_full_image[0], vmin=4.0, vmax=5.5, cmap="tab20c")
# cb = plt.colorbar()
# cb.set_label("Dose [Gy]")
# cmap = cb.get_cmap('PiYG', 11)    # 11 discrete colors
# plt.xlabel("Dw [Gy]")
# plt.ylabel("NetOD")
# plt.legend()
