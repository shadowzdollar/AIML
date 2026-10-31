import numpy as np
import pandas as pd

data = pd.DataFrame(np.random.standard_normal((1000, 4)))

print(data.describe())

#finding all the values in one of the columns exceeding 3 in absolute value

col = data[2]

print(col[col.abs() > 3])

print(data[(data.abs() > 3).any(axis="columns")])

#printing all the numbes with teh sign

print(np.sign(data).head())