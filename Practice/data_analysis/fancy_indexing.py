import numpy as np

arr = np.zeros((8, 4))

for i in range(8):
    arr[i] = i

print(arr)

#selecing all rows that contain a given integer

print(arr[[4, 3, 0, 6]])


#using negative selects the wraws at the end

# print(arr[-3, -5, -7])

arr = np.arange(32).reshape((8, 4))

print(arr)