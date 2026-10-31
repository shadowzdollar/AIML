import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()

# Define ax first before plotting
ax = fig.add_subplot()

# Plot the data
ax.plot(
    np.random.standard_normal(30).cumsum(),
    color="black",
    linestyle="dashed",
    marker="o"
)

plt.show()

