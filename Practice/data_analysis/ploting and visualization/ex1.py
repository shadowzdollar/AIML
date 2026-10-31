import numpy as np
import matplotlib.pyplot as plt

ax.plot(x, y, linestyle="--", color="green")

ax = fig.add_subplot()

ax.plot(np.random.standard_normal(30).cumsum(), color="black", linestyle="dashed", marker="o");

plt.show()
