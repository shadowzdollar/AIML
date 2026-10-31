import numpy as np
import matplotlib.pyplot as plt


plt.style.use("dark_background")

x = np.arange(1000)

y1 = np.cumsum(np.random.randn(1000))
y2 = np.cumsum(np.random.randn(1000))
y3 = np.cumsum(np.random.randn(1000))




plt.plot(x, y1, label="one", linestyle="-")
plt.plot(x, y2, label="two", linestyle="--")
plt.plot(x, y3, label="three", linestyle=":")

plt.legend()

plt.show()




