import matplotlib.pyplot as plt
import numpy as np

data = np.random.normal(100, 15, 1000)
plt.hist(data, bins=30)
plt.title('Histogram')
plt.show()
