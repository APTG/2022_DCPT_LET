import matplotlib.pyplot as plt
import numpy as np
from topas2numpy import BinnedResult

ntracks = BinnedResult('/home/villads/2022_DCPT_LET/data/topas/results/output/plan_2/Scoring_protonD_XYBox.csv')

print('{0} [{1}]'.format(ntracks.quantity, ntracks.unit))
print('Statistics: {0}'.format(ntracks.statistics))
x = []
for dim in ntracks.dimensions:
    print('{0} [{1}]: {2} bins'.format(dim.name, dim.unit, dim.n_bins))
    x.append(dim.name)
    x.append(dim.n_bins)
    x.append(dim.unit)
    


plt.imshow(np.squeeze(ntracks.data['Sum']), extent=[-5,5,-5,5])
plt.colorbar()
plt.xlabel('cm')
plt.ylabel('cm')


# plt.xticks([])  # Disable xticks
plt.show()
