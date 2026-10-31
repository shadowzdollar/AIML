import numpy as np

arr = np.arange(15).reshape((3, 5))

print(arr)

#while i transpose the array sthe columns beocmes tows and vice versa
#and capital T is used for this transposing

print(arr.T)

#matrix product using numpy.dot

print(np.dot(arr.T, arr))

#using also @ operator to perform matrix product

print(arr.T @ arr)



