import numpy as np

#self datatype assignment

arr1 = np.array([1, 2, 3, 4], dtype=np.float64)
arr2 = np.array([1, 2, 3, 4], dtype=np.int32)

print(arr1.dtype)
print(arr2.dtype)

#converting or casting an array from one data type to another using ndarray’s astype method:

arr = np.array([1, 2, 3, 4, 5])

print(arr.dtype)

float_arr = arr.astype(np.float64)

print(float_arr)
print(float_arr.dtype)

#converting back to the interger type the decimal part will be truncated

float_array = np.array([1.2, 20.3, 22.9, 49.78, 0.20, -4.75])

int_type = float_array.astype(np.int64)

print(int_type.dtype)

#generating random numbers

random_numbers = [np.random.standard_normal() for i in range(15)]
print(random_numbers)

#converting strings to real numbers


numeric_strings = np.array(["1.25", "-9.6", "42"], dtype=np.string)

numeric_strings.astype(float)

print(numeric_strings.dtype)