import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()

ax = fig.add_subplot()

data = np.random.standard_normal(30).cumsum()


ax.plot(data, color="black", linestyle="dashed", label="Default")
ax.plot(data, color="black", linestyle="dashed", drawstyle="steps-post", label="steps-post")


plt.legend()


plt.show()
