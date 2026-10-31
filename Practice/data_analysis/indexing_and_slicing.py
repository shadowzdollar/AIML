import numpy as np

arr = np.arange(10)

print(arr)


#slicing: the act of cutting out the array into sub array

print(arr[5:8])

#assigning  the sacalar values to the sliced array

arr[5:8] = 12

print(arr)

#updating the sub array(slice) also updates the original array

slice_arr = arr[5:8]

slice_arr[:]=64

print(arr)

#numpy arrays never make copies but changes updates the original array

#2d arrays
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

print(arr2d[0][1])

#for the 3d array

arr3d = np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])
print(arr3d)

#udating the values at certain index

arr3d[0] = 43

print(arr3d)

#slicing 2d arra
slice_2d_array = arr2d[:2]

print(slice_2d_array)

#multiple slicing

print(arr2d[:2, 1:])