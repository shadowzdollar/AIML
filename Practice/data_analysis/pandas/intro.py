import pandas as pd
import numpy as np

from pandas import Series, DataFrame

obj = pd.Series([4, 7, -5, 3])

print(obj)

print(obj.array)

#default index manipulation wind "index" specificatin

obj2 = pd.Series([4, 7, -5, 3], index=["d", "b", "a", "c"])

print(obj2)

print(obj2["a"])

#applying the mathematical boolean values on display

print(obj2[obj2 > 2])
#multiplication

print(obj2 * 2)

#for exponential numpy multiplicaiton

print(np.exp(obj2))

#boolean purpose checking

print("b" in obj2)

#passing the dictonary from the serie object

sdata = {"Ohio": 35000, "Texas": 71000, "Oregon": 16000, "Utah": 5000}

obj3 = pd.Series(sdata)

print(obj3)

#convering the serie back to the dictionay using ".to_dist(): function" key word

# obj3.to_dist()



states = ["California", "Ohio", "Oregon", "Texas"]

obj4 = pd.Series(sdata, index=states)

print(obj4)

#checking the missing values

print(pd.isna(obj4))
print(pd.notna(obj4))

#mathematical operations on the objects

print(obj3 + obj4)

#naming the pandas objects and the index

obj4.name = "Population"
obj4.index.name = "States"

print(obj4)



#Data franes(2d data storage)

#using the dictionary to create the dataframe table

data = {"state": ["Ohio", "Ohio", "Ohio", "Nevada", "Nevada", "Nevada"],
"year": [2000, 2001, 2002, 2001, 2002, 2003],
"pop": [1.5, 1.7, 3.6, 2.4, 2.9, 3.2]}

frame = pd.DataFrame(data)

print(frame)

#selecting only the first five or the last five lines 

print(frame.head())

print(frame.tail())

#using the column specification

pd.DataFrame(data, columns=["year", "state", "pop"])


print(frame.columns)

#selecting the specified column

print(frame["state"])
# or

print(frame.year)

#assignment by column

frame["debt"] = 16.5


#through arranging

frame["debt"] = np.arange(6.)





