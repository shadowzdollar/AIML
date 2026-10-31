import numpy as np
import matplotlib.pyplot as plt

fig, axis = plt.subplots(2, 2, sharex=True, sharey=True)

for i in range(2):
    for j in range(2):
        axis[i, j].hist(np.random.standard_normal(700), bins=50, color='orange', alpha=0.5)
fig.subplots_adjust(wspace=0, hspace=0)

plt.show()