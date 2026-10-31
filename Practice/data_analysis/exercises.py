import random 
import matplotlib.pyplot as plt
import numpy as np

position = 0
walk = [position]

nsteps = 1000

for _ in range(nsteps):
    step = 1 if random.randint(0, 1) else step = -1
    position +=step
    walk.append(position)


plt.plot(walk[:100])
plt.show()

