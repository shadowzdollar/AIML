import numpy as np 

data1 = [6, 7.5, 8, 0, 1]

arr1 = np.array(data1)

print(arr1)

#Nested sequences, like a list of equal-length lists, will be converted into a multidimen‐sional array:

data2 = [[1, 2, 3, 4], [5, 6, 7, 8]]

arr2 = np.array(data2)

print(arr2)
#confirming the size of the array and number of dimenstions it contains
print(arr2.ndim)
print(arr2.shape)

#data type checking

print(arr1.dtype)
print(f'{arr2.dtype}')

#creating arrays of the same numbers:
#using array.zeros and array.ones

print(np.zeros(10))
print(np.ones(10))

#for the multidimensional array

print(np.zeros((10, 3)))

#using np.arange for the ranged data

values = np.arange(15)
for i in values:
    print(f'{i}, ')

    