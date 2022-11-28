import matplotlib.pyplot as plt
import numpy as np
from topas2numpy import BinnedResult

files = []
files.append(BinnedResult('path to data'))
files.append(BinnedResult('path to data'))
for data in files:
    print('{0} [{1}]'.format(data.quantity, data.unit))
    print(f'Statistics: {data.statistics}')
    for dim in data.dimensions:
        print('{0} [{1}]: {2} bins'.format(dim.name, dim.unit, dim.n_bins))

    ax = plt.subplot(111)
    z = data.dimensions[1].get_bin_centers()
    plt.plot(np.flip(z), np.squeeze(data.data['Sum']))
    plt.xlabel(data.dimensions[1].name +": ["+ data.dimensions[1].unit+ "]")
    plt.grid()
    plt.ylabel(data.quantity +": ["+ data.unit + "]")

    plt.fill_between(x=[0, 10], y1=0, y2=max(np.squeeze(data.data['Sum'])), facecolor='blue', alpha=0.1, label="solid water")
    plt.fill_between(x=[10.0, 10.5], y1=0, y2=max(np.squeeze(data.data['Sum'])), facecolor='black', alpha=0.3, label="pmma")
    plt.fill_between(x=[10.5, 20.5], y1=0, y2=max(np.squeeze(data.data['Sum'])), facecolor='blue', alpha=0.1)
    
    plt.legend()

    # plt.vlines(x =[11.8, 12.8], ymin = 0, ymax =max(np.squeeze(dose.data['Sum'])), color = 'red', label = 'Cellflask 3')
    plt.savefig("TOPAS/Plots/2GySOBP/" + data.quantity)
    plt.clf()
