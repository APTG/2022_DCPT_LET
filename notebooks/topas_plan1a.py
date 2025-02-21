import matplotlib.pyplot as plt
import numpy as np
from topas2numpy import BinnedResult

files = []
Dose = BinnedResult('data/topas/results/output/plan01_geoA_SOBPcent/Scoring_protonD_ZBox.csv')
LET = BinnedResult('data/topas/results/output/plan01_geoA_SOBPcent/Scoring_protonLET_YBox.csv')

ax1 = plt.subplot()
ax2 = ax1.twinx()

x = Dose.dimensions[1].get_bin_centers()
yLET = np.squeeze(LET.data['Sum'])
yDose = np.squeeze(Dose.data['Sum'])

scale = 2/np.mean(yDose[90:225])

Dplot = ax1.plot(np.flip(x), yDose*scale, label="Dose")

DplotLET = ax1.plot(np.flip(x), yDose*scale + yLET*0.05*yDose*scale, c='b', label="RBE")
Dose_uBound = yDose*scale + yLET*0.05*yDose*1.1*scale
Dose_lBound = yDose*scale + yLET*0.05*yDose*0.9*scale

Dplot_u = ax1.plot(np.flip(x), Dose_uBound, '--', c='b', label="+/-10% in LET")
Dplot_l = ax1.plot(np.flip(x), Dose_lBound, '--', c='b')

LETplot = ax2.plot(np.flip(x), yLET, c='k', label="LETd")
ax1.set_xlabel("Z" + ": [" + Dose.dimensions[1].unit + "]")
ax1.grid()
ax1.set_ylabel("Dose" + ": [" + Dose.unit + "]")
ax2.set_ylabel(LET.quantity + ": [keV/micron]")

# added these three lines
lns = LETplot+DplotLET+Dplot+Dplot_u
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=2)

ax1.fill_between(x=[0, 10], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='blue', alpha=0.1)
ax1.fill_between(x=[10.0, 10.5], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='black', alpha=0.3)
ax1.fill_between(x=[10.5, 20.5], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='blue', alpha=0.1)
# plt.vlines(x =[11.8, 12.8], ymin = 0, ymax =max(np.squeeze(dose.data['Sum'])), color = 'red', label = 'Cellflask 3')
# plt.show()
plt.savefig("data/topas/results/plan01_geoA_SOBPcent/" + Dose.quantity + "_" + LET.quantity)
