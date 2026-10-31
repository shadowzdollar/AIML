import pandas as pd
import numpy as np

obj = pd.Series(np.arange(5.), index=["a", "b", "c", "d", "e"])

#dropping an object

new_obj = obj.drop("c")

print(new_obj)


data = pd.DataFrame(np.arange(16).reshape((4, 4)),

index=["Ohio", "Colorado", "Utah", "New York"],

columns=["one", "two", "three", "four"])


print(data)

data.drop(index=["Colorado", "Ohio"])

