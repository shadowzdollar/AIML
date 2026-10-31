import matplotlib.pyplot as plt

import numpy as np

fig, ax = plt.subplots()

x = np.linspace(0, 10, 100)

ax.plot(x, np.sin(x), label='Sine Wave', color='blue')
ax.plot(x, np.cos(x), label='Cosine Wave', color='red', linestyle='--')

#labels and title

ax.set_xlabel('Angle (radians)')
ax.set_ylabel('Amplitude')
ax.set_title('Sine and Cosine Waves')


#Ticks (custom locations)


