import numpy as np
import pandas as pd


import matplotlib.pyplot as plt


fig = plt.figure()

ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)

ax1.plot(np.random.rand(10))
ax3.hist(np.random.rand(100))
ax4.pie([10, 30, 50], labels=['A', 'B', 'C'])


#generating rand int for the scatter for x and y

x = np.random.rand(100)
y = np.random.rand(100)
ax2.scatter(x, y, color='red', marker='o')



plt.show()
