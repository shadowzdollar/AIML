import numpy as np
x = 60.5
y = 40.6
z = 30

theta = np.tan(y / x)
rho = np.sqrt(x**2 + y**2)

print(f'Rho: {rho:.2f}')
print(f'Theta: {theta:.2f}')
print(f'Z: {z:.2f}')
