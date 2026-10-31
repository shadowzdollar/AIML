import pandas as pd
import numpy as np


#selection on dataframe with loc and iloc 

data = pd.DataFrame(np.arange(16).reshape((4, 4)), index=["Ohio", "Colorado", "Utah", "New York"], columns=["one", "two", "three", "four"])

print(data)


#selection on data frame using loc and iloc


print(data.loc["Colorado"])
print(data.loc[["Colorado", "New York"]])

print(data.iloc[2])

#loc is for key or label based selection while the iloc is for the integer based selection and indexing



