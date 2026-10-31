import numpy as np
from numpy import random as rng

arr = np.arange(10)

#unary ufuncs

#performing squareroot using sqrt

print(np.sqrt(arr))

#exponent

print(np.exp(arr))

#binary ufungs


#generating random number's arrays

x = np.random.standard_normal(8)
y = np.random.standard_normal(8)

#for maximum numbers

print(np.maximum)

#perfoming summation of arrays

print(np.sum(x, y))

#using modify to integrate with both rmainder and the whole part


arr = rng.standard_normal(7) * 5

print(arr)


remainder, whole_part = np.modify(arr)


print(remainder)
print(whole_part)
