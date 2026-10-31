import numpy as np

names = np.array(["Bob", "Joe", "Will", "Bob", "Will", "Joe", "Joe"])

data = np.array([[4, 7], [0, 2], [-5, 6], [0, 0], [1, 2],[-12, -4], [3, 4]])

print(names == "Bob")

print(data[names == "Bob"])

#indexing also the columns

print(data[names == "Bob", 1])

#boolean for everthing else except bob

print(names != "Bob")

#negetion for inverting some booleans
 
cond = names == "Bob"

print(data[~cond])

#combining two or more 

mask = (names == "Bob") | (names == "Will")

print(mask)

