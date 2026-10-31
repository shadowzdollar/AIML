import pandas as pd
import numpy as np

obj = pd.Series(np.arange(3), index=["a", "b", "c"])

index = obj.index

print(index)

#index objects are immutable 

# index[1] = "f" #causes the error

#index sharing beteen objects

labels = pd.Index(np.arange(3))

print(labels)

obj2 = pd.Series([1.5, -2.5, 0], index=labels)

print(obj2)


