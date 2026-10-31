import numpy as np


#using meshgrid to create the sample random points in space

points = np.arange(-5, 5, 0.01)

xs, ys = np.meshgrid(points, points)

print(ys)

#performing operation on them

z = np.sqrt(xs ** 2 + ys ** 2)

print(z)

#using matplotlib for ploting


# import matplotlib.pyplot as plt

# plt.title("Random points image in space")
# plt.plot(xs, ys)

#Expressing Conditional Logic as Array Operations

xarr = np.array([1.1, 1.2, 1.3, 1.4, 1.5])

yarr = np.array([2.1, 2.2, 2.3, 2.4, 2.5])

cond = np.array([True, False, True, True, False])

result = np.where(cond, xarr, yarr)

print(result)
