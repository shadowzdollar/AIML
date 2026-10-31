import numpy as np
import pandas as pd

df = pd.DataFrame([[1.4, np.nan], [7.1, -4.5],

[np.nan, np.nan], [0.75, -1.3]],

index=["a", "b", "c", "d"],
columns=["one", "two"])



print(df)


#calling the function of summation

print(df.sum())

#summation bu columns 

print(df.sum(axis="columns"))

#suppose tha we want to skip the na values

print(df.sum(axis="columns", skipna=False))



df.mean(axis="columns")


df.idxmax()

df.cumsum()


       