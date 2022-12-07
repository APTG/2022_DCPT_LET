import matplotlib.pyplot as plt
import numpy as np
from topas2numpy import BinnedResult

files = []
Dose = BinnedResult('data/topas/results/output/plan_1c/Scoring_protonD_ZBox.csv')
LET = BinnedResult('data/topas/results/output/plan_1c/Scoring_protonLET_YBox.csv')

ax1 = plt.subplot()
ax2 = ax1.twinx()

x = Dose.dimensions[1].get_bin_centers()
yLET = np.squeeze(LET.data['Sum'])
yDose = np.squeeze(Dose.data['Sum'])

scale = 2/np.mean(yDose[90:225])

Dplot = ax1.plot(np.flip(x), yDose*scale,label=Dose.quantity)

DplotLET = ax1.plot(np.flip(x), yDose*scale + yLET*0.05*yDose*scale, c='b' ,label="LET optimised Dose")
Dose_uBound = yDose*scale + yLET*0.05*yDose*1.1*scale
Dose_lBound = yDose*scale + yLET*0.05*yDose*0.9*scale

Dplot_u = ax1.plot(np.flip(x), Dose_uBound, '--', c='b')
Dplot_l = ax1.plot(np.flip(x), Dose_lBound, '--', c='b')

LETplot = ax2.plot(np.flip(x), yLET, c='k', label=LET.quantity)
ax1.set_xlabel(Dose.dimensions[1].name +": ["+ Dose.dimensions[1].unit+ "]")
ax1.grid()
ax1.set_ylabel(Dose.quantity +": ["+ Dose.unit + "]")
ax2.set_ylabel(LET.quantity +": ["+ LET.unit + "]")


ax1.fill_between(x=[0, 15.8], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='blue', alpha=0.1)
ax1.fill_between(x=[15.8, 16.3], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='black', alpha=0.3)
ax1.fill_between(x=[16.3, 20], y1=0, y2=max(np.squeeze(Dose.data['Sum']))*scale+1, facecolor='blue', alpha=0.1)

# added these three lines
lns = LETplot+DplotLET+Dplot
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=0)
# plt.vlines(x =[11.8, 12.8], ymin = 0, ymax =max(np.squeeze(dose.data['Sum'])), color = 'red', label = 'Cellflask 3')
plt.show()
# plt.savefig("TOPAS/Plots/2GySOBP/" + data.quantity)

