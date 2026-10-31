#rrandom walks

import random
import numpy as np
import matplotlib.pyplot as plt

position = 0

walk = [position]

nsteps = 1000

for _ in range(nsteps):
    step = 1 if random.randint(0, 1) else step = -1
    position += step
    walk.append(position)


plt.plot(walk)

#Mathematical operation on random walks as sttistics

nsteps = 1000 #: Walk will have 1000 steps
rng = np.random.default_rng(seed=12345) #: Creates reproducible random number generator
draws = rng.integers(0, 2, size=nsteps) #: Generates 1000 random 0s or 1s
steps = np.where(draws == 0, 1, -1) #: Converts 0→1, 1→-1 (so each step is ±1)
walk = steps.cumsum() #: Calculates cumulative sum to create the random walk path


#calculating the minimum and the maximum point aling the trajectory

walk.min()
walk.max()

