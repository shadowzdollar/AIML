import numpy as np
import pandas as pd

df = pd.DataFrame(np.random.standard_normal((7, 3)))

print(df)

#adding na

df.iloc[:4, 1] = np.nan
df.iloc[:2, 2] = np.nan
print(df)



#removint the na

df.dropna()

print(df.dropna())

#how and limittation

print(df.dropna(thresh=2))


#filling in the missing data

print(df.fillna(0))




