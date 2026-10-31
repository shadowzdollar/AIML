import pandas as pd
import numpy as np

float_data = pd.Series([1.2, -3.5, np.nan, 0])

print(float_data)


print(float_data.isna())

#filtering out the missing data

data  = pd.Series([1, np.nan, 3.5, np.nan, 7])


print(data.dropna())


#or you can use the  notna 

print( data.notna())
